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
        self.options = []
        self.output_options = []
        self.processed_text = []
        self.files = []
        self.parsed_modules = []
        self.functions = []
        self.name_of_top_module = None
        self.SPIRV_asm_obj: SPIRV_ASM = None

class Function:
    name = ""
    params = []
    body = []
    returns = []

    def __init__(self, name, params, body, returns):
        self.name = name
        self.params = params
        self.body = body
        self.returns = returns

    def __str__(self):
        return f"{self.name}, {self.params}, {self.body}, {self.returns}"
    
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


    ## helper functions
                    


    def create_function(self, function_name):
        self.content[function_name] = _VerilogFunctionData()

    def add_body_node_to_function(self, name: str, node: d.Node):
        # self.content[name].body_nodes[node.spirv_id] = node
        # self.content[name].body_nodes[node.spirv_id].append(node)

        if not self.does_node_exist(name, node.spirv_id):
            self.content[name].body_nodes[node.spirv_id] = []

        self.content[name].body_nodes[node.spirv_id].append(node)

    def add_type_context_to_function(self, function_name: str, type_id: str, type_context: _VerilogTypeContext):
        # self.content[function_name].types.append(type_context)
        self.content[function_name].types[type_id] = type_context

    def type_exists_in_func(self, name: str, type_id: str):
        # return True if type_id in 
        return True if type_id in self.content[name].types else False

    def add_output_to_function(self, name:str, symbol:str):
        self.content[name].outputs.append(symbol)

    def get_datatype_from_id(self, name:str, id:str):
        return self.content[name].types[id].type

    def get_primative_type_id_from_id(self, name:str, id:str):
        x = self.content[name].types[id]
        if x.is_pointer:
            return x.alias
        else:
            return id

    def does_node_exist(self, name:str, node_id:str):
        return True if node_id in self.content[name].body_nodes else False

    def get_node(self, name:str, node_id: str):
        # return self.content[name].body_nodes[node_id]
        return self.content[name].body_nodes[node_id][-1]
    
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
    

    def generate_dot_graph(self):
        # print("===graph gen===") # debug


        for key in self.content.keys():
            dot = graphviz.Digraph(comment=f"digraph for {key}", filename=f"digraph_{key}.dot", directory="dots") 
            dot.attr(bgcolor="gray10")
            dot.attr(color="white")
            dot.attr(fontcolor="white")

            x = self._sort_body_nodes_by_tick(key)

            for k in range(0, len(x.keys())):
                # print(f"tick: {k}")

                with dot.subgraph(name=f"cluster_tick_{k}") as ds:
                    ds.attr(style="dashed")
                    ds.attr(label=f"tick {k}")
                    
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

                                    ds.edge(parent_l_id_label, current_node_label, color="white")
                                    ds.edge(parent_r_id_label, current_node_label, color="white")

                                case _:
                                    # should be unreachable
                                    raise Exception(f"{TitanErrors.UNEXPECTED.value} - got {parent_num} parents, but parents exist.", TitanErrors.UNEXPECTED.name)


            # print(dot.source)
            dot.render(view=False, overwrite_source=True)


    def __find_best_parents(self, subject_node: d.Node):

        # if variable is just storing a constant
        if subject_node.operation is Operation.STORE and subject_node.input_left.operation in Operation_Type.GENERIC_CONSTANT_DECLARATION:
            return subject_node.input_left
        
        # a non existant id means that it was created for either loading or arithmetic
        if subject_node.spirv_id not in self.declared_symbols:

            # if a temp id was only created for loading an existing value
            if subject_node.operation is Operation.LOAD:
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


    def _eval_parents_for_non_temp_id(self, current_node: d.Node):
        # a temp id is defined as a LOAD instruction which references an existing symbol
        # in spirv, this looks something like:
        #   %1 = OpLoad %type_int %a
        # where %1 is a temporary id containing the value of %a

        # print(self.declared_symbols)
        # print(current_node)

        
        best = self.__find_best_parents(current_node)

        # print(f"\n\nbest for node {current_node.spirv_id} is\n{best}")

        print(f"best parents for node {current_node.spirv_id} is:")
        print(f"\tL: {best[0]}\n\tR: {best[1]}")



    def clean_graph(self):
        for function in self.content.keys():
            for symbol in self.content[function].body_nodes.keys():
                for node in self.content[function].body_nodes[symbol]:

                    # if node.operation is (Operation.ADD or Operation.SUB or Operation.DIV or Operation.MULT):
                    if node.operation in Operation_Type.ARITHMETIC:
                        self._eval_parents_for_non_temp_id(node)
