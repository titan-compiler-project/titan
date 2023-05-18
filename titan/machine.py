from __future__ import annotations

import graphviz

import type
import dataflow as d
from errors import TitanErrors
from symbols import Operation, Operation_Type
from enum import Enum, auto
from typing import NamedTuple, TypedDict, Union, List

class Machine:

    def __init__(self):
        self.options = []   # parsed options (anything but output stuff)
        self.output_options = []    # parsed outputting options
        self.processed_text = []    # preprocessed python
        self.files = []     # file names
        self.parsed_modules = []
        self.functions = []
        self.name_of_top_module = None
        self.SPIRV_asm_obj: SPIRV_ASM = None

class Function:
    # name = ""
    # params = []
    # body = []
    # returns = []

    def __init__(self, name, params, body, returns, return_type):
        self.name = name
        self.params = params
        self.body = body
        self.returns = returns
        self.return_type = return_type

    def __str__(self):
        return f"{self.name}, {self.params}, {self.body}, {self.returns} with type {self.return_type}"
    
#######################################################################

class SPIRV_ASM:

    class Sections(Enum):
        CAPABILITY_AND_EXTENSION = auto()
        ENTRY_AND_EXEC_MODES = auto()
        DEBUG_STATEMENTS = auto()
        ANNOTATIONS = auto()
        TYPES_CONSTS_VARS = auto()
        FUNCTIONS = auto()

    class TypeContext(NamedTuple):
        primative_type: type.DataType = None
        storage_type: type.StorageType = None
        is_constant: bool = False
        is_pointer: bool = False

    class ConstContext(NamedTuple):
        primative_type: Union[int, float] = None
        value: Union[int, float] = None

    def __init__(self):
        self.generated_spirv = {
            self.Sections.CAPABILITY_AND_EXTENSION.name: [],
            self.Sections.ENTRY_AND_EXEC_MODES.name: [],
            self.Sections.DEBUG_STATEMENTS.name: [],
            self.Sections.ANNOTATIONS.name: [],
            self.Sections.TYPES_CONSTS_VARS.name: [],
            self.Sections.FUNCTIONS.name: []
        }

        # scuffed type hinting
        # but using typing.Dict or dict or Dict just throws numerous errors
        # https://stackoverflow.com/questions/51031757/how-to-type-hint-a-dictionary-with-values-of-different-types
        class declared_type_dict_hint(TypedDict):
            type_context: self.TypeContext
            id: str

        class declared_func_type_dict_hint(TypedDict):
            type: type.DataType
            id: str

        class declared_consts_dict_hint(TypedDict):
            type: self.ConstContext
            id: str

        class generated_line_dict_hint(TypedDict):
            id: str
            type: type.DataType

        self.declared_types: declared_type_dict_hint = {}
        self.declared_function_types: declared_func_type_dict_hint = {}
        self.declared_consts: declared_consts_dict_hint = {}

        # lines that were generated as a result of parsing arithmetic, they'll have something like "%titan_id_0" as their id
        self.generated_lines: generated_line_dict_hint = {}

        self.location = 0
        self.id = 0


    def append_code(self, section: Sections, code):
        self.generated_spirv[section.name].append(code)

    def print_contents(self):
        print("-"*10)
        for section, code in self.generated_spirv.items():
            print(f"{section}")
            for entry in code:
                print(f"\t{entry}")
        print("-"*10)

    def create_file_as_string(self):

        fake_file = ""

        for k, v in self.generated_spirv.items():
            for line in v:
                fake_file += f"{line}\n"

        return fake_file


    def output_to_file(self, name):

        with open(f"{name}.spvasm", "w") as f:
            for k, v in self.generated_spirv.items():
                print(f"writing {k}")
                
                for line in v:
                    f.write(line)
                    f.write(f"\n")


    # ==== type helper functions ====
    def type_exists(self, type: TypeContext):
        # can this be simplified to "return type in self.declared_types" ?
        return True if type in self.declared_types else False
    
    def add_type(self, type: TypeContext, id: str):
        self.declared_types[type] = id

    def get_type_id(self, type: TypeContext):
        return self.declared_types[type]


    # ==== function helper functions ====
    def func_type_exists(self, type: type.DataType):
        return True if type in self.declared_function_types else False

    def add_func_type(self, type: type.DataType, id: str):
        self.declared_function_types[type] = id

    def get_func_id(self, type: type.DataType):
        return self.declared_function_types[type]


    # === consts helper functions ===
    def const_exists(self, const: ConstContext):
        return True if const in self.declared_consts else False
    
    def add_const(self, c_ctx: ConstContext, id: str):
        self.declared_consts[c_ctx] = id

    def get_const_id(self, c_ctx: ConstContext):
        return self.declared_consts[c_ctx]


    # === generated line helper functions ===
    def line_exists(self, id: str):
        return True if id in self.generated_lines else False
    
    def get_line_type(self, id: str):
        return self.generated_lines[id]
    
    def add_line(self, id: str, type: type.DataType):
        self.generated_lines[id] = type


###############################################################

class _VerilogTypeContext(NamedTuple):
    type: type.DataType = None
    data: list = []
    is_pointer: bool = False
    alias: str = "" # alias is used to store the original type id when is_pointer is set to True

class _spirv_id_with_type_context_dict_hint(TypedDict):
    id: str
    type_context: _VerilogTypeContext

class _id_and_node_dict_hint(TypedDict):
    id: str
    node: List[d.Node]

class _VerilogFunctionData(NamedTuple):
    # name: str = "",
    # types: List[_VerilogTypeContext] = []
    types: _spirv_id_with_type_context_dict_hint = {}
    inputs: List[str] = []
    outputs: List[str] = []
    # body_nodes: List[d.Node] = []
    body_nodes: _id_and_node_dict_hint = {}

class Verilog_ASM():

    class Sections(Enum):
        MODULE_NAME = auto()
        PARAMETER_LIST = auto()
        PORTS_LIST = auto()
        BODY = auto()
        END = auto()


    def __init__(self):

        class function_name_and_data_dict_hint(TypedDict):
            name: str
            data: _VerilogFunctionData
        
        self.content: function_name_and_data_dict_hint = {}
        self.declared_symbols = []
        self.marked_symbols_for_deletion = []


    ## helper functions
    def _overwrite_body_nodes(self, fn_name, nodes):
        new_vfd = _VerilogFunctionData(
            self.content[fn_name].types,
            self.content[fn_name].inputs,
            self.content[fn_name].outputs,
            nodes
        )

        self.content[fn_name] = new_vfd


    def create_function(self, function_name):
        self.content[function_name] = _VerilogFunctionData()

    def add_body_node_to_function(self, fn_name: str, node: d.Node):
        # self.content[name].body_nodes[node.spirv_id] = node
        # self.content[name].body_nodes[node.spirv_id].append(node)

        if not self.does_node_exist(fn_name, node.spirv_id):
            self.content[fn_name].body_nodes[node.spirv_id] = []

        print(f"-[Verilog_ASM.add_body_node_to_function] adding {node} with id {node.spirv_id} to function {fn_name}")
        self.content[fn_name].body_nodes[node.spirv_id].append(node)

    def add_type_context_to_function(self, fn_name: str, type_id: str, type_context: _VerilogTypeContext):
        # self.content[function_name].types.append(type_context)
        self.content[fn_name].types[type_id] = type_context

    def get_type_context_from_function(self, fn_name:str, type_id: str):
        return self.content[fn_name].types[type_id]

    def type_exists_in_func(self, fn_name: str, type_id: str):
        # return True if type_id in 
        return True if type_id in self.content[fn_name].types else False

    def add_output_to_function(self, fn_name:str, symbol:str):
        self.content[fn_name].outputs.append(symbol)

    def add_input_to_function(self, fn_name:str, symbol:str):
        self.content[fn_name].inputs.append(symbol)

    def get_datatype_from_id(self, fn_name:str, id:str):
        return self.content[fn_name].types[id].type

    def get_primative_type_id_from_id(self, fn_name:str, id:str):
        x = self.content[fn_name].types[id]
        if x.is_pointer:
            return x.alias
        else:
            return id

    def does_node_exist(self, fn_name:str, node_id:str):
        return True if node_id in self.content[fn_name].body_nodes else False

    def does_node_exist_in_dict(self, node_dict, node_id):
        return True if node_id in node_dict else False

    def get_node(self, fn_name:str, node_id: str):
        return self.content[fn_name].body_nodes[node_id][-1]
    
    def modify_node(self, fn_name:str, target_node_id:str, pos:int,  value_node: d.Node, operation: Operation = Operation.NOP):
        # self.content[name].body_nodes[target_node_id].update_input(pos, value_node)
        x = self.get_node(fn_name, target_node_id)
        # print(x)
        # print(x.spirv_id)

        # new_ctx = d.NodeContext(
            # x.spirv_line_no, x.spirv_id, x.type_id, x.input_left, x.input_right, x.operation, x.data
        # )

        # dirty, maybe need to use a dataclass instead
        if pos == 0:
            # new_ctx.input_left = value_node
            new_ctx = d.NodeContext(
               x.spirv_line_no, x.spirv_id, x.type_id, value_node, x.input_right, operation, x.data
        )
        elif pos == 1:
            # new_ctx.input_right = value_node
            new_ctx = d.NodeContext(
               x.spirv_line_no, x.spirv_id, x.type_id, x.input_left, value_node, operation, x.data
        )

        self.content[fn_name].body_nodes[target_node_id].append(d.Node(new_ctx))


    def _sort_body_nodes_by_tick(self, fn_name: str):
        tick_dict = {}

        # TODO: can we just use list comprehension on this?
        for symbols in self.content[fn_name].body_nodes:
            for node in self.content[fn_name].body_nodes[symbols]:

                if node.tick not in tick_dict.keys():
                    tick_dict[node.tick] = []

                tick_dict[node.tick].append(node)

        return tick_dict

    @staticmethod
    def _parent_exists(node: d.Node):
        return True if node.input_left is not None or node.input_right is not None else False

    @staticmethod
    def _encode_parents(node: d.Node):
        count = 0

        if node.input_left is not None:
            count += 1
        if node.input_right is not None:
            count += 2

        # if left exists, return 1
        # if right exists, return 2
        # if both exist, return 3
        # if none exist, return 0
        return count
    

    def generate_dot_graph(self, file_name_suffix: str = "", clean_nodes = None):
        # print("===graph gen===") # debug


        for key in self.content.keys():
            dot = graphviz.Digraph(comment=f"digraph for {key}", filename=f"digraph_{key}{file_name_suffix}.dot", directory="dots") 
            dot.attr(bgcolor="gray10")
            dot.attr(color="white")
            dot.attr(fontcolor="white")

            if clean_nodes is None:
                x = self._sort_body_nodes_by_tick(key)
            else:
                x = clean_nodes

            for k in range(0, len(x.keys())):
            # for k in x.keys():
                # print(f"tick: {k}")

                with dot.subgraph(name=f"cluster_tick_{k}") as ds:
                    ds.attr(style="dashed")
                    ds.attr(label=f"tick {k}")
                    
                    try:
                        for v in x[k]:
                            # print(f"\t{v}, parents? {self._parent_exists(v)}, pos: {self._encode_parents(v)}")
                            current_node_label = f"{v.spirv_id}_{k}"
                            ds.node(current_node_label, f"{v.spirv_id} at tick {k} \n({v.operation})", color="white", fontcolor="white")

                            if self._parent_exists(v):
                                # check which parents exist
                                parent_num = self._encode_parents(v)
                                match parent_num:
                                    case 1:
                                        # ds.edge()
                                        # get parent name/spirv id
                                        # print(f"\t\tL: {v.input_left.spirv_id} at tick {v.input_left.tick}")
                                        parent_id_label = f"{v.input_left.spirv_id}_{v.input_left.tick}"
                                        ds.edge(parent_id_label, current_node_label, color="white")

                                    case 2:
                                        # print(f"\t\tR: {v.input_right.spirv_id} at tick {v.input_right.tick}")
                                        parent_id_label = f"{v.input_right.spirv_id}_{v.input_right.tick}"
                                        ds.edge(parent_id_label, current_node_label, color="white")
                                    case 3:
                                        # print(f"\t\tL: {v.input_left.spirv_id} at tick {v.input_left.tick}")
                                        # print(f"\t\tR: {v.input_right.spirv_id} at tick {v.input_right.tick}")

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

            # print(dot.source)
            dot.render(view=False, overwrite_source=True)


    def __find_best_parents(self, subject_node: d.Node):

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

            if subject_node.input_left.operation in Operation_Type.GENERIC_CONSTANT_DECLARATION:
                return subject_node.input_left
            
            if subject_node.input_left.operation in Operation_Type.ARITHMETIC:
                return subject_node.input_left
            
            if subject_node.input_left.operation in Operation_Type.COMPARISON:
                return subject_node.input_left
        
        # a non existant id means that it was created for either loading or arithmetic
        if subject_node.spirv_id not in self.declared_symbols:

            # if a temp id was only created for loading an existing value
            if subject_node.operation is Operation.LOAD:

                # if subject_node.spirv_id not in self.marked_symbols_for_deletion:
                    # self.marked_symbols_for_deletion.append(subject_node.spirv_id)
                    # print(f"mark node for deletion {subject_node.spirv_id}")

                return self.__find_best_parents(subject_node.input_left)
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
                    return (subject_node.input_left, self.__find_best_parents(subject_node.input_right))
                elif tandem_arith_right:
                    return (self.__find_best_parents(subject_node.input_left), subject_node.input_right)
                else:
                    return (self.__find_best_parents(subject_node.input_left), self.__find_best_parents(subject_node.input_right))
                
            # if its an actual comparison (and not a decision node), find the best parent nodes
            elif subject_node.operation in Operation_Type.COMPARISON and subject_node.operation is not Operation.DECISION:
                return (self.__find_best_parents(subject_node.input_left), self.__find_best_parents(subject_node.input_right))
            
            # if its a decision node, the best node will be the comparison node that just came before it, so return it
            elif subject_node.operation is Operation.DECISION:
                return subject_node.data[0] 


    def _eval_parents_for_non_temp_id(self, current_node: d.Node):
        # a temp id is defined as a LOAD instruction which references an existing symbol
        # in spirv, this looks something like:
        #   %1 = OpLoad %type_int %a
        # where %1 is a temporary id containing the value of %a
        
        best = self.__find_best_parents(current_node)
        node_names = []

        print(f"BEST EVAL---- {best}")

        # print(f"best parents for node {current_node} is:")

        try:
            # print(f"L: {best[0]} ({best[0].spirv_id})\nR: {best[1]} ({best[1].spirv_id})")
            # new_ctx = d.NodeContext(
            #     current_node.spirv_line_no, current_node.spirv_id,
            #     current_node.type_id, 
            #     best[0], best[1],
            #     current_node.operation, current_node.data
            # )
            node_names = [best[0].spirv_id, best[1].spirv_id]
        except:
            # print(f"O:{best} ({best.spirv_id})")
            # new_ctx = d.NodeContext(
            #     current_node.spirv_line_no, current_node.spirv_id,
            #     current_node.type_id, 
            #     best, current_node.input_right,
            #     current_node.operation, current_node.data
            # )
            node_names = [best.spirv_id]

        # return new_ctx
        return node_names

    def clean_graph(self):
        # for function in self.content.keys():
        #     for symbol in self.content[function].body_nodes.keys():
        #         for node in self.content[function].body_nodes[symbol]:

        #             is_node_a_declaration = node.operation in Operation_Type.GENERIC_CONSTANT_DECLARATION or node.operation in Operation_Type.GENERIC_VARIABLE_DECLARATION

        #             if not is_node_a_declaration:
        #                 print(f"{node.spirv_id} {node.operation} -- {is_node_a_declaration}")
        #                 self._eval_parents_for_non_temp_id(node)


        def _fetch_last_node(node_dict, node_name: str):
            if node_name in node_dict:
                return node_dict[node_name][-1]
            else:
                # return None
                raise Exception(TitanErrors.UNEXPECTED.value, TitanErrors.UNEXPECTED.name)

        def _update_node_dict(node_dict, node_name: str, node_ctx: d.NodeContext):
            if node_name in node_dict:
                node_dict[node_name].append(d.Node(node_ctx))
            else:
                node_dict[node_name] = [d.Node(node_ctx)]



        for function in self.content.keys():
            clean_nodes: _id_and_node_dict_hint = {}
            # print(self.content[functions].body_nodes)
            tick_ordered_nodes = self._sort_body_nodes_by_tick(function)

            # print(f"-[Verilog_ASM.clean_graph] tick_ordered_nodes: {tick_ordered_nodes}")

            # shift all declarations into the new dict (tick=0, consts + vars)
            # print('='*10)
            for node in tick_ordered_nodes[0]:
                # print(f"-[Verilog_ASM.clean_graph] node: {node}", end="")
                if node.spirv_id not in clean_nodes:
                    # print(f"...was not in clean nodes as was added into {node.spirv_id}")
                    clean_nodes[node.spirv_id] = [node]
                else:
                    # print(f"...was appended to {node.spirv_id}")
                    clean_nodes[node.spirv_id].append(node)
            # print('='*10)

            # print(f"-[Verilog_ASM.clean_graph] clean_nodes: {clean_nodes}")

            print()
            for tick in range(1, len(tick_ordered_nodes.keys())):
                print(f"-[Verilog_ASM.clean_graph] tick: {tick}")
                for node in tick_ordered_nodes[tick]:
                    print(f"\tnode: {node}", end="")

                    if node.spirv_id not in self.declared_symbols and node.operation is Operation.LOAD:
                        print(f"....ignored ({node.spirv_id})")
                        continue

                    print()

                    # print("="*10)
                    # print(len(clean_nodes))
                    # print("="*10)

                    # ctx = self._eval_parents_for_non_temp_id(node)
                    # print(f"node: {node} evalutes to context: \n\t{ctx}")
                    # new_node = d.Node(ctx)
                    # print(f"new node is: {new_node}\n\n")
                    
                    # if new_node.spirv_id not in clean_nodes:
                    #     clean_nodes[new_node.spirv_id] = [new_node]
                    # else:
                    #     clean_nodes[new_node.spirv_id].append(new_node)



                    # if _eval_parents_for_non_temp_id(node) returns a spirv id
                    # we should just try and reference the latest one in the clean
                    # nodes dict
                    print(f"-->[Verilog_ASM.clean_graph] current node: {node}")
                    best_node_names = self._eval_parents_for_non_temp_id(node)
                    print(f"-->[Verilog_ASM.clean_graph] returned with {best_node_names}")

                    if len(best_node_names) == 1:
                        print(f"returned with one node: {best_node_names[0]}")
                        # n = _fetch_last_node(clean_nodes, best_node_names[0])
                        # print(f"\n{n}")

                        # new_ctx = d.NodeContext(
                        #     node.spirv_line_no, node.spirv_id, node.type_id,
                        #     n, None, node.operation, node.data
                        # )

                        # _update_node_dict(clean_nodes, node.spirv_id, new_ctx)

                        # print(self.does_node_exist_in_dict(clean_nodes, node.spirv_id))

                        if self.does_node_exist_in_dict(clean_nodes, node.spirv_id):
                            n = _fetch_last_node(clean_nodes, best_node_names[0])

                            new_ctx = d.NodeContext(
                                node.spirv_line_no, node.spirv_id, node.type_id,
                                n, None, node.operation, node.data
                            )

                            _update_node_dict(clean_nodes, node.spirv_id, new_ctx)
                        else:

                            # print(f"-[Verilog_ASM.clean_graph] node {node} does not exist in clean dict")

                            if node.is_comparison:
                                n = _fetch_last_node(clean_nodes, node.data[0].spirv_id)
                                
                                new_ctx = d.NodeContext(
                                    node.spirv_line_no, node.spirv_id, node.type_id,
                                    node.input_left, node.input_right,
                                    node.operation, [n], node.is_comparison
                                )
                            else:
                                new_ctx = d.NodeContext(
                                    node.spirv_line_no, node.spirv_id, node.type_id,
                                    node.input_left, node.input_right, 
                                    node.operation, node.data, node.is_comparison
                                )

                            _update_node_dict(clean_nodes, node.spirv_id, new_ctx)



                    elif len(best_node_names) == 2:
                        print(f"returned with two nodes: {best_node_names}")
                        n1 = _fetch_last_node(clean_nodes, best_node_names[0])
                        n2 = _fetch_last_node(clean_nodes, best_node_names[1])

                        print(f"\t{n1}\n\t{n2}")

                        new_ctx = d.NodeContext(
                            node.spirv_line_no, node.spirv_id, node.type_id,
                            n1, n2, node.operation, node.data
                        )

                        _update_node_dict(clean_nodes, node.spirv_id, new_ctx)
                        # if node.spirv_id in clean_nodes:
                            # clean_nodes[node.spirv_id].append(d.Node(new_ctx))
                        # else:
                            # clean_nodes[node.spirv_id] = [d.Node(new_ctx)]


            print("="*10)
            # print(clean_nodes)
            for symbol in clean_nodes:
                print(symbol)
                for node in clean_nodes[symbol]:
                    print(f"\t{node}")
                print()
            print("="*10)

            # print(type(self.content[function].body_nodes))
            # self.content[function].body_nodes = clean_nodes
            self._overwrite_body_nodes(function, clean_nodes)

        # self.generate_dot_graph("_clean_nodes")

        
class Verilog_Text():

    class Sections(Enum):
        MODULE_AND_PORTS = auto()
        INTERNAL = auto()
        ALWAYS_BLOCK = auto()
        ASSIGNMENTS = auto()

    def __init__(self):
        self.generated_verilog = {
            self.Sections.MODULE_AND_PORTS.name: [],
            self.Sections.INTERNAL.name: [],
            self.Sections.ALWAYS_BLOCK.name: [],
            self.Sections.ASSIGNMENTS.name: []
        }

    def append_code(self, section: Sections, code:str):
        self.generated_verilog[section.name].append(code)

    def print_contents(self):
        print("-"*10)
        for section, code_list in self.generated_verilog.items():
            print(f"{section}")

            for entry in code_list:
                print(f"{entry}")

        print("-"*10)

    def output_to_file(self, name):

        with open(f"{name}.sv", "w") as f:
            for k, v in self.generated_verilog.items():
                print(f"writing {k}")
                
                for line in v:
                    f.write(line)
                    f.write(f"\n")
