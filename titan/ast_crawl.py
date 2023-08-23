# TODO:
# - update all add_symbol calls
# - check return types for _eval_line function
import ast, typing, enum

import type as titan_type
import machine

class _SPIRVHelperGenerator():

    class Sections(enum.Enum):
        CAPABILITY_AND_EXTENSION = enum.auto()
        ENTRY_AND_EXEC_MODES = enum.auto()
        DEBUG_STATEMENTS = enum.auto()
        ANNOTATIONS = enum.auto()
        TYPES = enum.auto()
        VAR_CONST_DECLARATIONS = enum.auto()
        FUNCTIONS = enum.auto()

    class TypeContext(typing.NamedTuple):
        primative_type: titan_type.DataType
        storage_type: titan_type.StorageType = titan_type.StorageType.NONE
        is_constant: bool = False
        is_pointer: bool = False
        is_function_typedef: bool = False
        
    class ConstContext(typing.NamedTuple):
        primative_type: titan_type.DataType
        value: typing.Union[int, float, bool, None]

    class SymbolInfo(typing.NamedTuple):
        type: titan_type.DataType
        location: titan_type.StorageType


    def __init__(self, disable_debug=True):
        self.entry_point = ""
        self._disable_debug = disable_debug
        self._latest_ifexp_selector_id = None
        self._latest_compare_id = None


        class symbol_type_hint(typing.TypedDict):
            symbol: str
            type: typing.Union[int, float, bool, None]

        class declared_constants_hint(typing.TypedDict):
            type: self.ConstContext
            spirv_id: str

        class declared_types_hint(typing.TypedDict):
            type: titan_type.DataType
            spirv_id: str

        class symbol_info_hint(typing.TypedDict):
            symbol_id: str
            info: self.SymbolInfo

        class intermediate_id_type_hint(typing.TypedDict):
            intermediate_id: str
            type: titan_type.DataType

        self.input_port_list: symbol_type_hint = {}
        self.output_port_list: symbol_type_hint = {}

        # attempts to align the output type list with the output port/symbol list
        # this is so that the correct id (assuming that it is handled in order) will be assigned the correct type
        # perhaps slightly over-engineered?
        self._internal_output_port_list_counter = 0 
        self.output_type_list = []

        # TODO: probably remove 
        # self.symbols_and_types: symbol_type_hint = {}

        self.symbol_info: symbol_info_hint = {}

        self.location_id = 0
        self.intermediate_id = 0
        self.return_id = 0
        self.intermediate_ids: intermediate_id_type_hint = {}

        self.declared_constants: declared_constants_hint = {}
        self.declared_types: declared_types_hint = {}
        self.body = []

        self.generated_spirv = {
            self.Sections.CAPABILITY_AND_EXTENSION.name: [],
            self.Sections.ENTRY_AND_EXEC_MODES.name: [],
            self.Sections.DEBUG_STATEMENTS.name: [],
            self.Sections.ANNOTATIONS.name: [],
            self.Sections.TYPES.name: [],
            self.Sections.VAR_CONST_DECLARATIONS.name: [],
            self.Sections.FUNCTIONS.name: []
        }

    def dump(self):
        if not self._disable_debug:

            print(f"[debug info _SPIRVHelperGenerator]\nentry point: {self.entry_point}")
            print(f"input port list: {self.input_port_list}")
            print(f"output port list: {self.output_port_list}")
            print(f"output type list: {self.output_type_list}")

            print(f"symbols with info:")
            for id, info in self.symbol_info.items():
                print(f"\t{id} -> {info}")

            print(f"declared constants:")
            for info, id in self.declared_constants.items():
                print(f"\t{id} -> {info}")


            print(f"declared types:")
            for info, id in self.declared_types.items():
                print(f"\t{id} -> {info}")

            print(f"intermediate line id & type:")
            for id, type in self.intermediate_ids.items():
                print(f"\t{id} -> {type}")

            print(f"generated spirv:")
            for section in self.generated_spirv.keys():
                print(f"section: {section}")

                for value in self.generated_spirv[section]:
                    print(f"\t{value}")

     
    def add_line(self, section: Sections, line:str):
        # self.body.append(line)
        self.generated_spirv[section.name].append(line)

    def add_output_type(self, type):
        self.output_type_list.append(type)

    def add_output_symbol(self, symbol:str):
        self.output_port_list[symbol] = self.output_type_list[self._internal_output_port_list_counter]
        self._internal_output_port_list_counter += 1

    def symbol_exists(self, symbol: str):
        """
        @param symbol: str: symbol name without SPIRV %
        """
        # return True if symbol in self.symbols_and_types else False
        return True if symbol in self.symbol_info else False

    def add_symbol(self, symbol_id: str, info: SymbolInfo):
        self.symbol_info[symbol_id] = info

    def add_symbol(self, symbol_id: str, type, location: titan_type.StorageType):
        self.symbol_info[symbol_id] = self.SymbolInfo(titan_type.DataType(type), location)

    def get_symbol_info(self, symbol_id: str) -> SymbolInfo:
        return self.symbol_info[symbol_id]
    
    # basically works the same as add_symbol
    def update_symbol_info(self, symbol_id:str, info: SymbolInfo):
        self.symbol_info[symbol_id] = info
        
    def add_symbol_if_nonexistant(self, symbol: str, type, location: titan_type.StorageType):

        if symbol not in self.symbol_info:
            self.symbol_info[symbol] = self.SymbolInfo(titan_type.DataType(type), location)
            
            self.add_line(
                self.Sections.DEBUG_STATEMENTS,
                f"OpName %{symbol} \"{symbol}\""
            )

            # if i/o
            if location is (titan_type.StorageType.IN or titan_type.StorageType.OUT):
                # add location (glsl specific i think)
                self.add_line(
                    self.Sections.ANNOTATIONS,
                    f"OpDecorate %{symbol} Location {self.location_id}"
                )

                if location is titan_type.StorageType.IN:
                    self.add_line(
                        self.Sections.ANNOTATIONS,
                        # more glsl specific stuff
                        f"OpDecorate %{symbol} Flat"
                    )

                    # input variable pointer type
                    ptr_ctx = self.TypeContext(
                            titan_type.DataType(type), titan_type.StorageType.IN,
                            False, True, False
                    )

                    ptr_id = self.add_type_if_nonexistant(
                        ptr_ctx,
                        f"%pointer_input_{titan_type.DataType(type).name.lower()}"
                    )

                    self.add_line(
                        self.Sections.VAR_CONST_DECLARATIONS,
                        f"%{symbol} = OpVariable {ptr_id} Input"
                    )
                elif location is titan_type.StorageType.OUT:
                    ptr_ctx = self.TypeContext(
                        titan_type.DataType(type), titan_type.StorageType.IN,
                        False, True, False
                    )

                    ptr_id = self.add_type_if_nonexistant(
                        ptr_ctx,
                        f"%pointer_output_{titan_type.DataType(type).name.lower()}"
                    )

                    self.add_line(
                        self.Sections.VAR_CONST_DECLARATIONS,
                        f"%{symbol} = OpVariable {ptr_id} Output"
                    )
            elif location is titan_type.StorageType.FUNCTION_VAR:
                
                ptr_id = self.add_type_if_nonexistant(
                    self.TypeContext(
                        titan_type.DataType(type), titan_type.StorageType.FUNCTION_VAR,
                        False, True, False
                    ),
                    f"%pointer_funcvar_{titan_type.DataType(type).name.lower()}"
                )
                
                self.add_line(
                    self.Sections.FUNCTIONS,
                    f"%{symbol} = OpVariable {ptr_id} Function"
                )

            self.location_id += 1

            return True
        else:
            return False
        
    def get_symbol_type(self, symbol):
        return self.symbol_info[symbol].type

    # def get_symbol_as_type_context(self, symbol):
    #     """DO NOT USE returns primative type only"""
    #     # TODO: handle funcvars somehow
    #     # perhaps dumb override?
    #     return self.symbols_and_types[symbol]

    
    def intermediate_id_exists(self, intermediate_id: str):
        return True if intermediate_id in self.intermediate_ids else False
    
    def add_intermediate_id(self, intermediate_id: str, type: titan_type.DataType):
        self.intermediate_ids[intermediate_id] = type


    # type helpers
    def type_exists(self, type: TypeContext):
        return True if type in self.declared_types else False
    
    def add_type(self, type: TypeContext, id: str):
        self.declared_types[type] = id

    def get_type_id(self, type: TypeContext):
        return self.declared_types[type]
    
    def get_primative_type_id(self, type: titan_type.DataType):
        return self.declared_types[
            self.TypeContext(titan_type.DataType(type))
        ]

    def add_type_if_nonexistant(self, type: TypeContext, id: str):
        if not self.type_exists(type):
            
            # TODO: remove
            self.add_type(type, id)

            spirv_txt = f"{id} = "

            if type.is_function_typedef:
                prim_tid = self.get_primative_type_id(type.primative_type)
                spirv_txt += f"OpTypeFunction {prim_tid}"
            elif type.is_pointer:
                prim_tid = self.get_primative_type_id(type.primative_type)
                storage_type = ""

                match type.storage_type:
                    case titan_type.StorageType.IN:
                        storage_type = "Input"
                    case titan_type.StorageType.OUT:
                        storage_type = "Output"
                    case titan_type.StorageType.FUNCTION_VAR:
                        storage_type = "Function"
                    case _:
                        raise Exception(f"no text for storage type for {type.storage_type}")

                spirv_txt += f"OpTypePointer {storage_type} {prim_tid}"

            # this should mean we're working with the primative types
            elif (not type.is_constant) and (not type.is_pointer) and (not type.is_function_typedef):

                match type.primative_type:
                    case titan_type.DataType.VOID:
                        spirv_txt += f"OpTypeVoid"
                    case titan_type.DataType.INTEGER:
                        spirv_txt += f"OpTypeInt 32 1"
                    case titan_type.DataType.BOOLEAN:
                        spirv_txt += f"OpTypeBool"
                    case titan_type.DataType.FLOAT:
                        spirv_txt += f"OpTypeFloat 32"
                    case _:
                        raise Exception(f"type text for {type} not implemented yet")
            else:
                raise Exception(f"unable to generate spirv text for type {id} -> {type}")

            self.add_line(
                self.Sections.TYPES,
                spirv_txt
            )

            return id
        else:
            return self.get_type_id(type)

    # const helpers
    def const_exists(self, const: ConstContext):
        return True if const in self.declared_constants else False

    def add_const(self, c_ctx: ConstContext, spirv_id: str):
        self.declared_constants[c_ctx] = spirv_id

    def add_const_if_nonexistant(self, const: ConstContext, negative_val:bool = False):

        if const not in self.declared_constants:
            txt_val = str(const.value)

            const_str = f"const_{titan_type.DataType(const.primative_type).name.lower()}"
            # print(f"[add_const_if_nonexistant] const_str: {const_str}")


            if negative_val:
                txt_val = txt_val.replace("-", "n")

            if const.primative_type is float:
                txt_val = txt_val.replace(".", "_")

            # const_str += f"_{str(const.value).replace('.', '_')}"

            const_str += f"_{txt_val}"

            self.declared_constants[const] = const_str

            self.add_line(
                self.Sections.VAR_CONST_DECLARATIONS,
                f"%{const_str} = OpConstant {self.get_primative_type_id(titan_type.DataType(const.primative_type))} {const.value}"
            )

            return const_str
        else:
            return self.declared_constants[const]

    # TODO: add one that uses the ConstContext thing directly?
    def get_const_id(self, value, type):
        temp_c_ctx = self.ConstContext(type, value)
        return self.declared_constants[temp_c_ctx]
    
    def get_const_id_with_ctx(self, context: ConstContext):
        return self.declared_constants[context]

class GenerateSPIRVFromAST(ast.NodeVisitor):

    def __init__(self, file):
        self._target_file = file
        self._tree = ast.parse(open(file, "r").read())

        # self.spirv = machine.SPIRV_ASM()
        self.spirv_helper = _SPIRVHelperGenerator(disable_debug=False)

    def crawl(self):
        # wrapper function for visiting the top of the tree
        self.visit(self._tree)
        self.spirv_helper.dump()

    # TODO: probably inefficient
    def create_file_as_string(self):
        fake_file = ""

        # key=section, value=list of lines
        for lines in self.spirv_helper.generated_spirv.values():
            for line in lines:
                fake_file += f"{line}\n"

        return fake_file
    
    def output_to_file(self, filename:str):
        ff = self.create_file_as_string()

        with open(f"{filename}.spvasm", "w") as f:
            for line in ff:
                f.write(line)
    
    def _get_python_type_from_string(self, type: str):
        """returns python type from <class 'x'> string"""
        return eval(type.split("'")[0])

    # TODO: can these be turned into enums instead?
    def _return_string_from_type(self, type):
        if (type is int):
            return "int"
        elif (type is float):
            return "float"
        elif (type is bool):
            return "bool"
        else:
            raise Exception(f"unexpected type {type}")
        
    def _return_type_from_string(self, type_as_string: str):
        if type_as_string == "int":
            return int
        elif type_as_string == "float":
            return float
        elif type_as_string == "bool":
            return bool
        else:
            raise Exception(f"unexpected type as string {type_as_string}")


    def visit_Module(self, node):
        _module_contains_step_function = False

        print(f"found {len(node.body)} functions\n")

        for i in range(len(node.body)):
            if node.body[i].name == "step":
                _module_contains_step_function = True

        if _module_contains_step_function:
            self.spirv_helper.entry_point = "step"
        else:
            # TODO: better to error or assume?
            self.spirv_helper.entry_point = node.body[0].name

        # spirv boilerplate
        self.spirv_helper.add_line(
            self.spirv_helper.Sections.CAPABILITY_AND_EXTENSION,
            f"OpCapability Shader"
        )

        self.spirv_helper.add_line(
            self.spirv_helper.Sections.CAPABILITY_AND_EXTENSION,
            f"OpMemoryModel Logical GLSL450"
        )

        for fn in node.body:
            # print(f"function: {fn.name} returns {fn.returns.id}")
            self.visit_FunctionDef(fn)

            # if the function is our entry point, we want to capture its params
            # TODO: this will fail if the entry point is not the first function in the list,
            #       since the lists/dicts will contain previous function entries, messing with the names
            if fn.name == self.spirv_helper.entry_point:
                # take contents of input/output ports and convert them into ids
                ports_str = ""

                for symbol, s_ctx in self.spirv_helper.symbol_info.items():
                    # print(s_ctx.location)
                    if (s_ctx.location is titan_type.StorageType.IN) or (s_ctx.location is titan_type.StorageType.OUT):
                        ports_str += f"%{symbol} "

                self.spirv_helper.add_line(
                    self.spirv_helper.Sections.ENTRY_AND_EXEC_MODES,
                    f"OpEntryPoint Fragment %{fn.name} \"{fn.name}\" {ports_str}"
                )

            self.spirv_helper.add_line(
                self.spirv_helper.Sections.ENTRY_AND_EXEC_MODES,
                f"OpExecutionMode %{fn.name} OriginUpperLeft"
            )

            print(f"exit function {fn.name}\n")


    
    def visit_FunctionDef(self, node):
        print(f"function {node.name} returns type {node.returns.id}\n\t{node._fields}")
        
        self.spirv_helper.add_line(
            self.spirv_helper.Sections.DEBUG_STATEMENTS,
            f"OpName %{node.name} \"{node.name}\""
        )

        # TODO: how to make so this only needs to run once? (low priority)
        void_ctx = self.spirv_helper.TypeContext(
            titan_type.DataType.VOID, titan_type.StorageType.NONE
        )

        t_void_id = self.spirv_helper.add_type_if_nonexistant(
            void_ctx,
            f"%type_void"
        )

        # make spirv function def for OpTypeFunction
        fn_ctx = self.spirv_helper.TypeContext(
            titan_type.DataType.VOID, titan_type.StorageType.NONE, False, False, True
        )

        t_fn_void_id = self.spirv_helper.add_type_if_nonexistant(
            fn_ctx,
            f"%type_function_{(titan_type.DataType.VOID.name).lower()}"
        )

        # mark start of function
        self.spirv_helper.add_line(
            self.spirv_helper.Sections.FUNCTIONS,
            f"%{node.name} = OpFunction {t_void_id} None {t_fn_void_id}"
        )

        self.spirv_helper.add_line(
            self.spirv_helper.Sections.FUNCTIONS,
            f"%label_{node.name} = OpLabel"
        )


        # iterate through each arg, make type & pointer type
        for args in node.args.args:
            # TODO: remove/fix/rework this try-except block
            # may have to use __attrs__ or something to check if args contains annotation
            try:
                # print(f"arg: {args.annotation.id}", end=" ")

                # TODO: not a fan of using "eval" to determine type, is there a better way?
                type_class = eval(args.annotation.id.split("'")[0])


                # check if generic type exists
                t_ctx = self.spirv_helper.TypeContext(
                    titan_type.DataType(type_class), titan_type.StorageType.NONE,
                    False, False
                )

                self.spirv_helper.add_type_if_nonexistant(
                    t_ctx,
                    f"%type_{(titan_type.DataType(type_class).name).lower()}"
                )

                # dealing with args means that a special type needs to be made
                ptr_t_ctx = self.spirv_helper.TypeContext(
                    titan_type.DataType(type_class), titan_type.StorageType.IN, False, True
                )

                self.spirv_helper.add_type_if_nonexistant(
                    ptr_t_ctx,
                    f"%pointer_input_{(titan_type.DataType(type_class).name).lower()}"
                )

                self.spirv_helper.add_symbol_if_nonexistant(
                    args.arg,
                    type_class,
                    titan_type.StorageType.IN
                )
            except AttributeError:
                # self.spirv_helper.add_input(args.arg, None)
                self.spirv_helper.add_symbol(args.arg, None, titan_type.StorageType.IN)

        # TODO: needs implementation for multiple returns
        # handle returns (types for now)
        if isinstance(node.returns, ast.Call):
            raise Exception(f"multiple returns/function calls not handled yet")
        elif isinstance(node.returns, ast.Name):
            type_class = self._get_python_type_from_string(node.returns.id)
            self.spirv_helper.add_output_type(type_class)

            type_as_string = titan_type.DataType(type_class).name.lower()

            # add primative type if it does not exist
            self.spirv_helper.add_type_if_nonexistant(
                self.spirv_helper.TypeContext(
                    titan_type.DataType(type_class)
                ),
                f"%type_{type_as_string}"
            )

            # add pointer type if it does not exist
            self.spirv_helper.add_type_if_nonexistant(
                self.spirv_helper.TypeContext(
                    titan_type.DataType(type_class), titan_type.StorageType.OUT,
                    False, True, False
                ),
                f"%pointer_output_{type_as_string}"
            )

            
    
        print(f"body start {node.name}")
        super().generic_visit(node)
        print(f"body end {node.name}")

        # TODO: add function that lets me add lists of strings instead of having to
        #       write this every time
        # spirv boilerplate for end of function
        self.spirv_helper.add_line(
            self.spirv_helper.Sections.FUNCTIONS,
            f"OpReturn"
        )

        self.spirv_helper.add_line(
            self.spirv_helper.Sections.FUNCTIONS,
            f"OpFunctionEnd"
        )


    def visit_Call(self, node):
        print(f"{node.__class__.__name__} {node._fields}")
        print(f"{node.func.id}")
        # print(f"{node.args}")

        for arg in node.args:
            print(f"{arg.id}")


    def visit_Assign(self, node):
        if len(node.targets) > 1:
            raise Exception("multiple assignments not supported")

        eval_id, eval_ctx = self._eval_line_wrap(node)
        type_class = self._extract_type(eval_ctx)

        if type_class is None:
            raise Exception("evaluated type as None for variable with no type declaration")
        
        t_id = self.spirv_helper.add_type_if_nonexistant(
            self.spirv_helper.TypeContext(
                titan_type.DataType(type_class)
            ),
            f"%type_{titan_type.DataType(type_class).name.lower()}"
        )

        self.spirv_helper.add_symbol_if_nonexistant(node.targets[0].id, type_class, titan_type.StorageType.FUNCTION_VAR)

        self.spirv_helper.add_line(
            self.spirv_helper.Sections.FUNCTIONS,
            f"OpStore %{node.targets[0].id} %{eval_id.strip('%')}"
        )

        
    def visit_AnnAssign(self, node):
        # print(f"{node.annotation.id} {node.target.id} = {node.value.value}")
        type_class = self._get_python_type_from_string(node.annotation.id)

        t_id = self.spirv_helper.add_type_if_nonexistant(
            self.spirv_helper.TypeContext(titan_type.DataType(type_class)),
            f"%type_{titan_type.DataType(type_class).name.lower()}"
        )

        eval_id, eval_ctx = self._eval_line_wrap(node)
        eval_type = self._extract_type(eval_ctx)

        if eval_type != type_class:
            raise Exception(f"mismatched types: eval_type {eval_type} - type_class {type_class}")

        self.spirv_helper.add_symbol_if_nonexistant(node.target.id, type_class, titan_type.StorageType.FUNCTION_VAR)

        self.spirv_helper.add_line(
            self.spirv_helper.Sections.FUNCTIONS,
            f"OpStore %{node.target.id} {eval_id}"
        )



    def visit_Return(self, node):
        """
        handle return nodes
        """
        # TODO: add calls to _eval_line to get proper id for node
        if isinstance(node.value, ast.Constant):
            print(f"returning const: {node.value.value}")
            raise Exception("TODO: return constant value")
        elif isinstance(node.value, ast.Name):
            print(f"returning name: {node.value.id}")
            id, ctx = self._eval_line(node.value)

            if self.spirv_helper.symbol_exists(id):
                s_info = self.spirv_helper.get_symbol_info(id)

                if s_info.location == titan_type.StorageType.FUNCTION_VAR:
                    s_info_new = self.spirv_helper.SymbolInfo(
                        ctx, titan_type.StorageType.OUT
                    )

                    self.spirv_helper.update_symbol_info(id, s_info_new)

                    ptr_t_id = self.spirv_helper.get_type_id(
                        self.spirv_helper.TypeContext(
                            ctx, titan_type.StorageType.FUNCTION_VAR, False, True
                        )
                    )

                    ptr_t_out_id = self.spirv_helper.get_type_id(
                        self.spirv_helper.TypeContext(
                            ctx, titan_type.StorageType.OUT, False, True
                        )
                    )

                    self.spirv_helper.add_line(
                        self.spirv_helper.Sections.VAR_CONST_DECLARATIONS,
                        f"%{id} = OpVariable {ptr_t_out_id} Output"
                    )

                    str_to_match = f"%{id} = OpVariable {ptr_t_id} Function"
                    
                    # TODO: implement better method
                    # bruteforce remove reference of symbol declaration in FUNCTIONS section
                    i = 0
                    for line in self.spirv_helper.generated_spirv[self.spirv_helper.Sections.FUNCTIONS.name]:
                        if line == str_to_match:
                            self.spirv_helper.generated_spirv[self.spirv_helper.Sections.FUNCTIONS.name].pop(i)
                            break
                        i += 1


        elif isinstance(node.value, ast.IfExp):
            # print(f"returning if expression")
            # print(node.value._fields)
            # print(f"test: {node.value.test._fields}")

            # error prone
            # node.value.test.ops is a list! be careful and check length before doing anything
            # print(f"\tleft: {node.value.test.left.id}")

            # print("\tops & comparators:")
            # for i in range(len(node.value.test.ops)):
                # print(f"\t{node.value.test.ops[i].__class__.__name__} {self._extract_content(node.value.test.comparators[i])}")

            #        v node.value.body.id
            # return c if a > 0 else 0 
            #             ^ ^        ^ node.value.orelse
            #             | | node.value.test.{ops|comparators}
            #             | node.value.test.left
            # print(f"body: {node.value.body.id} {node.value.body.ctx}")

            # print(f"orelse: {self._extract_content(node.value.orelse)}")

            # TODO: need to get ID somehow, move the IfExp function to something else accessible and call it directly?
            super().generic_visit(node)

            # because this is direct return, we have to make a temp symbol into which we can return (in spirv terms)
            # we have to also add it to the symbols list, making sure that it has the same type as the indicated return type
            # and that it doesn't clash with the return type

            out_str_id = f"titan_return_id_{self.spirv_helper.return_id}"
            self.spirv_helper.return_id += 1
            # TODO: make sure names don't clash?
            self.spirv_helper.add_symbol_if_nonexistant(
                out_str_id, self.spirv_helper.output_type_list[0], titan_type.StorageType.OUT
            )

            self.spirv_helper.add_output_symbol(out_str_id)

            # store titan_id_x into the newly created return variable
            self.spirv_helper.add_line(
                self.spirv_helper.Sections.FUNCTIONS,
                f"OpStore %{out_str_id} %{self.spirv_helper._latest_ifexp_selector_id}"
            )

            ptr_t_out_ctx = self.spirv_helper.TypeContext(
                titan_type.DataType(self.spirv_helper.output_type_list[0]), titan_type.StorageType.OUT,
                False, True, False
            )

            ptr_t_out_id = self.spirv_helper.get_type_id(ptr_t_out_ctx)

            self.spirv_helper.add_line(
                self.spirv_helper.Sections.VAR_CONST_DECLARATIONS,
                f"%{out_str_id} = OpVariable %{ptr_t_out_id.strip('%')} Output"
            )
            

            # print(f"return {node.value.body.id} if {node.value.test.left.id} {node.value.test.ops[0].__class__.__name__} {self._extract_content(node.value.test.comparators[0])} else {self._extract_content(node.value.orelse)}")
        elif isinstance(node.value, ast.BinOp):
            raise Exception("TODO implement handling binops for return values")

            id, ctx = self._eval_line(node.value)
            print(f"returning binop val ({id})")

            if self.spirv_helper.symbol_exists(id):
                print("this was a symbol")
            elif self.spirv_helper.intermediate_id_exists(id):
                print("this was a temp id")
            else:
                raise Exception("idk")

        else:
            raise Exception(f"unhandled type during return node evaluation {node} {type(node)}")


    def visit_Name(self, node): pass

    
    def _get_id_of_node(self, node):
        if isinstance(node, ast.Name):
            if self.spirv_helper.symbol_exists(node.id):
                return node.id
            else:
                raise Exception(f"symbol referenced but does not exist")
        elif isinstance(node, ast.Constant):

            c_ctx = self.spirv_helper.ConstContext(titan_type.DataType(type(node.value)), node.value)
            if self.spirv_helper.const_exists(c_ctx):
                return self.spirv_helper.get_const_id_with_ctx(node.value, c_ctx)
            else:
                # TODO: does not account for negative numbers, probably need an UnaryOp section 
                c_id = self.spirv_helper.add_const_if_nonexistant(
                    c_ctx, False
                )
                return c_id
            # return self.spirv_helper.get_const_id(node.value, titan_type.DataType(type(node.value)))
        else:
            raise Exception(f"unhandled node {node} {type(node)}")

    def visit_IfExp(self, node):
        print(f"[visit_IfExp] {node} {node._fields}")

        print(f"\tbody: {node.body.id} {node.body.ctx.__class__.__name__}")
        # print(f"\ttest & ops (testing against {node.test.left.id}):")
        # for i in range(len(node.test.ops)):
            # print(f"\t\t{node.test.ops[i].__class__.__name__} {self._extract_content(node.test.comparators[i])}")
        print(f"\torelse: {self._extract_content(node.orelse)}")

        # this should take care of the comparison node
        super().generic_visit(node)

        # TODO: probably should check if both types match, but as a hack we check only the left one and pray
        t_id = self.spirv_helper.get_primative_type_id(self.spirv_helper.get_symbol_type(node.test.left.id))

        body_id = self._get_id_of_node(node.body)
        orelse_id = self._get_id_of_node(node.orelse)

        self.spirv_helper.add_line(
            self.spirv_helper.Sections.FUNCTIONS,
            #TODO:                                                                  vvv should this just be always -1 of the current id?
            f"%titan_id_{self.spirv_helper.intermediate_id} = OpSelect {t_id} {self.spirv_helper._latest_compare_id} %{body_id} %{orelse_id}"
        )

        # add id, set it as latest, increment by 1
        self.spirv_helper.add_intermediate_id(f"titan_id_{self.spirv_helper.intermediate_id}", bool)
        self.spirv_helper._latest_ifexp_selector_id = f"titan_id_{self.spirv_helper.intermediate_id}"
        self.spirv_helper.intermediate_id += 1




    # comparison only, do not need to worry about the "orelse" value
    def visit_Compare(self, node):
        # print(f"compare: {node._fields}")

        if len(node.ops) > 1:
            # TODO: will probably need recursive function to evaluate all comparisons?
            raise Exception("TODO: cannot handle multiple comparisons yet")

        # print(f"left: {node.left.id} op:{node.ops[0].__class__.__name__} comparator:{self._extract_content(node.comparators[0])}")

        t_id = self.spirv_helper.add_type_if_nonexistant(
            self.spirv_helper.TypeContext(
                titan_type.DataType.BOOLEAN
            ),
            f"%type_{titan_type.DataType.BOOLEAN.name.lower()}"
        )

        left_id = None
        right_id = None
        opcode = None
        target_type = self.spirv_helper.get_symbol_type(node.left.id) # this will need to be changed to whatever object the left operand is

        # if we're dealing with a symbol
        # TODO: implement for right node
        if isinstance(node.left, ast.Name):
            # lets just make sure it actually exists...
            if not self.spirv_helper.symbol_exists(node.left.id):
                raise Exception(f"got ast.Name object implying a symbol, but no related symbol was found... {node.left.id}")
            
            left_type_id = self.spirv_helper.get_primative_type_id(self.spirv_helper.get_symbol_type(node.left.id))
            left_id = f"temp_{node.left.id}"
            self.spirv_helper.add_line(
                self.spirv_helper.Sections.FUNCTIONS,
                f"%{left_id} = OpLoad {left_type_id} %{node.left.id}"
            )
        else:
            raise Exception(f"unhandled instance when evaluating left operand {node.left} {type(node.left)}")
        
        print(f"COMPARATOR: {node.comparators[0]} {type(node.comparators[0])}")

        if isinstance(node.comparators[0], ast.Constant):
            print(node.comparators[0].value)
            print(node.comparators[0].kind)
            
            # TODO: is there a better way of getting the type?
            # right_id = self.spirv_helper.get_const_id(node.comparators[0].value, type(node.comparators[0].value))

            right_id = self.spirv_helper.add_const_if_nonexistant(
                self.spirv_helper.ConstContext(
                    titan_type.DataType(type(node.comparators[0].value)), 
                    node.comparators[0].value
                )
            )

        else:
            raise Exception(f"unhandled instance when checking comparator {node.comparators[0]} {type(node.comparators[0])}")


        # if int .. if float
        # opcode = relevant opcode for comparison 
        _operator = node.ops[0]
        # error prone? might not always be guaranteed to be a titan_type
        if target_type.value is int:
            match type(node.ops[0]):
                case ast.Eq:
                    opcode = "OpIEqual"
                case ast.NotEq:
                    opcode = "OpINotEqual"
                case ast.Lt:
                    opcode = "OpSLessThan"
                case ast.LtE:
                    opcode = "OpSLessThanEqual"
                case ast.Gt:
                    opcode = "OpSGreaterThan"
                case ast.GtE:
                    opcode = "OpSGreaterThanEqual"

        elif target_type.value is float:
            match type(node.ops[0]):
                case ast.Eq:
                    opcode = "OpFOrdEqual"
                case ast.NotEq:
                    opcode = "OpFOrdNotEqual"
                case ast.Lt:
                    opcode = "OpFOrdLessThan"
                case ast.LtE:
                    opcode = "OpFOrdLessThanEqual"
                case ast.Gt:
                    opcode = "OpFOrdGreaterThan"
                case ast.GtE:
                    opcode = "OpFOrdGreaterThanEqual"

        else:
            raise Exception(f"unhandled type during comparison {target_type}")
        
        self.spirv_helper.add_intermediate_id(f"titan_id_{self.spirv_helper.intermediate_id}", type(node.comparators[0].value))
        self.spirv_helper.add_line(
            self.spirv_helper.Sections.FUNCTIONS,
            f"%titan_id_{self.spirv_helper.intermediate_id} = {opcode} {t_id} %{left_id} %{right_id}"
        )

        self.spirv_helper._latest_compare_id = f"%titan_id_{self.spirv_helper.intermediate_id}"
        self.spirv_helper.intermediate_id += 1

    # TODO: figure out exactly what info is needed from here, if any
    def visit_arguments(self, node): pass

    def visit_Constant(self, node): pass

    def generic_visit(self, node):
        print(f"{node.__class__.__name__} {node._fields}")

    def _extract_content(self, node):
        """
        returns value if node is ast.Constant, id if node is ast.Name
        """
        
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return node.id
        else:
            raise Exception(f"idk what to do for {type(node)}")

    def _extract_type(self, context):

        if isinstance(context, self.spirv_helper.TypeContext):
            return context.primative_type
        elif isinstance(context, self.spirv_helper.ConstContext):
            return context.primative_type
        elif isinstance(context, titan_type.DataType):
            return context.value

    def _eval_line(self, node):
        """
        returns line id and line context
        """
        if isinstance(node, ast.BinOp):

            left_id, left_ctx = self._eval_line(node.left)
            right_id, right_ctx = self._eval_line(node.right)

            return_ctx = None
            chosen_type = None
            spirv_line_str = f"titan_id_{self.spirv_helper.intermediate_id}"

            left_type = self._extract_type(left_ctx)
            left_type_id = self.spirv_helper.get_primative_type_id(left_type)

            right_type = self._extract_type(right_ctx)
            right_type_id = self.spirv_helper.get_primative_type_id(right_type)

            # print(f"L: {left_id} HAS TYPE {left_type} (id: {left_type_id}) ({left_ctx} {type(left_ctx)})")
            # print(f"R: {right_id} HAS TYPE {right_type} (id: {right_type_id}) ({right_ctx} {type(right_ctx)})")
            
            # print(f"{node.op.__class__.__name__} {isinstance(node.op, ast.Add)}")

            if left_type is not right_type:
                raise Exception(f"mismatched types l: {left_type}  r: {right_type}")

            if left_type is None:
                return_ctx = right_ctx
                chosen_type = right_type
            elif right_type is None:
                return_ctx = left_ctx
                chosen_type = left_type
            elif left_type is right_type:
                return_ctx = left_ctx
                chosen_type = left_type
            else:
                raise Exception(f"unable to determine return type (L: {left_type} , R: {right_type})")

            if self.spirv_helper.symbol_exists(left_id):
                temp_left_id = f"temp_{left_id}"
                self.spirv_helper.add_line(
                    self.spirv_helper.Sections.FUNCTIONS,
                    f"%{temp_left_id} = OpLoad {left_type_id} %{left_id}"
                )

                left_id = temp_left_id

            if self.spirv_helper.symbol_exists(right_id):
                temp_right_id = f"temp_{right_id}"
                self.spirv_helper.add_line(
                    self.spirv_helper.Sections.FUNCTIONS,
                    f"%{temp_right_id} = OpLoad {right_type_id} %{right_id}"
                )

                right_id = temp_right_id

            self.spirv_helper.add_intermediate_id(f"{spirv_line_str}", chosen_type)
            chosen_type_id = self.spirv_helper.get_primative_type_id(titan_type.DataType(chosen_type))

            # set the appropriate opcode
            opcode = None
            if chosen_type is int:
                match type(node.op):
                    case ast.Add:
                        opcode = "OpIAdd"
                    case ast.Sub:
                        opcode = "OpISub"
                    case ast.Mult:
                        opcode = "OpIMul"
                    case ast.Div:
                        opcode = "OpSDiv"

            elif chosen_type is float:
                match type(node.op):
                    case ast.Add:
                        opcode = "OpFAdd"
                    case ast.Sub:
                        opcode = "OpFSub"
                    case ast.Mult:
                        opcode = "OpFMult"
                    case ast.Div:
                        opcode = "OpFDiv"
            else:
                raise Exception(f"unexpected operator {node.op}")
            
            if opcode is None:
                raise Exception(f"opcode was not updated, why? {node.op} {chosen_type} {left_id} {right_id}")

            self.spirv_helper.add_line(
                self.spirv_helper.Sections.FUNCTIONS,
                f"%{spirv_line_str} = {opcode} {chosen_type_id} %{left_id.strip('%')} %{right_id.strip('%')}"
            )


            # TODO: check which type is not None, and propagate that back up
            # TODO: should we change the type for a symbol?
            self.spirv_helper.intermediate_id += 1
            return spirv_line_str, return_ctx
        elif isinstance(node, ast.UnaryOp):

            if isinstance(node.op, ast.USub):
                value = node.operand.value

                if type(value) not in [int, float, bool]:
                    raise Exception(f"got unexpected constant value type {type(value)}")

                c_ctx = self.spirv_helper.ConstContext(type(value), value * -1)

                if not self.spirv_helper.const_exists(c_ctx):
                    # id = f"%const_{self._return_string_from_type(type(value))}_n{str(value).replace('.', '_')}"
                    id = f"%const_{titan_type.DataType(type(value)).name.lower()}_n{str(value).replace('.', '_')}"
                    # self.spirv_helper.add_const(c_ctx, id)
                    self.spirv_helper.add_const_if_nonexistant(c_ctx, True)
                    return id, c_ctx
                else:
                    return self.spirv_helper.get_const_id(value*-1, type(value)), c_ctx

            raise Exception(f"unhandled additional operator in unaryop class {node.op}")
            # return f"{node.op.__class__.__name__} {node.operand.value} {type(node.operand.value)} ({isinstance(node.op,ast.USub)})"

        elif isinstance(node, ast.Name):
            if not self.spirv_helper.symbol_exists(node.id):
                raise Exception(f"symbol does not exist {node.id}")

            return f"{node.id}", self.spirv_helper.get_symbol_type(node.id)

        elif isinstance(node, ast.Constant):
            # TODO: maybe use titan_types instead of python types?
            c_ctx = self.spirv_helper.ConstContext(type(node.value), node.value)

            if not self.spirv_helper.const_exists(c_ctx):
                # TODO: check if type also exists?
                # id = f"%const_{self._return_string_from_type(type(node.value))}_{node.value}"
                id = f"%const_{titan_type.DataType(type(node.value)).name.lower()}_{str(node.value).replace('.', '_')}"
                # self.spirv_helper.add_const(c_ctx, id)
                self.spirv_helper.add_const_if_nonexistant(c_ctx)
                return id, c_ctx
            else:
                return self.spirv_helper.get_const_id(node.value, type(node.value)), c_ctx
                
        else:
            print(f"unexpected {type(node)} to parse")

    def _eval_line_wrap(self, node):
        """
        works on ast.Assign or ast.AnnAssign nodes
        """
        # print(node._fields)

        if isinstance(node, ast.Assign):
            for target in node.targets:
                print(target.id, end="")

                evaluated = self._eval_line(node.value)
                print(f" = {evaluated}")
                return evaluated

        elif isinstance(node, ast.AnnAssign):
            print(node.target.id, end="")
            
            evaluated = self._eval_line(node.value)
            print(f" = {evaluated}")
            return evaluated