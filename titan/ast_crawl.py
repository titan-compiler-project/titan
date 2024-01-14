# TODO:
# - update all add_symbol calls
# - check return types for _eval_line function
import ast, typing, enum, logging, json

import common.type as titan_type
import machine
import common.errors as errors

class _SPIRVHelperGenerator():
    """Helper class that provides functions related to SPIR-V generation."""

    class Sections(enum.Enum):
        """ Enum containing sections that are present in the final SPIR-V assembly file.
        
            Dividing the SPIR-V file into sections helps with ensuring that the code is
            placed in the right spot, and can be easily altered if needed.
        """
        CAPABILITY_AND_EXTENSION = enum.auto()
        ENTRY_AND_EXEC_MODES = enum.auto()
        DEBUG_STATEMENTS = enum.auto()
        ANNOTATIONS = enum.auto()
        TYPES = enum.auto()
        VAR_CONST_DECLARATIONS = enum.auto()
        FUNCTIONS = enum.auto()

    class TypeContext(typing.NamedTuple):
        """ Tuple that provides context about a given type. Used to align Python types with SPIR-V.
        
            Attributes:
                primative_type (titan.common.type.DataType): Base/primative (python) type.
                storage_type (titan.common.type.StorageType): Storage type in SPIR-V.
                is_constant (bool): Type describes a constant.
                is_pointer (bool): Type describes a pointer.
                is_function_typedef (bool): Type describes a function definition. 
        """
        primative_type: titan_type.DataType
        storage_type: titan_type.StorageType = titan_type.StorageType.NONE
        is_constant: bool = False
        is_pointer: bool = False
        is_function_typedef: bool = False
        
    class ConstContext(typing.NamedTuple):
        """ Tuple that provides context about a given constant.
        
            Attributes:
                primative_type (titan.common.type.DataType): Base/primative (python) type.
                value: Value of the constant. Can be int, float, bool or None.
        """
        primative_type: titan_type.DataType
        value: typing.Union[int, float, bool, None]

    class SymbolInfo(typing.NamedTuple):
        """ Tuple that associates a primative type with a storage location.

            Attributes:
                type (titan.common.type.DataType): Base/primative (python) type.
                location (titan.common.type.StorageType): Storage type in SPIR-V.
        """
        type: titan_type.DataType
        location: titan_type.StorageType


    def __init__(self, disable_debug=True):
        """ Init function for _SPIRVHelperGenerator.

            Creates various attributes and allows for helper function access.
        
            Args:
                disable_debug (bool): Disable debug output.

            Attributes:
                entry_point (string): TODO
                _disable_debug (bool): Disables debug. Set to value of parameter.
                _latest_ifexp_selector_id (None): Last known ID for an if-expression selector.
                _latest_compare_id (None): Last known ID for a compare expression.
                _latest_function_name (None): TODO
                _decorator_dict: Stores information regarding decorators are used on which functions.
                input_port_list (TypedDict): List of input port names and their primative types.
                output_port_lsit (TypedDict): List of output port names and their primative types.
                _internal_output_port_list_counter (None): TODO
                output_type_list: TODO
                symbol_info: TODO
                location_id: TODO
                intermediate_id (int): Keep track of latest intermediate ID (used by unrolled expressions).
                return_id (int): TODO
                intermediate_ids: List of used intermediate IDs. Stores ID as string and primative type.
                declared_constants: List of declared constants. Stores ConstContext and string ID of constant.
                declared_types: List of declared types. Stores primative type and string ID.
                body: TODO
                generated_spirv (dict): Dictionary indexed with Sections enum, and stores generated lines in a list.
        """

        self.entry_point = ""
        self._disable_debug = disable_debug
        self._latest_ifexp_selector_id = None
        self._latest_compare_id = None
        self._latest_function_name = None

        self._decorator_dict = {}


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
        """Output debug info if debug flag has been set. Uses the logging library."""
        if not self._disable_debug:

            logging.debug(f"[debug info _SPIRVHelperGenerator]")
            logging.debug(f"entry point: {self.entry_point}")
            logging.debug(f"input port list: {self.input_port_list}")
            logging.debug(f"output port list: {self.output_port_list}")
            logging.debug(f"output type list: {self.output_type_list}")

            logging.debug(f"symbols with info:")
            for id, info in self.symbol_info.items():
                logging.debug(f"\t{id} -> {info}")

            logging.debug(f"declared constants:")
            for info, id in self.declared_constants.items():
                logging.debug(f"\t{id} -> {info}")


            logging.debug(f"declared types:")
            for info, id in self.declared_types.items():
                logging.debug(f"\t{id} -> {info}")

            logging.debug(f"intermediate line id & type:")
            for id, type in self.intermediate_ids.items():
                logging.debug(f"\t{id} -> {type}")

            logging.debug(f"generated spirv:")
            for section in self.generated_spirv.keys():
                logging.debug(f"section: {section}")

                for value in self.generated_spirv[section]:
                    logging.debug(f"\t{value}")

     
    def add_line(self, section: Sections, line:str):
        # """add a line of generated SPIR-V to a certain section"""
        """ Add a generated line of SPIR-V to a given section.
        
            Args:
                section (titan.ast_crawl._SPIRVHelperGenerator.Sections): The section to append the line to.
                line (str): The line to add.
        """
        self.generated_spirv[section.name].append(line)

    def add_output_type(self, type):
        """ Add an output type.
        
            Args:
                type: The type to add.

            Warning:
                This function may be removed in the future. It's not clear _what_ specifically it is adding.
                Could possibly cause issues with the rest of the program.
        """
        self.output_type_list.append(type)

    def add_output_symbol(self, symbol:str):
        """ Add an output symbol to the output_port_list.

            Also increments an internal counter.

            Args:
                symbol (str): The symbol to be added. 
        """

        # HACK: what is the point of this line
        self.output_port_list[symbol] = self.output_type_list[self._internal_output_port_list_counter]
        self._internal_output_port_list_counter += 1

    def symbol_exists(self, symbol: str) -> bool:
        """ Check if a symbol exists.
        
            Args:
                symbol (str): Given symbol name, with the SPIR-V "%" prefix.

            Returns:
                symbol_exists: True if symbol exists, else False.
        """

        return True if symbol in self.symbol_info else False

    # no overloading
    # def add_symbol(self, symbol_id: str, info: SymbolInfo):
        # self.symbol_info[symbol_id] = info

    def add_symbol(self, symbol_id: str, type, location: titan_type.StorageType):
        """ Add a symbol.

            The value ``type`` arg will be automatically converted into a valid ``titan.common.type.DataType`` value.
        
            Args:
                symbol_id: ID given to the symbol.
                type: Python type of the symbol.
                location: Given storage location for the symbol. Required for SPIR-V.

            TODO:
                Need to determine whether the symbol ID contains the "%" prefix or not.
        """
        self.symbol_info[symbol_id] = self.SymbolInfo(titan_type.DataType(type), location)

    def get_symbol_info(self, symbol_id: str) -> SymbolInfo:
        """ Get information regarding a given symbol via ID.

            Args:
                symbol_id: ID of the symbol to check.

            Returns:
                Symbol information tuple.
        """
        return self.symbol_info[symbol_id]
    
    # basically works the same as add_symbol
    def update_symbol_info(self, symbol_id:str, info: SymbolInfo):
        """ Update the information currently stored of a given symbol.

            Warning:
                Simply overwrites an existing entry. The symbol _must_ have be declared before using this,
                otherwise you may run into a KeyError exception.

            Args:
                symbol_id: ID of the symbol to update.
                info: Tuple to update the information with.
        """
        self.symbol_info[symbol_id] = info
        
    def add_symbol_if_nonexistant(self, symbol: str, type, location: titan_type.StorageType) -> bool:
        """ Add a symbol, only if it does not already exist.

            Method first checks if symbol exists or not. If not, it'll generate the corresponding SPIR-V
            lines depending on its type and location, and increment the ``location_id`` counter.

            Args:
                symbol: Name of the symbol to add.
                type: Python type of the symbol.
                location: Given storage location for the symbol. Required for SPIR-V.

            Returns:
                symbol_added: True if symbol has been added, else False.
        """

        if symbol not in self.symbol_info:
            self.symbol_info[symbol] = self.SymbolInfo(titan_type.DataType(type), location)
            
            self.add_line(
                self.Sections.DEBUG_STATEMENTS,
                f"OpName %{symbol} \"{symbol}\""
            )

            # TODO: more elegant solution?
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
        
    def get_symbol_type(self, symbol:str) -> titan_type.DataType:
        """ Get symbol type, using symbol ID.

            Args:
                symbol: Symbol ID
            
            Returns:
                Primative type of symbol.
        """

        # symbol_info[symbol] -> info (SymbolInfo).type
        return self.symbol_info[symbol].type



    # def get_symbol_as_type_context(self, symbol):
    #     """DO NOT USE returns primative type only"""
    #     # TODO: handle funcvars somehow
    #     # perhaps dumb override?
    #     return self.symbols_and_types[symbol]

    
    def intermediate_id_exists(self, intermediate_id: str) -> bool:
        """ Check if an intermediate ID already exists.
        
            Args:
                intermediate_id: Intermediate ID to check.
            
            Returns:
                True if intermediate ID already exists, else False.
        """
        return True if intermediate_id in self.intermediate_ids else False
    
    def add_intermediate_id(self, intermediate_id: str, type: titan_type.DataType):
        """ Add an intermediate ID.

            Args:
                intermediate_id: Intermediate ID to add.
                type: Type to associate with the intermediate ID.
        """
        self.intermediate_ids[intermediate_id] = type

    def get_type_of_intermediate_id(self, intermediate_id: str) -> titan_type.DataType:
        """ Returns the type of an intermediate ID, _not_ the type ID.

            Args:
                intermediate_id: Intermediate ID to return the type of.

            Returns:
                Primative intermediate ID type.
        """
        return self.intermediate_ids[intermediate_id]

    # type helpers
    def type_exists(self, type: TypeContext) -> bool:
        """ Check if a type already exists, using a ``TypeContext``.

            Args:
                type: Type to check if it exists.

            Returns:
                True if type exists, else False.
        """
        return True if type in self.declared_types else False
    
    def add_type(self, type: TypeContext, id: str):
        """ Add a type, using ``TypeContext``. Used to generate SPIR-V types.
        
            Args:
                type: Type, as ``TypeContext`` to add.
                id: ID to associate with the type.
        """
        self.declared_types[type] = id

    def get_type_id(self, type: TypeContext) -> str:
        """ Get the ID of a given type.

            Args:
                type: Type to get ID for.
            
            Returns:
                ID of the type.
        """
        # FIXME: the type hint declared for this attribute does not use TypeContext as the key.
        #        declared_type_hint suggests to use common.type.DataType as the key!
        return self.declared_types[type]
    
    def get_primative_type_id(self, type: titan_type.DataType) -> str:
        """ Get the ID of a primative type.

            Args:
                type: Primative type to get ID for.

            Return:
                ID of the type.
        """

        # TODO: convoluted? may be a better way to do this
        # can this just be replaced with indexing with the primative type instead of going through TypeContext?
        return self.declared_types[
            self.TypeContext(titan_type.DataType(type))
        ]

    def add_type_if_nonexistant(self, type: TypeContext, id: str) -> str:
        """ Add a type, only if it does not already exist.

            If the type does not already exist, the function will generate the corresponding SPIR-V for it.

            Note: Currently supported types:
                - OpTypeVoid
                - OpTypeInteger (32-bit signed)
                - OpTypeBool
                - OpTypeFloat (32-bit float)

            Args:
                type: The type to add.
                id: The ID to associate with the type.

            Returns:
                type_id: The ID of the type.
        """
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
                        logging.exception(f"no text for storage type for {type.storage_type}", exc_info=False)
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
                        logging.exception(f"type text for {type} not implemented yet (did you wrap the type in a DataType() call to enum?)", exc_info=False)
                        raise Exception(f"type text for {type} not implemented yet (did you wrap the type in a DataType() call to enum?)")
            else:
                logging.exception(f"unable to generate spirv text for type {id} -> {type}", exc_info=False)
                raise Exception(f"unable to generate spirv text for type {id} -> {type}")

            self.add_line(
                self.Sections.TYPES,
                spirv_txt
            )

            return id
        else:
            return self.get_type_id(type)

    # const helpers
    def const_exists(self, const: ConstContext) -> bool:
        """ Check if a constant exists.

            Args:
                const: Constant to check.

            Returns:
                True if constant exists, else False.
        """
        return True if const in self.declared_constants else False

    def add_const(self, c_ctx: ConstContext, spirv_id: str):
        """ Add a constant.

            Args:
                c_ctx: Constant to add.
                spirv_id: The ID to associate with the constant.
        """
        self.declared_constants[c_ctx] = spirv_id

    def add_const_if_nonexistant(self, const: ConstContext, negative_val:bool = False) -> str:
        """ Add a constant, only if it does not exist already.
        
            Checks if the constant exists, and if not, the method will generate the corresponding SPIR-V.

            Args:
                const: Constant to add.
                negative_val: Flag the value as a negative constant. Needed to generate the SPIR-V assembly correctly.

            Returns:
                constant_id: Returns the ID of the constant.
        """

        if const not in self.declared_constants:
            txt_val = str(const.value)
            const_str = f"const_{titan_type.DataType(const.primative_type).name.lower()}"

            # format the string properly
            if negative_val:
                txt_val = txt_val.replace("-", "n")

            if const.primative_type is float:
                txt_val = txt_val.replace(".", "_")

            const_str += f"_{txt_val}"

            self.declared_constants[const] = const_str

            # check if type has been declared
            self.add_type_if_nonexistant(self.TypeContext(titan_type.DataType(const.primative_type)),f"%type_{(titan_type.DataType(const.primative_type).name).lower()}")

            self.add_line(
                self.Sections.VAR_CONST_DECLARATIONS,
                f"%{const_str} = OpConstant {self.get_primative_type_id(titan_type.DataType(const.primative_type))} {const.value}"
            )

            return const_str
        else:
            return self.declared_constants[const]

    # TODO: add one that uses the ConstContext thing directly?
    def get_const_id(self, value, type) -> str:
        """ Get the ID of a constant.
        
            Args:
                value: A constant value.
                type: The type of the constant value.

            Returns:
                ID of the constant.
        """
        temp_c_ctx = self.ConstContext(type, value)
        return self.declared_constants[temp_c_ctx]
    
    def get_const_id_with_ctx(self, context: ConstContext) -> str:
        """ Get the ID of a constant, using ``ConstContext``.

            Args:
                context: Context of the constant.

            Returns:
                ID of the constant.
        """
        return self.declared_constants[context]

class GenerateSPIRVFromAST(ast.NodeVisitor):
    """ Class responsible for generating the SPIR-V assembly, using Python's AST module."""

    def __init__(self, file):
        """ Init function for GenerateSPIRVFromAST.

            Args:
                file: Python source file to transpile.

            Attributes:
                _target_file: Stores the ``file`` parameter. (Should probably be removed.)
                _tree: Stores the AST generated by the AST library whilst parsing the source file.
                spirv_helper: An instance of ``_SPIRVHelperGenerator``.
        """
        self._target_file = file
        self._tree = ast.parse(open(file, "r").read())

        self.spirv_helper = _SPIRVHelperGenerator(disable_debug=False)

    def crawl(self):
        """ Method reponsible for starting the compilation.

            Begins visiting each node and calls corresponding functions to generate SPIR-V assembly.
        """
        # wrapper function for visiting the top of the tree
        self.visit(self._tree)
        self.spirv_helper.dump()

    # TODO: probably inefficient
    def create_file_as_string(self) -> str:
        """ Transforms the generated SPIR-V assembly from lists into a very long string.

            TODO:
                Rework this function. Must be a better way to do this.

            Returns:
                String containing all of the generated SPIR-V assembly code.
        """
        fake_file = ""

        # key=section, value=list of lines
        for lines in self.spirv_helper.generated_spirv.values():
            for line in lines:
                fake_file += f"{line}\n"

        return fake_file
    
    def output_to_file(self, filename:str):
        """ Write generated SPIR-V assembly into a real file.

            Args:
                filename: Name of the file to write to. ``.spvasm`` will be automatically appended.
        """
        ff = self.create_file_as_string()

        with open(f"{filename}.spvasm", "w") as f:
            for line in ff:
                f.write(line)
    
    def _get_python_type_from_string(self, type: str):
        """ Returns the Python type by extracting the string from the type, and evaluating it.
        
            Warning:
                This is probably bad, and should be replaced when possible.

            Args:
                type: Python type as a string, i.e. "<class 'int'>"

            Returns:
                Type as an object.
        """
        # returns python type from <class 'x'> string
        return eval(type.split("'")[0])

    # TODO: can these be turned into enums instead?
    def _return_string_from_type(self, type) -> str:
        """ Returns a string depending on the type() of a variable. 

            Works on int, float and bool. 

            Warning:
                Should be replaced when possible.

            Args:
                type: Returned value of ``type()``.

            Returns:
                Type as a string.

            Raises:
                Exception: Unknown type.
        """

        if (type is int):
            return "int"
        elif (type is float):
            return "float"
        elif (type is bool):
            return "bool"
        else:
            logging.exception(f"unexpected type {type}", exc_info=False)
            raise Exception(f"unexpected type {type}")
        
    def _return_type_from_string(self, type_as_string: str):
        """ Returns the type object when given a string.
        
            Args:
                type_as_string: Type, given as a string.

            Returns:
                Type, as an object.

            Raises:
                Exception: Unknown string.
        """
        """returns a type class depending on the recieved string

        works on int, float and bool, otherwise raises an exception
        """
        if type_as_string == "int":
            return int
        elif type_as_string == "float":
            return float
        elif type_as_string == "bool":
            return bool
        else:
            logging.exception(f"unexpected type as string {type_as_string}", exc_info=False)
            raise Exception(f"unexpected type as string {type_as_string}")




    # ---------- start of AST functions ----------
    # see: https://docs.python.org/3/library/ast.html

    def visit_Module(self, node):
        """ Function called when visiting a module.

            Method first sets the entry point to the name of the function inside the module. If there are multiple,
            the name can either be specified via a command line option, or if present, a function named "step" will
            be the entry point. If there is only one function, then it will be used instead, regardless of the name.

            Some initial boilerplate SPIR-V code is added at this stage.

            After that the method will visit all of the functions in the body, generating the equivalent SPIR-V assembly.
            The ports (I/O or parameters/returns) are handled after the function visits.

            Args:
                node: The current node.

            Attributes:
                _module_contains_step_function (bool): A check if the module contains a function specifically called "step".
            
        """
        _module_contains_step_function = False

        logging.debug(f"found {len(node.body)} functions")

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

            logging.debug(f"exit function {fn.name}")


    
    def visit_FunctionDef(self, node):
        """ Function called when visiting a function definition.

            Method evaluates function signature, generates appropriate SPIR-V types and visits the body nodes.

            Args:
                node: The current node.
        
        """
        logging.debug(f"function {node.name} returns type {node.returns.id} -- {node._fields}")
        self.spirv_helper._latest_function_name = node.name


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
            logging.exception(f"multiple returns/function calls no handled yet", exc_info=False)
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

            
    
        logging.debug(f"body start {node.name}")
        super().generic_visit(node)
        logging.debug(f"body end {node.name}")

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
        """ Function called when performing a function call.

            Warning:
                Work in progress. Will be used to implement decorators, to enable features such as delayed inputs.

            Args:
                node: The current node.
        """
        logging.debug(f"TODO: function calls/decorators properly")
        logging.debug(ast.dump(node))

        if isinstance(node.func, ast.Attribute):
            # logging.debug(f"attribute hit with name {node.func.value.id}.{node.func.attr} with args {node.args}, targeting {self.spirv_helper._latest_function_name}")

            match node.func.attr:
                case "lag":
                    logging.debug(f"lagging decorator found")

                    if len(node.args) != 1:
                        raise Exception(f"unexpected amount of args, wanted 1 got {len(node.args)}")

                    decorator_args = node.args[0] # there should only be one entry, and this should be a list

                    if not isinstance(decorator_args, ast.List):
                        raise Exception(f"expecting list for decorator, got {type(decorator_args)} instead")
                    
                    list_of_inputs_and_lags = decorator_args.elts

                    # {function_name: {
                    #                   input1: 2,
                    #                   input2: 5
                    #                 }
                    # }

                    temp_dict = {}

                    for element in list_of_inputs_and_lags:
                        # still working with ast.Lists here
                        if len(element.elts) != 2:
                            raise Exception(f"unexpected amount of elements, wanted 2 got {len(element.elts)}")
                        
                        target_input = self._extract_content(element.elts[0])
                        target_lag_depth = self._extract_content(element.elts[1])
                        temp_dict[target_input] = target_lag_depth

                    self.spirv_helper._decorator_dict[self.spirv_helper._latest_function_name] = temp_dict
                    logging.debug(f"lagging decorator produced: {self.spirv_helper._decorator_dict}")

                    logging.info(f"Generating JSON (contains lagging information)...")
                    with open(f"{self.spirv_helper._latest_function_name}_lagging_info.json", "w+") as f:
                        f.write(json.dumps(self.spirv_helper._decorator_dict, indent=4))


                case "recursive":
                    raise Exception("TODO")
                case _:
                    raise Exception("unexpected attribute when handling a call")
            


    def visit_Assign(self, node):
        """ Function called when performing an assignment.
        
            Attempts to evaluate the assignment, by calling ``_eval_line()``.

            Args:
                node: The current node.
        """
        if len(node.targets) > 1:
            logging.exception(f"multiple assignments not supported", exc_info=False)
            raise Exception("multiple assignments not supported")

        try:
            eval_id, eval_ctx = self._eval_line_wrap(node)
        except Exception as e:
            logging.exception(f"failed to unpack evaluation, usually a sign that the operation was not handled properly... exception: {e}")
            raise Exception(f"failed to unpack evaluation, usually a sign that the operation was not handled properly... exception: {e}")

        type_class = self._extract_type(eval_ctx)

        if type_class is None:
            logging.exception(f"evaluated type as None for variable with no type declaration", exc_info=False)
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
        try:
            eval_id, eval_ctx = self._eval_line_wrap(node)
        except Exception as e:
            logging.exception(f"failed to unpack evaluation, usually a sign that the operation was not handled properly... exception: {e}")
            raise Exception(f"failed to unpack evaluation, usually a sign that the operation was not handled properly... exception: {e}")


        eval_type = self._extract_type(eval_ctx)

        if eval_type != type_class:
            logging.exception(f"mismatched types: eval_type {eval_type} - type_class {type_class}", exc_info=False)
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
            logging.debug(f"returning const: {node.value.value}")
            logging.exception(f"TODO: return constant value", exc_info=False)
            raise Exception("TODO: return constant value")
        
        elif isinstance(node.value, ast.Name):
            logging.debug(f"returning name: {node.value.id}")
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
            logging.exception(f"TODO implement handling binops for return values", exc_info=False)
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
            logging.exception(f"unhandled type during return node evaluation {node}", exc_info=False)
            raise Exception(f"unhandled type during return node evaluation {node} {type(node)}")


    def visit_Name(self, node): pass

    
    def _get_id_of_node(self, node):
        if isinstance(node, ast.Name):
            if self.spirv_helper.symbol_exists(node.id):
                return node.id
            else:
                logging.exception(f"symbol referenced but does not exist: {node.id}", exc_info=False)
                raise Exception(f"symbol referenced but does not exist: {node.id}")
        elif isinstance(node, ast.Constant):

            c_ctx = self.spirv_helper.ConstContext(titan_type.DataType(type(node.value)), node.value)
            if self.spirv_helper.const_exists(c_ctx):
                return self.spirv_helper.get_const_id_with_ctx(c_ctx)
            else:
                # TODO: does not account for negative numbers, probably need an UnaryOp section 
                c_id = self.spirv_helper.add_const_if_nonexistant(
                    c_ctx, False
                )
                return c_id
            # return self.spirv_helper.get_const_id(node.value, titan_type.DataType(type(node.value)))
        else:
            logging.exception(f"unhandled node {node}", exc_info=False)
            raise Exception(f"unhandled node {node} {type(node)}")

    def visit_IfExp(self, node):
        logging.debug(f"[visit_IfExp] {node} {node._fields}")


        # this should take care of the comparison node
        # --- only if IfExp is visited by this function, and not _eval_line
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
        # also fails to do a > b -- "failed to unpack evaluation, unhandled instance when checking Name object"

        if len(node.ops) > 1:
            # TODO: will probably need recursive function to evaluate all comparisons?
            logging.exception(f"TODO: cannot handle multiple comparisons yet", exc_info=False)
            raise Exception("TODO: cannot handle multiple comparisons yet")

        t_id = self.spirv_helper.add_type_if_nonexistant(
            self.spirv_helper.TypeContext(
                titan_type.DataType.BOOLEAN
            ),
            f"%type_{titan_type.DataType.BOOLEAN.name.lower()}"
        )

        # left_id = None
        # right_id = None
        # opcode = None

        # fails to do 1 > b -- "constant object has no attribute id"
        # TODO: needs typechecking to determine correct type of node
        # target_type = self.spirv_helper.get_symbol_type(node.left.id) # this will need to be changed to whatever object the left operand is

        eval_left_id, left_ctx = self._eval_line(node.left)
        eval_right_id, right_ctx = self._eval_line(node.comparators[0])

        left_type = self._extract_type(left_ctx)
        right_type = self._extract_type(right_ctx)


        # big chance that this will have to get changed since it may cause issues if you're not super specific with types
        if left_type is not right_type:
            logging.exception(f"{errors.TitanErrors.TYPE_MISMATCH.value}, L: {left_type} R: {right_type} ({errors.TitanErrors.TYPE_MISMATCH.name})")
            raise Exception(f"{errors.TitanErrors.TYPE_MISMATCH.value}, L: {left_type} R: {right_type} ({errors.TitanErrors.TYPE_MISMATCH.name})")
        else:
            target_type = left_type
            target_type_id = self.spirv_helper.get_primative_type_id(target_type)


        # handle left node
        if isinstance(node.left, ast.Name):
            # if name, that means symbol, so we have to load it
            load_str = f"temp_{node.left.id}"
            self.spirv_helper.add_line(
                self.spirv_helper.Sections.FUNCTIONS,
                f"%{load_str} = OpLoad {target_type_id} %{node.left.id}"
            )
            eval_left_id = load_str # use updated id

        elif isinstance(node.left, ast.Constant):
            # possibly do nothing, or simply set variables? although we already have info from _eval_line
            pass
        else:
            logging.exception(f"possibly unhandled left node when evaluating comparison: {node.left} {type(node.left)}")
            raise Exception(f"possibly unhandled left node when evaluating comparison: {node.left} {type(node.left)}")


        # handle comparators
        # - at the moment this can only handle 1 comparator, so dont do nesting
        # - might need some recursive function to handle various depths of comparisons i.e. for each comparison, call _eval_line?
        if isinstance(node.comparators[0], ast.Name):
            load_str = f"temp_{node.comparators[0].id}"
            self.spirv_helper.add_line(
                self.spirv_helper.Sections.FUNCTIONS,
                f"%{load_str} = OpLoad {target_type_id} %{node.comparators[0].id}"
            )
            eval_right_id = load_str

        # node.ops contains a list of operators (as ast.LtE, ast.Gt etc etc), we take the zeroth one since atm we can only do 1 comparison
        opcode = self.__return_correct_opcode(target_type, node.ops[0])

        self.spirv_helper.add_intermediate_id(f"titan_id_{self.spirv_helper.intermediate_id}", target_type)
        self.spirv_helper.add_line(
            self.spirv_helper.Sections.FUNCTIONS,
            f"%titan_id_{self.spirv_helper.intermediate_id} = {opcode} {t_id} %{eval_left_id.strip('%')} %{eval_right_id.strip('%')}"
        )

        self.spirv_helper._latest_compare_id = f"%titan_id_{self.spirv_helper.intermediate_id}"
        self.spirv_helper.intermediate_id += 1

    # TODO: figure out exactly what info is needed from here, if any
    def visit_arguments(self, node): pass

    def visit_Constant(self, node): pass

    def generic_visit(self, node):
        logging.debug(f"generic visit {node.__class__.__name__} {node._fields}")

    def _extract_content(self, node):
        """
        returns value if node is ast.Constant, id if node is ast.Name
        """
        
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return node.id
        else:
            logging.exception(f"idk what to do for {type(node)}", exc_info=False)
            raise Exception(f"idk what to do for {type(node)}")


    def _extract_type(self, context):
        """
        attempts to extract the primative type from a given context

        - handles TypeContext, ConstContext, DataType, bool and int
        """
        if isinstance(context, self.spirv_helper.TypeContext):
            return context.primative_type
        elif isinstance(context, self.spirv_helper.ConstContext):
            return context.primative_type
        elif isinstance(context, titan_type.DataType):
            return context.value
        elif context is bool or int:
            return context
        else:
            logging.exception(f"unable to extract type from context - {context} {type(context)}", exc_info=False)
            raise Exception(f"unable to extract type from context - {context} {type(context)}")

    def __return_correct_opcode(self, chosen_type, operation):
        logging.debug(f"determining opcode for {operation} (type: {chosen_type})")

        opcode_dict = {
            (ast.Add, int) : "OpIAdd",
            (ast.Sub, int) : "OpISub",
            (ast.Mult, int) : "OpIMul",
            (ast.Div, int) : "OpSDiv",
            (ast.LShift, int) : "OpShiftLeftLogical",
            (ast.RShift, int) : "OpShiftRightLogical",
            (ast.Eq, int) : "OpIEqual",
            (ast.NotEq, int) : "OpINotEqual",
            (ast.Lt, int) : "OpSLessThan",
            (ast.LtE, int) : "OpSLessThanEqual",
            (ast.Gt, int) : "OpSGreaterThan",
            (ast.GtE, int) : "OpSGreaterThanEqual",

            (ast.Add, float) : "OpFAdd",
            (ast.Sub, float) : "OpFSub",
            (ast.Div, float) : "OpFDiv",
            (ast.Mult, float) : "OpFMult",
            (ast.Eq, float) : "OpFOrdEqual",
            (ast.NotEq, float) : "OpFOrdNotEqual",
            (ast.Lt, float) : "OpFOrdLessThan",
            (ast.LtE, float) : "OpFOrdLessThanEqual",
            (ast.Gt, float) : "OpFOrdGreaterThan",
            (ast.GtE, float) : "OpFOrdGreaterThanEqual"
        }

        try:
            # need __class__ to avoid indexing with object instance
            return opcode_dict[(operation.__class__, chosen_type)]
        except KeyError:
            logging.exception(f"unable to index opcode: ({operation.__class__}, {chosen_type})")
            raise
        except Exception as e:
            logging.exception(f"{e}")
            raise

    def _eval_line(self, node):
        """
        recursively evaluates a line and returns the final line id and line context
        """
        logging.debug(f"evaluating node: {node.__class__}")


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
                logging.exception(f"mismatched types l: {left_type} r: {right_type}", exc_info=False)
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
                logging.exception(f"unable to determine return type (L: {left_type} , R: {right_type})", exc_info=False)
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
            opcode = self.__return_correct_opcode(chosen_type, node.op)
            
            if opcode is None:
                logging.exception(f"opcode was not updated, why? {node.op} {chosen_type} {left_id} {right_id} {left_type} {right_type}", exc_info=False)
                raise Exception(f"opcode was not updated, why? {node.op} {chosen_type} {left_id} {right_id} {left_type} {right_type}")

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
                    logging.exception(f"got unexpected constant value type {type(value)}", exc_info=False)
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

            logging.exception(f"unhandled additional operator in unaryop class {node.op}", exc_info=False)
            raise Exception(f"unhandled additional operator in unaryop class {node.op}")
            # return f"{node.op.__class__.__name__} {node.operand.value} {type(node.operand.value)} ({isinstance(node.op,ast.USub)})"

        elif isinstance(node, ast.Name):
            if not self.spirv_helper.symbol_exists(node.id):
                logging.exception(f"symbol '{node.id}' does not exist", exc_info=False)
                raise Exception(f"symbol '{node.id}' does not exist")

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
        
        elif isinstance(node, ast.IfExp):
            self.visit_IfExp(node)

            # return the context of the comparison node, because that'll indicate the type
            # whereas the the ifexp_selector would only be bool due to the comparison condition
            ctx = self.spirv_helper.get_type_of_intermediate_id(self.spirv_helper._latest_compare_id[1:])
            return self.spirv_helper._latest_ifexp_selector_id, ctx

        
        elif isinstance(node, ast.Compare):
            self.visit_Compare(node)

            ctx = self.spirv_helper.get_type_of_intermediate_id(self.spirv_helper._latest_compare_id[1:])
            return self.spirv_helper._latest_compare_id, ctx

        else:
            logging.exception(f"unexpected {type(node)} to parse in eval_line, probably not implemented yet", exc_info=False)
            raise Exception(f"unexpected {type(node)} to parse in eval_line, probably not implemented yet")

    def _eval_line_wrap(self, node):
        """
        works on ast.Assign or ast.AnnAssign nodes
        """
        
        # this will call _eval_line on various nodes, including IfExp instead of going through visit_IfExp
        # is this going to be an issue?

        if isinstance(node, ast.Assign):
            if len(node.targets) > 1:
                logging.exception(f"multiple assignments not supported", exc_info=False)
                raise Exception("multiple assignments not supported")

            # for target in node.targets:
            target = node.targets[0]
            logging.debug(f"{target.id}")

            evaluated = self._eval_line(node.value)
            logging.debug(f" = {evaluated}")
            return evaluated

        elif isinstance(node, ast.AnnAssign):
            logging.debug(f"{node.target.id}")
            
            evaluated = self._eval_line(node.value)
            logging.debug(f" = {evaluated}")
            return evaluated