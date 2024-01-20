from __future__ import annotations

import graphviz, logging
from typing import NamedTuple, List, Tuple, Union
from enum import Enum, auto

# import dataflow
import compiler.hinting as hinting
from common.type import DataType
from common.symbols import Operation, Operation_Type
from common.errors import TitanErrors

class NodeContext(NamedTuple):
    """ Tuple which holds context about a node.
    
        Attributes:
            line_no (int): Line of the SPIR-V assembly this node referring to.
            id (str): Associated SPIR-V ID.
            type_id (str): Associated type ID.
            input_left (titan.Node): Left parent node.
            input_right (titan.Node): Right parent node.
            operation (titan.common.symbols.Operation): Operation being performed by the node.
            data: Additional information stored by the node.
            is_comparison (bool): Set if this node doing a comparison.
    """
    line_no: int = 0
    id: str = ""
    type_id: str = ""
    input_left: Node = None
    input_right: Node = None
    operation: Operation = None
    data: List() = []
    is_comparison: bool = False # hack because i didn't realise that OpSelect had so many parameters


class Node:
    """ Node class. 
    
        Attributes:
            spirv_line_no (int): SPIR-V assembly line number.
            spirv_id (str): Assigned SPIR-V ID.
            type_id (str): Stores the type ID of the nodes type.
            input_left (titan.compiler.node.Node): Left parent node.
            input_right (titan.compiler.node.Node): Right parent node.
            operation (titan.common.symbols.Operation): Operation that the node is performing.
            data (None): TODO
            is_comparison (bool): TODO
            tick (int): Integer representing at what stage in the pipeline this should be executed.
    """

    @staticmethod
    def _calculate_tick(left_node: Node, right_node: Node, comparison_node: Node = None) -> int:
        """ Calculate the correct tick for the node.
        
            Ticks can be set to zero if the node has no parents, or to the highest tick of the parents + 1.

            Args:
                left_node: Left node.
                right_node: Right node.
                comparison_node: Comparison node, used if currently using a decision node.

            Returns:
                Maximum calculated tick, based on the nodes provided.
        """
        
        if comparison_node is None:
            if left_node is None and right_node is None:
                return 0
            elif left_node is None:
                return right_node + 1
            elif right_node is None:
                return left_node + 1
            else:
                return max(left_node, right_node) + 1
        else:
            if left_node is None and right_node is None:
                return comparison_node + 1
            elif left_node is None:
                return max(right_node, comparison_node) + 1
            elif right_node is None:
                return max(left_node, comparison_node) + 1
            else:
                return max(left_node, right_node, comparison_node) + 1

    @staticmethod
    def _set_tick_during_init(context: NodeContext):
        """ Calculate the tick for the node during initialisation. 
        
            Args:
                context: Context about the node to create.
        """

        l_node_val = None if context.input_left == None else context.input_left.tick
        r_node_val = None if context.input_right == None else context.input_right.tick

        if context.is_comparison:
            # return Node._calculate_tick(l_node_val, r_node_val, context.data[0].tick)
            # TODO: do we have to account for the tick of the input nodes, if the selector is guaranteed to come after?
            #                                                                               is it even guaranteed to come right after? idk
            return Node._calculate_tick(0, 0, context.data[0].tick) 
        else:
            return Node._calculate_tick(l_node_val, r_node_val)


    def __init__(self, context: NodeContext):
        """ Init function for a node.
        
            Args:
                context: Context to create the node with.
        """
        self.spirv_line_no = context.line_no
        self.spirv_id = context.id
        self.type_id = context.type_id
        self.input_left = context.input_left
        self.input_right = context.input_right
        self.operation = context.operation
        self.data = context.data
        self.is_comparison = context.is_comparison
        self.tick = self._set_tick_during_init(context)


    def _update_tick(self) -> int:
        """ Helper function to update the tick when one of the parent nodes are changed.
        
            Returns:
                Recalculated tick value.
        """
        left_node_is_none = self.input_left == None
        right_node_is_none = self.input_right == None

        l_node_val = None if left_node_is_none else self.input_left.tick
        r_node_val = None if right_node_is_none else self.input_right.tick

        if self.is_comparison:
            return Node._calculate_tick(l_node_val, r_node_val, self.data[0].tick)
        else:
            return Node._calculate_tick(l_node_val, r_node_val)

        # if left_node_is_none and right_node_is_none:
        #     return 0
        # elif left_node_is_none:
        #     return self.input_right.tick + 1
        # elif right_node_is_none:
        #     return self.input_left.tick + 1
        # else:
        #     return max(self.input_left.tick, self.input_right.tick) + 1


    def update_input(self, pos: int, new_node: Node):
        """ Update a parent node.
        
            Automatically recalculates the tick for the current node.

            Args:
                pos: 0 = left node, 1 = right node
                new_node: New node to update the input with.
        """        
        if pos == 0: # left node
            self.input_left = new_node
        elif pos == 1: # right node
            self.input_right = new_node

        self.tick = self._update_tick()


    # TODO: make this look better
    def __str__(self):
        return f"({self.__class__.__name__}: [{self.spirv_line_no}:{self.spirv_id}], type_id: [{self.type_id}], left: [{None if self.input_left is None else self.input_left.spirv_id}], right: [{None if self.input_right is None else self.input_right.spirv_id}], op: {self.operation}, data: {self.data},  is_comparison: {self.is_comparison}, tick: {self.tick})"


    def __repr__(self):
        return f"({self.__class__.__name__}: [{self.spirv_line_no}:{self.spirv_id}], type_id: [{self.type_id}], left: [{None if self.input_left is None else self.input_left.spirv_id}], right: [{None if self.input_right is None else self.input_right.spirv_id}], op: {self.operation}, data: {self.data},  is_comparison: {self.is_comparison}, tick: {self.tick})"
        # return f"({self.__class__.__name__}: [{self.spirv_line_no}:{self.spirv_id}], type_id: [{self.type_id}], left: [{self.input_left}], right: [{self.input_right}], op: {self.operation}, data: {self.data},  is_comparison: {self.is_comparison}, tick: {self.tick})"


class NodeTypeContext(NamedTuple):
    """ Tuple describing type information for a node.
    
        Attributes:
            type: Primative datatype.
            data: Additional data to store in the type.
            is_pointer: Set to true if the type describes a pointer.
            alias: If ``is_pointer`` is true, this attribute will store the original type id.
    """
    type: DataType = None
    data: List() = []
    is_pointer: bool = False
    alias: str = "" # alias is used to store the original type id when is_pointer is set to True

class NodeModuleData():
    """ Class encapsulating information required for a module.
    
        Attributes:
            types: All types contained within the function.
            inputs: A list of all inputs.
            outputs: A list of all outputs.
            body_nodes: A dictionary containing all body nodes, with the SPIR-V ID as its key and a list of associated nodes as its value.
    """
    types: hinting.spirv_id_and_type_context = {}
    inputs: List[str] = []
    outputs: List[str] = []
    body_nodes: hinting.spirv_id_and_node = {}


class NodeAssembler():
    """ Node assembler. """

    content: hinting.module_name_and_data = {}
    declared_symbols = []
    

    def _overwrite_body_nodes(self, module_name: str, nodes: List[Node]):
        """ Overwrite an existing set of nodes for a given module/function.

            Args:
                module_name: The module to modify.
                nodes: Updated list of nodes.

            Note:
                The parameter "module_name" used to be called "fn_name". This was modified during a rewrite,
                and this message is a reminder of that.
        """

        # self.content[module_name].nodes = nodes
        self.content[module_name].body_nodes = nodes

    # NOTE: equiv. to create_function
    def create_module(self, module_name: str):
        """ Method to create a new, empty module class. 
        
            Args:
                module_name: Name of the module.
        """
        self.content[module_name] = NodeModuleData()

    # NOTE: equiv. to add_body_node_to_function
    def add_body_node_to_module(self, module_name: str, node: Node):
        """ Add a body node to an existing module.
        
            Checks if the node exists by using the associated SPIR-V ID, creating it if not.
            Then appends the node to that SPIR-V ID.

            Args:
                module_name: Module to ad to.
                node: Node to add.
        """
        if not self.node_exists(module_name, node.spirv_id):
            self.content[module_name].body_nodes[node.spirv_id] = []

        self.content[module_name].body_nodes[node.spirv_id].append(node)

    def add_type_context_to_module(self, module_name: str, type_id: str, type_context: NodeTypeContext):
        """ Add a type context to a function.
        
            Args:
                module_name: Module to add to.
                type_id: ID to associate with the type.
                type_context: Context about the type.
        """
        self.content[module_name].types[type_id] = type_context

    def get_type_context_from_module(self, module_name: str, type_id: str) -> NodeTypeContext:
        """ Get type context from a module using a type ID.
        
            Args:
                module_name: Module to fetch from.
                type_id: ID of type to query.

            Returns:
                Context of the type.
        """
        return self.content[module_name].types[type_id]
    
    def type_exists_in_module(self, module_name: str, type_id: str) -> bool:
        """ Check if a type exists for a given module.
        
            Args:
                module_name: Module to check in.
                type_id: Type ID to check for.

            Returns:
                True if ID exists in function, else false.
        """
        return True if type_id in self.content[module_name].types else False
    
    def add_output_to_module(self, module_name: str, symbol: str):
        """ Add an output to a module.
        
            Args:
                module_name: Module to add to.
                symbol: Symbol to add as an output.
        """
        self.content[module_name].outputs.append(symbol)

    def add_input_to_module(self, module_name: str, symbol: str):
        """ Add an input to a module.
        
            Args:
                module_name: Module to add to.
                symbol: Symbol to add as an input.
        """
        self.content[module_name].inputs.append(symbol)

    def get_datatype_from_id(self, module_name: str, id: str) -> DataType:
        """ Return primative type from ID.
        
            Args:
                module_name: Module to check in.
                id: ID to query.

            Returns:
                Primative datatype of ID, if it exists.
        """
        return self.content[module_name].types[id].type

    def get_primative_type_id_from_id(self, module_name: str, id: str) -> str:
        """ Returns the associated primative type ID given an ID of a symbol.
        
            Can handle pointers too.

            Args:
                module_name: Module to fetch from.
                id: ID to fetch from.

            Returns:
                Primative type ID.
        """
        x = self.content[module_name].types[id]
        if x.is_pointer:
            return x.alias
        else:
            return id
        
    # renamed from does_node_exist
    def node_exists(self, module_name: str, node_id: str) -> bool:
        """ Checks if a node exists in a given module.
        
            Args:
                module_name: Module to check in.
                node_id: Node ID to check for.

            Returns:
                True if node exists, else false.
        """
        return True if node_id in self.content[module_name].body_nodes else False
    
    def does_node_exist_in_dict(self, node_dict: dict[Node], node_id: str) -> bool:
        """ Checks if a node exists in the node dictionary.
        
            Args:
                node_dict: Dictionary containing Nodes.
                node_id: ID of the node to check for.

            Returns:
                True if node exists in the dictionary, else false.
        """
        return True if node_id in node_dict else False
    
    def get_node(self, module_name: str, node_id: str) -> Node:
        """ Gets the latest node given a node ID in a given function.
        
            Args:
                module_name: Module to check in.
                node_id: Node ID to check for.

            Returns:
                Latest node for the given node ID.
        """
        # TODO: why the -1?
        return self.content[module_name].body_nodes[node_id][-1]
    

    # default arg_pos is [1, 2] since its commonly used
    # however different values needed for other nodes
    def get_left_and_right_nodes(self, module_name: str, line, arg_pos: List(int) = [1, 2]) -> Tuple[Node, Node]:
        left = self.get_node(module_name, line.opcode_args[arg_pos[0]])
        right = self.get_node(module_name, line.opcode_args[arg_pos[1]])
        return (left, right)
    
    def modify_node(self, module_name: str, target_node_id: str, pos: int, value_node: Node, operation: Operation = Operation.NOP):
        """ Modify the parents and/or the operation of a node within a module.
        
            Args:
                module_name: Module to modify node in.
                target_node_id: Node to modify.
                pos: Which parent of the node to modify. (0 = left, 1 = right)
                value_node: New parent node.
                operation: Operation that the node is performing.
        """

        x = self.get_node(module_name, target_node_id)
        logging.debug(f"modifiying {target_node_id}: {x}")
        logging.debug(f"\tposition {pos} should contain {value_node.spirv_id}")
        logging.debug(f"\toperation {x.operation} should update to {operation}")

        if pos == 0:
            new_ctx = NodeContext(
                x.spirv_line_no, x.spirv_id, x.type_id, value_node, x.input_right, operation, x.data
            )

        elif pos == 1:
            new_ctx = NodeContext(
                x.spirv_line_no, x.spirv_id, x.type_id, x.input_left, value_node, operation, x.data
            )

        logging.debug(f"new node context: {new_ctx}")

        self.content[module_name].body_nodes[target_node_id].append(Node(new_ctx))

    def _sort_body_nodes_by_tick(self, module_name: str) -> dict:
        """ Sorts the nodes in ascending order (0 -> max tick).
        
            Args:
                module_name: Name of module to sort nodes of.

            Returns:
                New dictionary containing sorted nodes, with the tick as the key.
        """
        tick_dict = {}

        # logging.debug(f"nodes before {len(self.content[module_name].body_nodes)}: {self.content[module_name].body_nodes}")
        # TODO: can we just use list comprehension on this?
        for symbols in self.content[module_name].body_nodes:
            for node in self.content[module_name].body_nodes[symbols]:

                if node.tick not in tick_dict.keys():
                    tick_dict[node.tick] = []

                tick_dict[node.tick].append(node)
        # logging.debug(f"nodes after {len(tick_dict)}: {tick_dict}")
        return tick_dict
    
    @staticmethod
    def _parent_exists(node: Node) -> bool:
        """ Check whether the node has any parents.
        
            Args:
                node: Node to check parents of.
            
            Returns:
                True if any parents exist, else false.
        """
        return True if node.input_left is not None or node.input_right is not None else False
    
    @staticmethod
    def _encode_parents(node: Node) -> int:
        """ Numerically encode the position of the parents.
        
            Note:
                - 0: No parents exist.
                - 1: Left parent exists.
                - 2: Right parent exists.
                - 3: Both parents exist.

            Args:
                node: Node to encode the parents of.
        """

        count = 0

        if node.input_left is not None:
            count += 1
        
        if node.input_right is not None:
            count += 2

        return count
    
    def generate_dot_graph(self, file_name_suffix: str = "", clean_nodes = None):
        """ Generates Graphviz dot graphs of the dataflow of a function. Requires the ``graphviz`` package.
        
            Args:
                file_name_suffix: String to append to the filename.
                clean_nodes: List of clean/optimised nodes.
        """
        for module in self.content.keys():
            dot = graphviz.Digraph(comment=f"digraph for {module}", filename=f"digraph_{module}{file_name_suffix}.dot", directory="dots") 
            
            # dark mode
            dot.attr(bgcolor="gray10")
            dot.attr(color="white")
            dot.attr(fontcolor="white")

            if clean_nodes is None:
                x = self._sort_body_nodes_by_tick(module)
            else:
                x = clean_nodes

            for k in range(0, len(x.keys())):
                with dot.subgraph(name=f"cluster_tick_{k}") as ds:
                    ds.attr(style="dashed")
                    ds.attr(label=f"tick {k}")
                    
                    try:
                        for v in x[k]:
                            current_node_label = f"{v.spirv_id}_{k}"
                            ds.node(current_node_label, f"{v.spirv_id} at tick {k} \n({v.operation})", color="white", fontcolor="white")

                            if self._parent_exists(v):
                                # check which parents exist
                                parent_num = self._encode_parents(v)
                                match parent_num:
                                    case 1:
                                        # ds.edge()
                                        # get parent name/spirv id
                                        parent_id_label = f"{v.input_left.spirv_id}_{v.input_left.tick}"
                                        ds.edge(parent_id_label, current_node_label, color="white")

                                    case 2:
                                        parent_id_label = f"{v.input_right.spirv_id}_{v.input_right.tick}"
                                        ds.edge(parent_id_label, current_node_label, color="white")
                                    case 3:

                                        # TODO: need a better way to determine correct id & tick to use when dealing with decision nodes
                                        # this solution will fail if it's basically a stack of Operation.STOREs because it only goes back
                                        # two nodes.
                                        if v.is_comparison:
                                            if v.input_left.operation is Operation.STORE:
                                                parent_l_id_label = f"{v.input_left.input_left.spirv_id}_{self.get_node(module, v.input_left.input_left.spirv_id).tick}"

                                            if v.input_right.operation is Operation.STORE:
                                                parent_r_id_label = f"{v.input_right.input_right.spirv_id}_{self.get_node(module, v.input_right.input_right.spirv_id).tick}"
                                        else:
                                            parent_l_id_label = f"{v.input_left.spirv_id}_{v.input_left.tick}"
                                            parent_r_id_label = f"{v.input_right.spirv_id}_{v.input_right.tick}"

                                        ds.edge(parent_l_id_label, current_node_label, color="white" if not v.is_comparison else "green")
                                        ds.edge(parent_r_id_label, current_node_label, color="white" if not v.is_comparison else "red")

                                        if v.is_comparison:
                                            parent_compare_id_label = f"{v.data[0].spirv_id}_{v.data[0].tick}"
                                            ds.edge(parent_compare_id_label, current_node_label, color="white")

                                    case _:
                                        # should be unreachable
                                        raise Exception(f"{TitanErrors.UNEXPECTED.value} - got {parent_num} parents, but parents exist.", TitanErrors.UNEXPECTED.name)
                    except KeyError:
                        continue

            dot.render(view=False, overwrite_source=True)

    def _find_best_parents(self, subject_node: Node) -> Union(Node, Tuple(Node, Node)):
        """ Attempt to find the best parents.

            Args:
                subject_node: Node to determine best parents for.

            Returns:
                best_node: Best parent (single).
                best_nodes: Best parents (tuple).

            TODO:
                What's actually defined as being the best parent? AFAIK it was any non-temporary 
                node but will need to double check.
            
            FIXME:
                Avoid mixing different returns. This method can either return a single Node or 
                a tuple of Nodes.
        """
        # if the node is a constant declaration, return itself
        if subject_node.operation in Operation_Type.GENERIC_CONSTANT_DECLARATION:
          return subject_node

        # if node is a GLOBAL variable and is declared, return itself as being the best (this assumes that it is either an input or output of the function)
        if subject_node.operation in Operation_Type.GENERIC_VARIABLE_DECLARATION and subject_node.spirv_id in self.declared_symbols:
            return subject_node

        # if variable is just storing a constant
        if subject_node.operation is Operation.STORE and subject_node.input_left.operation in Operation_Type.GENERIC_CONSTANT_DECLARATION:
            return subject_node.input_left
        
        if subject_node.operation is Operation.STORE:
            return subject_node.input_left

        
        # a non existant id means that it was created for either loading or arithmetic
        if subject_node.spirv_id not in self.declared_symbols:

            # if a temp id was only created for loading an existing value
            if subject_node.operation is Operation.LOAD:
                return self._find_best_parents(subject_node.input_left)
            
            elif subject_node.operation in Operation_Type.ARITHMETIC:
                # tandem arithmetic means that this node references a previous node that is also an arithmetic node
                # for example:
                # %titan_id_0 = OpIAdd %int %const_3 %const_5
                # %titan_id_1 = OpIMul %int %titan_id_0 %const_2
                # 
                # we want to retain the refereced arithmetic node id (%titan_id_0) in this case, because it is the best parent for the left side
                # so tandem_arith_left will be True
                tandem_arith_left = True if subject_node.input_left.operation in Operation_Type.ARITHMETIC else False
                tandem_arith_right = True if subject_node.input_right.operation in Operation_Type.ARITHMETIC else False
                # print(f"tal: {tandem_arith_left} - tar: {tandem_arith_right}")

                if tandem_arith_left and tandem_arith_right:
                    return (subject_node.input_left, subject_node.input_right)
                elif tandem_arith_left:
                    return (subject_node.input_left, self._find_best_parents(subject_node.input_right))
                elif tandem_arith_right:
                    return (self._find_best_parents(subject_node.input_left), subject_node.input_right)
                else:
                    return (self._find_best_parents(subject_node.input_left), self._find_best_parents(subject_node.input_right))
                
            # if its an actual comparison (and not a decision node), find the best parent nodes
            elif subject_node.operation in Operation_Type.COMPARISON and subject_node.operation is not Operation.DECISION:
                return (self._find_best_parents(subject_node.input_left), self._find_best_parents(subject_node.input_right))
            
            # if its a decision node, the best node will be the comparison node that just came before it, so return it
            elif subject_node.operation is Operation.DECISION:
                return subject_node.data[0] 
            
            elif subject_node.operation in Operation_Type.BITWISE:
                return (self._find_best_parents(subject_node.input_left), self._find_best_parents(subject_node.input_right))
       
    def _evaluate_parents_for_non_temp_id(self, current_node: Node) -> list:
        """ Method to evaluate the parents of a node for non-temporary IDs.
        
            Calls ``titan.machine._find_best_parents`` internally, kinda acts like a wrapper function
            to handle the scuffed returns.

            Args:
                current_node: Node to determine best parents for.
            
            Returns:
                The ID(s) of the best parent(s). Can either be a one or two-element list.
        """
        # a temp id is defined as a LOAD instruction which references an existing symbol
        # in spirv, this looks something like:
        #   %1 = OpLoad %type_int %a
        # where %1 is a temporary id containing the value of %a
        
        best = self._find_best_parents(current_node)
        node_names = []

        try:
            node_names = [best[0].spirv_id, best[1].spirv_id]
        except:
            node_names = [best.spirv_id]

        return node_names
    
    def clean_graph(self):
        """ Method to remove temporary nodes generated by SPIR-V. 
        
            Does not return anything, overwrites the existing node list.
        """

        def _fetch_last_node(node_dict, node_name: str):
            if node_name in node_dict:
                return node_dict[node_name][-1]
            else:
                raise Exception(TitanErrors.UNEXPECTED.value, TitanErrors.UNEXPECTED.name)

        def _update_node_dict(node_dict, node_name: str, node_ctx: NodeContext):
            if node_name in node_dict:
                node_dict[node_name].append(Node(node_ctx))
            else:
                node_dict[node_name] = [Node(node_ctx)]



        for function in self.content.keys():
            clean_nodes: hinting.spirv_id_and_node = {}
            tick_ordered_nodes = self._sort_body_nodes_by_tick(function)

            for node in tick_ordered_nodes[0]:
                if node.spirv_id not in clean_nodes:
                    logging.debug(f"{node.spirv_id} did not exist in clean nodes and was added")
                    clean_nodes[node.spirv_id] = [node]
                else:
                    logging.debug(f"{node.spirv_id} was appended to clean nodes list")
                    clean_nodes[node.spirv_id].append(node)

            for tick in range(1, len(tick_ordered_nodes.keys())): #TODO: remove .keys() call
                logging.debug(f"tick: {tick}")
                _debug_str = f"node: {node}"
                for node in tick_ordered_nodes[tick]:

                    if node.spirv_id not in self.declared_symbols and node.operation is Operation.LOAD:
                        _debug_str = _debug_str + f"....ignored ({node.spirv_id})"
                        continue

                    # logging.debug(_debug_str)

                    # if _eval_parents_for_non_temp_id(node) returns a spirv id
                    # we should just try and reference the latest one in the clean
                    # nodes dict
                    logging.debug(f"current node: {node}")
                    best_node_names = self._evaluate_parents_for_non_temp_id(node)
                    logging.debug(f"returned with {best_node_names}")

                    if len(best_node_names) == 1:
                        # print(f"returned with one node: {best_node_names[0]}")
                        logging.debug(f"returned with one node: {best_node_names[0]}")

                        if self.does_node_exist_in_dict(clean_nodes, node.spirv_id):
                            n = _fetch_last_node(clean_nodes, best_node_names[0])

                            new_ctx = NodeContext(
                                node.spirv_line_no, node.spirv_id, node.type_id,
                                n, None, node.operation, node.data
                            )

                            _update_node_dict(clean_nodes, node.spirv_id, new_ctx)
                        else:

                            # print(f"-[Verilog_ASM.clean_graph] node {node} does not exist in clean dict")

                            if node.is_comparison:
                                # accessing the node data should fetch the related comparison line & its info
                                # we assume that it is in the 0th index
                                n = _fetch_last_node(clean_nodes, node.data[0].spirv_id)

                                new_ctx = NodeContext(
                                    node.spirv_line_no, node.spirv_id, node.type_id,
                                    node.input_left, node.input_right,
                                    node.operation, [n], node.is_comparison
                                )
                            else:
                                # TODO: does this every actually get hit? may be something redundant
                                new_ctx = NodeContext(
                                    node.spirv_line_no, node.spirv_id, node.type_id,
                                    node.input_left, node.input_right, 
                                    node.operation, node.data, node.is_comparison
                                )

                            _update_node_dict(clean_nodes, node.spirv_id, new_ctx)



                    elif len(best_node_names) == 2:
                        # print(f"returned with two nodes: {best_node_names}")
                        logging.debug(f"returned with two nodes: {best_node_names}")
                        n1 = _fetch_last_node(clean_nodes, best_node_names[0])
                        n2 = _fetch_last_node(clean_nodes, best_node_names[1])

                        # print(f"\t{n1}\n\t{n2}")
                        logging.debug(f"\tnode 1:{n1}")
                        logging.debug(f"\tnode 2: {n2}")

                        new_ctx = NodeContext(
                            node.spirv_line_no, node.spirv_id, node.type_id,
                            n1, n2, node.operation, node.data
                        )

                        _update_node_dict(clean_nodes, node.spirv_id, new_ctx)

            logging.debug(f"---- symbol dump ----")
            for symbol in clean_nodes:
                logging.debug(symbol)
                for node in clean_nodes[symbol]:
                    logging.debug(f"\t{node}")

            logging.debug(f"---- end symbol dump ----")

            self._overwrite_body_nodes(function, clean_nodes)