from __future__ import annotations

import ast, logging, json
from enum import Enum, auto
from typing import NamedTuple, Union, TypedDict
from bidict import bidict

import compiler.hinting as hinting
from common.type import DataType, StorageType
import common.errors as errors

class SPIRVAssembler(ast.NodeVisitor):
    """ SPIR-V assembler class. """

    class Sections(Enum):
        """ Enum containing sections that are present in the final SPIR-V assembly file.
        
            Dividing the SPIR-V file into sections helps with ensuring that the code is
            placed in the right spot, and can be easily altered if needed.
        """
        CAPABILITY_AND_EXTENSION = auto()
        ENTRY_AND_EXEC_MODES = auto()
        DEBUG_STATEMENTS = auto()
        ANNOTATIONS = auto()
        TYPES = auto()
        VAR_CONST_DECLARATIONS = auto()
        ARRAY_TYPES = auto()
        ARRAY_DECLARATIONS = auto()
        FUNCTIONS = auto()

    class TypeContext(NamedTuple):
        """ Tuple that provides context about a given type. Used to align Python types with SPIR-V.
        
            Attributes:
                primative_type (titan.common.type.DataType): Base/primative (python) type.
                storage_type (titan.common.type.StorageType): Storage type in SPIR-V.
                is_constant (bool): Type describes a constant.
                is_pointer (bool): Type describes a pointer.
                is_function_typedef (bool): Type describes a function definition. 
                is_array (bool): Type describes array.
                array_size (int): Stores size of array.
        """
        primative_type: DataType
        storage_type: StorageType = StorageType.NONE
        is_constant: bool = False
        is_pointer: bool = False
        is_function_typedef: bool = False
        is_array: bool = False
        array_size: int = 0

    class ConstContext(NamedTuple):
        """ Tuple that provides context about a given constant.
        
            Attributes:
                primative_type (titan.common.type.DataType): Base/primative (python) type.
                value: Value of the constant. Can be int, float, bool or None.
                declared_id: SPIR-V ID associated to the particular constant.
        """
        primative_type: DataType
        value: Union[int, float, bool, None]
        declared_id: str = None

    class SymbolInfo(NamedTuple):
        """ Tuple that associates a primative type with a storage location.

            Attributes:
                type (titan.common.type.DataType): Base/primative (python) type.
                location (titan.common.type.StorageType): Storage type in SPIR-V.
                is_array (bool): Is the symbol an array type?
                declared_type_id (str): SPIR-V type ID associated to the particular symbol.
        """
        type: DataType
        location: StorageType
        is_array: bool = False
        declared_type_id: str = None


    class IntermediateIDContext(NamedTuple):
        """ Tuple to store information about an intermediate ID. 
        
            Attributes:
                type: Base/primative type.
                is_accessing_array: Whether the ID is accessing an array or not (i.e represents OpAccessChain).
        """
        type: DataType
        is_accessing_array: bool = False

    class symbol_info_hint(TypedDict):
        symbol_id: str
        info: SPIRVAssembler.SymbolInfo

    class constant_context_and_id(TypedDict):
        type: SPIRVAssembler.ConstContext
        spirv_id: str

    class intermediate_id_and_ctx(TypedDict):
        intermediate_id: str
        id_ctx: SPIRVAssembler.IntermediateIDContext

    # attributes
    entry_point = ""
    _disable_debug = True
    _latest_ifexp_selector_id = None
    _latest_compare_id = None
    _latest_function_name = None
    _decorator_dict = {}
    _import_mapping = bidict()


    input_port_list: symbol_info_hint = {}
    output_port_list: hinting.symbol_and_type = {}
    symbol_info: symbol_info_hint = {}
    declared_constants: constant_context_and_id = {}
    declared_types: hinting.declared_types = {}
    body = []

    # attempts to align the output type list with the output port/symbol list
    # this is so that the correct id (assuming that it is handled in order) will be assigned the correct type
    # perhaps slightly over-engineered?
    _internal_output_port_list_counter = 0 
    output_type_list = []

    location_id = 0
    intermediate_id = 0
    return_id = 0
    intermediate_ids: intermediate_id_and_ctx = {}

    _target_file = None
    _tree = None

    # TODO: remove the .name operators
    generated_spirv = {
        Sections.CAPABILITY_AND_EXTENSION.name: [],
        Sections.ENTRY_AND_EXEC_MODES.name: [],
        Sections.DEBUG_STATEMENTS.name: [],
        Sections.ANNOTATIONS.name: [],
        Sections.TYPES.name: [],
        Sections.VAR_CONST_DECLARATIONS.name: [],
        Sections.ARRAY_TYPES.name: [],
        Sections.ARRAY_DECLARATIONS.name: [],
        Sections.FUNCTIONS.name: []
    }


    def __init__(self, target_file: str, disable_debug=True):
        """ Init function for _SPIRVHelperGenerator.

            Creates various attributes and allows for helper function access.
        
            Args:
                disable_debug (bool): Disable debug output.
                target_file: File to read.

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
                _import_mapping (bidict): Bi-directional dictionary to store import names & aliases
        """

        self._disable_debug = disable_debug
        self._target_file = target_file
        self._tree = ast.parse(open(self._target_file, "r").read())

    def dump(self):
        """ Output debug info if debug flag has been set. Uses the logging library."""
        if not self._disable_debug:

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

    def add_line(self, section: Sections, line: str):
        """ Add a generated line of SPIR-V to a given section.
        
            Args:
                section (titan.compiler.spirv.SPIRVAssembler.Sections): The section to append the line to.
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

    def add_output_symbol(self, symbol: str):
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
                symbol (str): Given symbol name, without the SPIR-V "%" prefix.

            Returns:
                symbol_exists: True if symbol exists, else False.
        """
        return True if symbol in self.symbol_info else False

    # NOTE: unused, no references    
    # def add_symbol(self, symbol_id: str, type, location: StorageType, is_array: bool = False, declared_type_id: str = None):
    #     """ Add a symbol.

    #         The value ``type`` arg will be automatically converted into a valid ``titan.common.type.DataType`` value.
        
    #         Args:
    #             symbol_id: ID given to the symbol.
    #             type: Python type of the symbol.
    #             location: Given storage location for the symbol. Required for SPIR-V.
    #             is_array: Is the symbol an array?
    #             declared_id: SPIR-V ID of the type associated with the particular symbol.

    #         TODO:
    #             Need to determine whether the symbol ID contains the "%" prefix or not.
    #     """
    #     self.symbol_info[symbol_id] = self.SymbolInfo(DataType(type), location, is_array, declared_type_id)

    def get_symbol_info(self, symbol_id: str) -> SymbolInfo:
        """ Get information regarding a given symbol via ID.

            Args:
                symbol_id: ID of the symbol to check.

            Returns:
                Symbol information tuple.
        """
        return self.symbol_info[symbol_id]
    
    # basically works the same as add_symbol
    def update_symbol_info(self, symbol_id: str, info: SymbolInfo):
        """ Update the information currently stored of a given symbol.

            Warning:
                Simply overwrites an existing entry. The symbol _must_ have been declared before using this,
                otherwise you may run into a KeyError exception.

            Args:
                symbol_id: ID of the symbol to update.
                info: Tuple to update the information with.
        """
        self.symbol_info[symbol_id] = info

    def add_symbol_if_nonexistant(self, symbol: str, type, location: StorageType, array_type_id: str = None, array_size: int = 0) -> bool:
        """ Add a symbol, only if it does not already exist.

            Method first checks if symbol exists or not. If not, it'll generate the corresponding SPIR-V
            lines depending on its type and location, and increment the ``location_id`` counter.

            Args:
                symbol: Name of the symbol to add.
                type: Python type of the symbol.
                location: Given storage location for the symbol. Required for SPIR-V.
                array_type_id: SPIR-V ID (with %) of the array type.
                array_size: Total elements present in the array.

            Returns:
                symbol_added: True if symbol has been added, else False.
        """

        symbol_is_array = False if array_type_id is None else True

        if symbol not in self.symbol_info:
            logging.debug(f"updating symbol: {symbol}")
            
            # keeping track of which id is used to create the symbol
            final_type_id = None
            
            self.add_line(self.Sections.DEBUG_STATEMENTS, f"OpName %{symbol} \"{symbol}\"")

            # if i/o
            if location is (StorageType.IN or StorageType.OUT):
                # add location (glsl specific i think)
                self.add_line(self.Sections.ANNOTATIONS, f"OpDecorate %{symbol} Location {self.location_id}")

                if location is StorageType.IN:
                    # more glsl specific stuff
                    self.add_line(self.Sections.ANNOTATIONS, f"OpDecorate %{symbol} Flat")

                    # input variable pointer type
                    ptr_id = self.add_type_if_nonexistant(
                        self.TypeContext(primative_type=DataType(type), storage_type=StorageType.IN, is_pointer=True),
                        f"%pointer_input_{DataType(type).name.lower()}"
                    )


                    if symbol_is_array:
                        self.add_line(self.Sections.VAR_CONST_DECLARATIONS, f"%{symbol} = OpVariable {array_type_id} Input")
                        final_type_id = array_type_id

                    else:
                        self.add_line(self.Sections.VAR_CONST_DECLARATIONS, f"%{symbol} = OpVariable {ptr_id} Input")
                        final_type_id = ptr_id


                elif location is StorageType.OUT:

                    ptr_id = self.add_type_if_nonexistant(
                        self.TypeContext(primative_type=DataType(type), storage_type=StorageType.IN, is_pointer=True),
                        f"%pointer_output_{DataType(type).name.lower()}"
                    )

                    if symbol_is_array:
                        self.add_line(self.Sections.VAR_CONST_DECLARATIONS, f"%{symbol} = OpVariable {array_type_id} Output")
                        final_type_id = array_type_id
                    else:
                        self.add_line(self.Sections.VAR_CONST_DECLARATIONS, f"%{symbol} = OpVariable {ptr_id} Output")
                        final_type_id = ptr_id
                        

                    
            elif location is StorageType.FUNCTION_VAR:
            
                ptr_id = self.add_type_if_nonexistant(
                    self.TypeContext(
                        primative_type=DataType(type), storage_type=StorageType.FUNCTION_VAR, is_pointer=True),
                    f"%pointer_funcvar_{DataType(type).name.lower()}"
                )
                
                if symbol_is_array:
                    self.add_line(self.Sections.FUNCTIONS, f"%{symbol} = OpVariable {array_type_id} Function")
                    final_type_id = array_type_id
                else:
                    self.add_line(self.Sections.FUNCTIONS, f"%{symbol} = OpVariable {ptr_id} Function")
                    final_type_id = ptr_id

            # increment by 1 for regular variables, or by element count for arrays
            self.location_id += 1 if not symbol_is_array else array_size

            symbol_info = self.SymbolInfo(DataType(type), location, is_array=symbol_is_array, declared_type_id=final_type_id)
            logging.debug(f"{symbol} : {symbol_info}")
            self.symbol_info[symbol] = symbol_info
            return True
        else:
            return False
        
    def get_symbol_type(self, symbol: str) -> DataType:
        """ Get symbol type, using symbol ID.

            Args:
                symbol: Symbol ID
            
            Returns:
                Primative type of symbol.
        """
        # symbol_info[symbol] -> info (SymbolInfo).type
        return self.symbol_info[symbol].type

    # NOTE: unused, no references
    # def get_symbol_declared_type_id(self, symbol: str) -> str:
    #     """ Get the ID of the type that was used to declare the symbol with.
        
    #         Args:
    #             symbol: Symbol ID

    #         Returns:
    #             Type ID
    #     """
    #     return self.symbol_info[symbol].declared_type_id

    def intermediate_id_exists(self, intermediate_id: str) -> bool:
        """ Check if an intermediate ID already exists.
        
            Args:
                intermediate_id: Intermediate ID to check.
            
            Returns:
                True if intermediate ID already exists, else False.
        """
        return True if intermediate_id in self.intermediate_ids else False
    
    def add_intermediate_id(self, intermediate_id: str, type: DataType, is_accessing_array: bool = False):
        """ Add an intermediate ID.

            Args:
                intermediate_id: Intermediate ID to add.
                type: Type to associate with the intermediate ID.
        """
        # self.intermediate_ids[intermediate_id] = type
        self.intermediate_ids[intermediate_id] = self.IntermediateIDContext(type, is_accessing_array)

    def get_type_of_intermediate_id(self, intermediate_id: str) -> DataType:
        """ Returns the type of an intermediate ID, _not_ the type ID.

            Args:
                intermediate_id: Intermediate ID to return the type of.

            Returns:
                Primative intermediate ID type.
        """
        return self.intermediate_ids[intermediate_id].type

    def get_is_intermediate_id_accessing_array(self, intermediate_id: str) -> bool:
        """ Returns true/false if intermediate ID is accessing an array.
        
            Args:
                intermediate_id: Intermediate ID to check

            Returns:
                True if accessing array, else False
        """
        return self.intermediate_ids[intermediate_id].is_accessing_array
    
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
    
    def get_primative_type_id(self, type: DataType) -> str:
        """ Get the ID of a primative type.

            Args:
                type: Primative type to get ID for.

            Return:
                ID of the type.
        """

        # TODO: convoluted? may be a better way to do this
        # can this just be replaced with indexing with the primative type instead of going through TypeContext?
        return self.declared_types[
            self.TypeContext(DataType(type))
        ]
    
    def add_type_if_nonexistant(self, type_ctx: TypeContext, id: str) -> str:
        """ Add a type, only if it does not already exist.

            If the type does not already exist, the function will generate the corresponding SPIR-V for it.

            Note: Currently supported types:
                - OpTypeVoid
                - OpTypeInteger (32-bit signed)
                - OpTypeBool
                - OpTypeFloat (32-bit float)
                - OpTypeArray

            Args:
                type: The type to add.
                id: The ID to associate with the type.

            Returns:
                type_id: The ID of the type.
        """
        if not self.type_exists(type_ctx):
            
            # TODO: remove
            self.add_type(type_ctx, id)

            spirv_txt = f"{id} = "

            if type_ctx.is_function_typedef:
                prim_tid = self.get_primative_type_id(type_ctx.primative_type)
                spirv_txt += f"OpTypeFunction {prim_tid}"

            elif type_ctx.is_pointer and not type_ctx.is_array:
                prim_tid = self.get_primative_type_id(type_ctx.primative_type)
                storage_type_str = type_ctx.storage_type.value

                assert type(storage_type_str) is str, f"did not get text for the storage type: {type_ctx.storage_type}"

                spirv_txt += f"OpTypePointer {storage_type_str} {prim_tid}"

            elif type_ctx.is_array and not type_ctx.is_pointer:
                prim_tid = self.get_primative_type_id(type_ctx.primative_type)

                # get id for array size, may need to add if doesnt exist
                const_size_id = self.add_const_if_nonexistant(
                    self.ConstContext(
                        type_ctx.primative_type,
                        type_ctx.array_size
                    )
                )

                spirv_txt += f"OpTypeArray {prim_tid} %{const_size_id}"

            elif type_ctx.is_array and type_ctx.is_pointer:
                
                # get base array id for this specific pointer
                array_type_id = self.get_type_id(
                    self.TypeContext(
                        primative_type=type_ctx.primative_type,
                        storage_type=StorageType.NONE, # the base array id does not have storage type
                        is_pointer=False,
                        is_array=True,
                        array_size=type_ctx.array_size
                    )
                )

                spirv_txt += f"OpTypePointer {type_ctx.storage_type.value} {array_type_id}"

            # this should mean we're working with the primative types
            elif (not type_ctx.is_constant) and (not type_ctx.is_pointer) and (not type_ctx.is_function_typedef):

                match type_ctx.primative_type:
                    case DataType.VOID:
                        spirv_txt += f"OpTypeVoid"
                    case DataType.INTEGER:
                        spirv_txt += f"OpTypeInt 32 1"
                    case DataType.BOOLEAN:
                        spirv_txt += f"OpTypeBool"
                    case DataType.FLOAT:
                        spirv_txt += f"OpTypeFloat 32"
                    case _:
                        logging.exception(f"type text for {type_ctx} not implemented yet (did you wrap the type in a DataType() call to enum?)", exc_info=False)
                        raise Exception(f"type text for {type_ctx} not implemented yet (did you wrap the type in a DataType() call to enum?)")
            else:
                logging.exception(f"unable to generate spirv text for type {id} -> {type_ctx}", exc_info=False)
                raise Exception(f"unable to generate spirv text for type {id} -> {type_ctx}")


            if not type_ctx.is_array:
                self.add_line(
                    self.Sections.TYPES,
                    spirv_txt
            )
            else:
                self.add_line(
                    self.Sections.ARRAY_TYPES,
                    spirv_txt
                )

            return id
        else:
            return self.get_type_id(type_ctx)
        
    # const helpers
    def const_exists(self, const: ConstContext | str) -> bool:
        """ Check if a constant exists.

            Args:
                const: Constant to check, either with ConstContext or ID (without '%')

            Returns:
                True if constant exists, else False.
        """
        return const in self.declared_constants.keys() or const in self.declared_constants.values()

    # NOTE: unused, no references    
    # def add_const(self, c_ctx: ConstContext, spirv_id: str):
    #     """ Add a constant.

    #         Args:
    #             c_ctx: Constant to add.
    #             spirv_id: The ID to associate with the constant.
    #     """
    #     self.declared_constants[c_ctx] = spirv_id

    def add_const_if_nonexistant(self, const: ConstContext, negative_val: bool = False) -> str:
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
            const_str = f"const_{DataType(const.primative_type).name.lower()}"

            # format the string properly
            if negative_val:
                txt_val = txt_val.replace("-", "n")

            if const.primative_type is float:
                txt_val = txt_val.replace(".", "_")

            const_str += f"_{txt_val}"

            self.declared_constants[const] = const_str

            # check if type has been declared
            self.add_type_if_nonexistant(self.TypeContext(DataType(const.primative_type)),f"%type_{(DataType(const.primative_type).name).lower()}")

            self.add_line(
                self.Sections.VAR_CONST_DECLARATIONS,
                f"%{const_str} = OpConstant {self.get_primative_type_id(DataType(const.primative_type))} {const.value}"
            )

            return const_str
        else:
            return self.declared_constants[const]
        
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

    def get_new_intermediate_id(self) -> str:
        """ Gets intermediate ID string and increments the counter.
        
            Returns:
                A (hopefully) unused intermediate ID value.
        """
        new_id = f"titan_id_{self.intermediate_id}"
        self.intermediate_id += 1
        return new_id

    def add_temp_load_op_if_needed(self, id: str, type_id: str) -> str:
        """ Add an OpLoad into a temporary ID if the symbol already exists, or if dealing with arrays (TODO).
        
            Required by SPIR-V syntax.

            Args:
                id: ID of the symbol.
                type_id: ID of the type of the symbol.

            Returns:
                Returns the new temporary ID if the symbol exists, otherwise returns provided symbol_id.
        """

        # if id is a symbol
        if self.symbol_exists(id):
            temp_id = f"temp_{id}"

            self.add_line(
                self.Sections.FUNCTIONS,
                f"%{temp_id} = OpLoad {type_id} %{id}"
            )

            return temp_id
        
        # if constant -- no need to load anything, can use directly
        elif self.const_exists(id.strip("%")):
            return id

        # not a symbol, and not an intermediate id..? what does this line do?
        elif (not self.symbol_exists(id) and not self.intermediate_id_exists(id)) or self.get_is_intermediate_id_accessing_array(id):

            temp_id = self.get_new_intermediate_id()
            self.add_line(
                self.Sections.FUNCTIONS,
                f"%{temp_id} = OpLoad {type_id} %{id}"
            )

            return temp_id
        else:
            return id
        

    ### ast related stuff here
    
    def compile(self):
        """ Begin the AST/Python -> SPIR-V compilation. """
        self.visit(self._tree)

        if not self._disable_debug:
            self.dump()

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
        for lines in self.generated_spirv.values():
            for line in lines:
                fake_file += f"{line}\n"

        return fake_file
    
    def output_to_file(self, filename:str):
        """ Write generated SPIR-V assembly into a real file.

            Args:
                filename: Name of the file to write to. ``.spvasm`` will be automatically appended.
        """
        ff = self.create_file_as_string()

        with open(f"output/{filename}.spvasm", "w") as f:
            for line in ff:
                f.write(line)

    # dont look at this
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
            # skip over imports in module definition
            if node is ast.Import or ast.ImportFrom:
                continue

            if node.body[i].name == "step":
                _module_contains_step_function = True
                self.entry_point = "step"

        if not _module_contains_step_function:
            total_func_defs = 0
            func_def_pos = 0

            for i in range(len(node.body)):
                operation = node.body[i]

                if type(operation) is ast.FunctionDef:
                    total_func_defs += 1
                    func_def_pos = i
            

            assert total_func_defs != 0, "no function defintions found"
            assert not total_func_defs > 1, "multiple function defintions found, please specify top"
            
            self.entry_point = node.body[func_def_pos].name
            logging.debug(f"setting entry point as '{self.entry_point}'")

        # spirv boilerplate
        self.add_line(
            self.Sections.CAPABILITY_AND_EXTENSION,
            f"OpCapability Shader"
        )

        self.add_line(
            self.Sections.CAPABILITY_AND_EXTENSION,
            f"OpMemoryModel Logical GLSL450"
        )

        # this makes the assumption that the module body only contains FunctionDef nodes
        # may not always be the case...
        # TODO: rename 'fn', misleading
        for fn in node.body:
            
            # deal with imports
            if type(fn) is ast.Import:
                self.visit_Import(fn)
                continue
            elif type(fn) is ast.ImportFrom:
                self.visit_ImportFrom(fn)
                continue

            # ignore everything else
            elif type(fn) is not ast.FunctionDef:
                logging.debug(f"not processing {type(fn)}")
                continue

            # evaluate function signature
            self.visit_FunctionDef(fn)

            # if the function is our entry point, we want to capture its params
            # TODO: this will fail if the entry point is not the first function in the list,
            #       since the lists/dicts will contain previous function entries, messing with the names
            if fn.name == self.entry_point:
                # take contents of input/output ports and convert them into ids
                ports_str = ""

                for symbol, symbol_ctx in self.symbol_info.items():
                    if (symbol_ctx.location is StorageType.IN) or (symbol_ctx.location is StorageType.OUT):
                        ports_str += f"%{symbol} "

                self.add_line(
                    self.Sections.ENTRY_AND_EXEC_MODES,
                    f"OpEntryPoint Fragment %{fn.name} \"{fn.name}\" {ports_str}"
                )

            self.add_line(
                self.Sections.ENTRY_AND_EXEC_MODES,
                f"OpExecutionMode %{fn.name} OriginUpperLeft"
            )

            logging.debug(f"exit function {fn.name}")


    def visit_Import(self, node):
        """ Function called when visiting import nodes.
        
            Updates an internal attribute to keep track of imported modules, as names only.
            Does not actually evaluate if module exists, only intended to work with Numpy for arrays.
        """

        for imported_module in node.names:
            # cant use hasattr() because it will always return true, check against None instead
            if imported_module.asname is None:
                # no alternative name given
                self._import_mapping[imported_module.name] = imported_module.name
            else:
                self._import_mapping[imported_module.name] = imported_module.asname
       
    def visit_ImportFrom(self, node):
        """ Function called when visiting import from 'x' nodes. 

            Does not implement any functionality.
        """
        logging.error(f"importing directly from modules not supported: {ast.dump(node)}")

    def visit_FunctionDef(self, node):
        """ Function called when visiting a function definition.

            Method evaluates function signature, generates appropriate SPIR-V types and visits the body nodes.

            Args:
                node: The current node.
        
        """

        _debug_returns = None
        if hasattr(node, "returns"):
            _debug_returns = f"returns type {node.returns.id}"
        else:
            _debug_returns = "does not hint at returning anything"
            logging.info(f"'{node.name}' does not have a return type hint - is this expected?")

        logging.debug(f"function {node.name} {_debug_returns}")
        self._latest_function_name = node.name

        self.add_line(self.Sections.DEBUG_STATEMENTS, f"OpName %{node.name} \"{node.name}\"")

        void_ctx = self.TypeContext(DataType.VOID, StorageType.NONE)
        t_void_id = self.add_type_if_nonexistant(void_ctx, f"%type_void")

        # make spirv function def for OpTypeFunction
        fn_ctx = self.TypeContext(DataType.VOID, StorageType.NONE, False, False, True)
        t_fn_void_id = self.add_type_if_nonexistant(fn_ctx, f"%type_function_{(DataType.VOID.name).lower()}")

        # mark start of function
        self.add_line(self.Sections.FUNCTIONS, f"%{node.name} = OpFunction {t_void_id} None {t_fn_void_id}")
        self.add_line(self.Sections.FUNCTIONS, f"%label_{node.name} = OpLabel")

        # process decorators - this should handle array defs etc
        # TODO: can this be replaced with a specialised function, as to free up the visit_Call function?
        for decorator in node.decorator_list:
            self.visit_Call(decorator)

        # iterate through each arg, make type & pointer type
        for args in node.args.args:

            # args.arg == argument name
            # args.annotation == type annotation
            #   - seems like python types are recognised as "ast.Name"

            if type(args.annotation) is ast.Name:
                # potentially bad
                type_class = eval(args.annotation.id)

                # TODO: update true/false for arrays?
                # check if generic type exists
                t_ctx = self.TypeContext(DataType(type_class), StorageType.NONE, False, False)
                self.add_type_if_nonexistant(t_ctx, f"%type_{(DataType(type_class).name).lower()}")

                # dealing with args means that a special type needs to be made
                ptr_t_ctx = self.TypeContext(DataType(type_class), StorageType.IN, False, True)
                self.add_type_if_nonexistant(ptr_t_ctx, f"%pointer_input_{(DataType(type_class).name).lower()}")

                self.add_symbol_if_nonexistant(args.arg, type_class, StorageType.IN)

            elif type(args.annotation) is ast.Attribute:
                logging.debug(f"not doing anything for arg {args.arg} as annotation was ast.Attribute")
                pass
            else:
                raise Exception(f"unexpected type of annotation for argument: {type(args.annotation)}")


        # TODO: needs implementation for multiple returns
        # handle returns (types for now)
        assert not isinstance(node.returns, ast.Call), "multiple returns/function calls not handled"

        if isinstance(node.returns, ast.Name):
            type_class = self._get_python_type_from_string(node.returns.id)
            self.add_output_type(type_class)

            type_as_string = DataType(type_class).name.lower()

            # add primative type if it does not exist
            self.add_type_if_nonexistant(self.TypeContext(DataType(type_class)), f"%type_{type_as_string}")

            # add pointer type if it does not exist
            self.add_type_if_nonexistant(self.TypeContext(DataType(type_class), StorageType.OUT, False, True, False),
                f"%pointer_output_{type_as_string}"
            )

            
    
        logging.debug(f"body start {node.name}")
        super().generic_visit(node)
        logging.debug(f"body end {node.name}")

        # spirv boilerplate for end of function
        self.add_line(
            self.Sections.FUNCTIONS,
            f"OpReturn"
        )

        self.add_line(
            self.Sections.FUNCTIONS,
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
                    assert len(node.args) == 1, f"unexpected amount of args, wanted 1 but got {len(node.args)}"

                    decorator_args = node.args[0] # there should only be one entry, and this should be a list
                    assert isinstance(decorator_args, ast.List), f"expecting list for decorator, got {type(decorator_args)} instead"
                    
                    list_of_inputs_and_lags = decorator_args.elts

                    # {function_name: {
                    #                   input1: 2,
                    #                   input2: 5
                    #                 }
                    # }

                    temp_dict = {}

                    for element in list_of_inputs_and_lags:
                        # still working with ast.Lists here
                        assert len(element.elts) == 2, f"unexpected amount for elements, wanted 2 but got {len(element.elts)} instead"
                        
                        target_input = self._extract_content(element.elts[0])
                        target_lag_depth = self._extract_content(element.elts[1])
                        temp_dict[target_input] = target_lag_depth

                    self._decorator_dict[self._latest_function_name] = temp_dict
                    logging.debug(f"lagging decorator produced: {self._decorator_dict}")

                    logging.info(f"Generating JSON (contains lagging information)...")
                    with open(f"{self._latest_function_name}_lagging_info.json", "w+") as f:
                        f.write(json.dumps(self._decorator_dict, indent=4))


                case "recursive":
                    raise Exception("TODO")
                
                case "arraydefs":
                    # format example:
                    # @titan.arraydefs(
                    #   {
                    #       "a": [3, int],
                    #       "b": [(3, 2), float]
                    #   }
                    # )
                    # expecting dictionary that contains the symbols as keys, and their type def as values
                    #   - the dimensions can either be int, or tuple of ints
                    #   - the second value in list must be a python base type

                    assert len(node.args) == 1, f"unexpected number of arguments, wanted 1 but got {len(node.args)}"
                    assert type(node.args[0]) == ast.Dict, f"expected dict for arg, got {type(node.args[0])} instead"

                    dict_keys = node.args[0].keys
                    dict_vals = node.args[0].values

                    for key, value in zip(dict_keys, dict_vals):
                        assert type(key.value) == str, f"expected str for symbol, got {type(key.value)} instead"
                        array_symbol = key.value

                        # this is the dictionary value part
                        assert type(value) == ast.List, f"expected list for array definition, got {type(value)} instead"
                        assert type(value.elts[0]) in [ast.Constant, ast.Tuple], f"unexpected element type, wanted either constant or tuple but got {type(value.elts[0])}"
                        assert type(value.elts[0]) == ast.Constant, f"TODO: tuple support for array defs"

                        array_shape = value.elts[0].value
                        # assuming that its still int, size must be > 1 -- will need to be updated when implementing tuples
                        assert array_shape > 1, f"cannot define array with size less than or equal to 1, got but {array_shape}"

                        assert eval(value.elts[1].id) in [int, float, bool], f"attmpted to evaluate type given '{value.elts[1].id}' but failed. allowed types are int, float, bool"
                        array_type = eval(value.elts[1].id)

                        logging.debug(f"creating array with symbol '{array_symbol}', shape: {array_shape}, type: {array_type}")

                        # init primative types
                        primative_type_id = self.add_type_if_nonexistant(self.TypeContext(primative_type=DataType(array_type)), f"%type_{DataType(array_type).name.lower()}")

                        if type(array_shape) is int:
                            self.add_const_if_nonexistant(
                                self.ConstContext(
                                    primative_type=DataType(type(array_shape)), value=array_shape
                                )
                            )
                        else:
                            raise Exception("unexpected type")

                        t_ctx_array = self.TypeContext(
                            primative_type=DataType(array_type), is_array=True, array_size=array_shape
                        )
                        
                        t_id_array = self.add_type_if_nonexistant(t_ctx_array, f"%array_{DataType(array_type).name.lower()}_{array_shape}")

                        t_ctx_array_ptr = self.TypeContext(
                            primative_type=DataType(array_type), storage_type=StorageType.IN, is_pointer=True,
                            is_array=True, array_size=array_shape
                        )

                        t_id_array_ptr = self.add_type_if_nonexistant(t_ctx_array_ptr, f"%array_ptr_{DataType(array_type).name.lower()}_{array_shape}_{StorageType.IN.value.lower()}")
                        self.add_symbol_if_nonexistant(array_symbol, array_type, StorageType.IN, t_id_array_ptr, array_shape)

                case _:
                    raise Exception("unexpected attribute when handling a call")
                
    def visit_Assign(self, node):
        """ Function called when performing an assignment.
        
            Attempts to evaluate the assignment, by calling ``_eval_line()``.

            Args:
                node: The current node.
        """

        assert len(node.targets) == 1, "multiple assignments not supported"


        # special case: array initialisation
        # will deal within _eval_line() instead
        if isinstance(node.value, ast.Call):
            eval_id, eval_ctx = self._eval_line_wrap(node)
            return
        
        # special case: array indexing, if the target is array then we are doing "x[1] = b"
        elif isinstance(node.targets[0], ast.Subscript):
            index_id, index_ctx = self._eval_line(node.value)
            access_id, access_ctx = self._eval_line(node.targets[0])
            value_temp_load_id = self.add_temp_load_op_if_needed(index_id, index_ctx.primative_type)

            self.add_line(
                self.Sections.FUNCTIONS,
                f"OpStore %{access_id.strip('%')} %{value_temp_load_id.strip('%')}"
            )
            return        

        # if node.value contains a subscript object, it means we're doing something like "b = x[1]"
        elif isinstance(node.value, ast.Subscript):

            # evaluate array access
            access_id, access_ctx = self._eval_line(node.value)

            # make symbol if non-existant
            self.add_symbol_if_nonexistant(node.targets[0].id, access_ctx.primative_type.value, StorageType.FUNCTION_VAR)

            # add opload for array
            temp_load_id = self.add_temp_load_op_if_needed(access_id, self.get_primative_type_id(self.get_type_of_intermediate_id(access_id)))

            # store
            self.add_line(
                self.Sections.FUNCTIONS,
                f"OpStore %{node.targets[0].id} %{temp_load_id}"
            )

            return
        
        # for all other things
        else:
            try:
                eval_id, eval_ctx = self._eval_line_wrap(node)
            except Exception as e:
                logging.exception(f"failed to unpack evaluation, usually a sign that the operation was not handled properly... exception: {e}")
                raise Exception(f"failed to unpack evaluation, usually a sign that the operation was not handled properly... exception: {e}")

            type_class = self._extract_type(eval_ctx)
            assert not type_class is None, f"evaluated type as None for variable with no type declaration"
            
            t_id = self.add_type_if_nonexistant(
                self.TypeContext(
                    DataType(type_class)
                ),
                f"%type_{DataType(type_class).name.lower()}"
            )

            self.add_symbol_if_nonexistant(node.targets[0].id, type_class, StorageType.FUNCTION_VAR)

            self.add_line(
                self.Sections.FUNCTIONS,
                f"OpStore %{node.targets[0].id} %{eval_id.strip('%')}"
            )

    def visit_AnnAssign(self, node):
        # print(f"{node.annotation.id} {node.target.id} = {node.value.value}")
        type_class = self._get_python_type_from_string(node.annotation.id)

        t_id = self.add_type_if_nonexistant(
            self.TypeContext(DataType(type_class)),
            f"%type_{DataType(type_class).name.lower()}"
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

        self.add_symbol_if_nonexistant(node.target.id, type_class, StorageType.FUNCTION_VAR)

        self.add_line(
            self.Sections.FUNCTIONS,
            f"OpStore %{node.target.id} {eval_id}"
        )  

    def visit_Return(self, node):
        """ Handle return nodes. """

        # TODO: add calls to _eval_line to get proper id for node
        # if isinstance(node.value, ast.Constant):
            # logging.debug(f"returning const: {node.value.value}")
            # logging.exception(f"TODO: return constant value", exc_info=False)
            # raise Exception("TODO: return constant value")
        
        assert not isinstance(node.value, ast.Constant), f"TODO: return constant values (returning {node.value.value})"
        assert not isinstance(node.value, ast.BinOp), f"TODO: return binops"

        if isinstance(node.value, ast.Name):
            logging.debug(f"returning name: {node.value.id}")
            id, ctx = self._eval_line(node.value)

            if self.symbol_exists(id):
                s_info = self.get_symbol_info(id)

                # because the symbol exists, and isn't a temporary one
                # and if we're returning it, it must be an output
                if s_info.location == StorageType.FUNCTION_VAR:
                    s_info_new = self.SymbolInfo(
                        ctx, StorageType.OUT, s_info.is_array
                    )

                    self.update_symbol_info(id, s_info_new)

                    ptr_t_id = self.get_type_id(
                        self.TypeContext(
                            ctx, StorageType.FUNCTION_VAR, False, True
                        )
                    )

                    ptr_t_out_id = self.get_type_id(
                        self.TypeContext(
                            ctx, StorageType.OUT, False, True
                        )
                    )

                    self.add_line(
                        self.Sections.VAR_CONST_DECLARATIONS,
                        f"%{id} = OpVariable {ptr_t_out_id} Output"
                    )

                    str_to_match = f"%{id} = OpVariable {ptr_t_id} Function"
                    
                    # TODO: implement better method
                    # bruteforce remove reference of symbol declaration in FUNCTIONS section
                    i = 0
                    for line in self.generated_spirv[self.Sections.FUNCTIONS.name]:
                        if line == str_to_match:
                            self.generated_spirv[self.Sections.FUNCTIONS.name].pop(i)
                            break
                        i += 1

        elif isinstance(node.value, ast.IfExp):

            #        v node.value.body.id
            # return c if a > 0 else 0 
            #             ^ ^        ^ node.value.orelse
            #             | | node.value.test.{ops|comparators}
            #             | node.value.test.left

            # TODO: need to get ID somehow, move the IfExp function to something else accessible and call it directly?
            super().generic_visit(node)

            # because this is direct return, we have to make a temp symbol into which we can return (in spirv terms)
            # we have to also add it to the symbols list, making sure that it has the same type as the indicated return type
            # and that it doesn't clash with the return type

            out_str_id = f"titan_return_id_{self.return_id}"
            self.return_id += 1
            # TODO: make sure names don't clash?
            self.add_symbol_if_nonexistant(
                out_str_id, self.output_type_list[0], StorageType.OUT
            )

            self.add_output_symbol(out_str_id)

            # store titan_id_x into the newly created return variable
            self.add_line(
                self.Sections.FUNCTIONS,
                f"OpStore %{out_str_id} %{self._latest_ifexp_selector_id}"
            )

            ptr_t_out_ctx = self.TypeContext(
                DataType(self.output_type_list[0]), StorageType.OUT,
                False, True, False
            )

            ptr_t_out_id = self.get_type_id(ptr_t_out_ctx)

            self.add_line(
                self.Sections.VAR_CONST_DECLARATIONS,
                f"%{out_str_id} = OpVariable %{ptr_t_out_id.strip('%')} Output"
            )
            

            # print(f"return {node.value.body.id} if {node.value.test.left.id} {node.value.test.ops[0].__class__.__name__} {self._extract_content(node.value.test.comparators[0])} else {self._extract_content(node.value.orelse)}")
        # elif isinstance(node.value, ast.BinOp):
            # logging.exception(f"TODO implement handling binops for return values", exc_info=False)
            # raise Exception("TODO implement handling binops for return values")

            # id, ctx = self._eval_line(node.value)
            # print(f"returning binop val ({id})")

            # if self.symbol_exists(id):
            #     print("this was a symbol")
            # elif self.intermediate_id_exists(id):
            #     print("this was a temp id")
            # else:
            #     raise Exception("idk")

        else:
            logging.exception(f"unhandled type during return node evaluation {node}", exc_info=False)
            raise Exception(f"unhandled type during return node evaluation {node} {type(node)}")


    def visit_Name(self, node): pass

    def _get_id_of_node(self, node):
        if isinstance(node, ast.Name):
            if self.symbol_exists(node.id):
                return node.id
            else:
                logging.exception(f"symbol referenced but does not exist: {node.id}", exc_info=False)
                raise Exception(f"symbol referenced but does not exist: {node.id}")
        elif isinstance(node, ast.Constant):

            c_ctx = self.ConstContext(DataType(type(node.value)), node.value)
            if self.const_exists(c_ctx):
                return self.get_const_id_with_ctx(c_ctx)
            else:
                # TODO: does not account for negative numbers, probably need an UnaryOp section 
                c_id = self.add_const_if_nonexistant(
                    c_ctx, False
                )
                return c_id
            # return self.spirv_helper.get_const_id(node.value, titan_type.DataType(type(node.value)))
        else:
            logging.exception(f"unhandled node {node}", exc_info=False)
            raise Exception(f"unhandled node {node} {type(node)}")

    def visit_IfExp(self, node):
        logging.debug(f"{node} {node._fields}")


        # this should take care of the comparison node
        # --- only if IfExp is visited by this function, and not _eval_line
        super().generic_visit(node)

        # TODO: probably should check if both types match, but as a hack we check only the left one and pray
        t_id = self.get_primative_type_id(self.get_symbol_type(node.test.left.id))

        body_id = self._get_id_of_node(node.body)
        orelse_id = self._get_id_of_node(node.orelse)

        intermediate_id = self.get_new_intermediate_id()

        self.add_line(
            self.Sections.FUNCTIONS,
            #TODO:                                                              vvv should this just be always -1 of the current id?
            f"%{intermediate_id} = OpSelect {t_id} {self._latest_compare_id} %{body_id} %{orelse_id}"
        )

        # add id and set it as latest
        self.add_intermediate_id(f"{intermediate_id}", DataType.BOOLEAN)
        self._latest_ifexp_selector_id = intermediate_id

    # comparison only, do not need to worry about the "orelse" value
    def visit_Compare(self, node):
        # also fails to do a > b -- "failed to unpack evaluation, unhandled instance when checking Name object"

        # if len(node.ops) > 1:
            # TODO: will probably need recursive function to evaluate all comparisons?
            # logging.exception(f"TODO: cannot handle multiple comparisons yet", exc_info=False)
            # raise Exception("TODO: cannot handle multiple comparisons yet")

        assert len(node.ops) == 1, "TODO: cannot handle multiple comparisons"

        t_id = self.add_type_if_nonexistant(
            self.TypeContext(
                DataType.BOOLEAN
            ),
            f"%type_{DataType.BOOLEAN.name.lower()}"
        )

        # fails to do 1 > b -- "constant object has no attribute id"
        # TODO: needs typechecking to determine correct type of node
        # target_type = self.spirv_helper.get_symbol_type(node.left.id) # this will need to be changed to whatever object the left operand is

        eval_left_id, left_ctx = self._eval_line(node.left)
        eval_right_id, right_ctx = self._eval_line(node.comparators[0])

        left_type = self._extract_type(left_ctx)
        right_type = self._extract_type(right_ctx)

        assert left_type is right_type, f"type mismatch, left is {left_type}, right is {right_type}"

        # big chance that this will have to get changed since it may cause issues if you're not super specific with types
        # if left_type is not right_type:
            # logging.exception(f"{errors.TitanErrors.TYPE_MISMATCH.value}, L: {left_type} R: {right_type} ({errors.TitanErrors.TYPE_MISMATCH.name})")
            # raise Exception(f"{errors.TitanErrors.TYPE_MISMATCH.value}, L: {left_type} R: {right_type} ({errors.TitanErrors.TYPE_MISMATCH.name})")
        # else:

        target_type = left_type
        target_type_id = self.get_primative_type_id(target_type)


        # handle left node
        if isinstance(node.left, ast.Name):
            # if name, that means symbol, so we have to load it
            load_str = f"temp_{node.left.id}"
            self.add_line(
                self.Sections.FUNCTIONS,
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
            self.add_line(
                self.Sections.FUNCTIONS,
                f"%{load_str} = OpLoad {target_type_id} %{node.comparators[0].id}"
            )
            eval_right_id = load_str

        # node.ops contains a list of operators (as ast.LtE, ast.Gt etc etc), we take the zeroth one since atm we can only do 1 comparison
        opcode = self.__return_correct_opcode(target_type, node.ops[0])

        intermediate_id = self.get_new_intermediate_id()
        self.add_intermediate_id(f"{intermediate_id}", target_type)
        self.add_line(
            self.Sections.FUNCTIONS,
            f"%{intermediate_id} = {opcode} {t_id} %{eval_left_id.strip('%')} %{eval_right_id.strip('%')}"
        )

        self._latest_compare_id = f"%{intermediate_id}"

    # TODO: figure out exactly what info is needed from here, if any
    def visit_arguments(self, node): pass

    def visit_Constant(self, node): pass

    def generic_visit(self, node):
        logging.debug(f"generic visit {node.__class__.__name__} {node._fields}")

    def _extract_content(self, node):
        """ Extract the relevant content from a given node type.

            TODO:
                Better explanation
        
            Returns:
                value if node is ``ast.Constant``, if if node is ``ast.Name``
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
        if isinstance(context, self.TypeContext):
            return context.primative_type
        elif isinstance(context, self.ConstContext):
            return context.primative_type
        elif isinstance(context, DataType):
            return DataType(context.value)
        elif context is bool or int:
            return context
        else:
            logging.exception(f"unable to extract type from context - {context} {type(context)}", exc_info=False)
            raise Exception(f"unable to extract type from context - {context} {type(context)}")
        
    def __return_correct_opcode(self, chosen_type, operation):
        logging.debug(f"determining opcode for {operation} (type: {chosen_type})")

        if isinstance(chosen_type, DataType):
            chosen_type = chosen_type.value

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
        """ Recursively evaluates a line

            Returns:
                Final line id
                Line context
        """
        logging.debug(f"evaluating node: {node.__class__}, {node}")

        if isinstance(node, ast.BinOp):

            left_id, left_ctx = self._eval_line(node.left)
            right_id, right_ctx = self._eval_line(node.right)

            return_ctx = None
            chosen_type = None

            left_type = self._extract_type(left_ctx)
            left_type_id = self.get_primative_type_id(left_type)

            right_type = self._extract_type(right_ctx)
            right_type_id = self.get_primative_type_id(right_type)


            assert left_type is right_type, f"type mismatch, left is {left_type}, right is {right_type}"

            # if left_type is not right_type:
                # logging.exception(f"mismatched types l: {left_type} r: {right_type}", exc_info=False)
                # raise Exception(f"mismatched types l: {left_type}  r: {right_type}")

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

            left_id = self.add_temp_load_op_if_needed(left_id, left_type_id)
            right_id = self.add_temp_load_op_if_needed(right_id, right_type_id)

            chosen_type_id = self.get_primative_type_id(DataType(chosen_type))

            # set the appropriate opcode
            opcode = None
            opcode = self.__return_correct_opcode(chosen_type, node.op)
            
            assert not opcode is None, f"opcode is still none after attempting to determine it, why?"

            # if opcode is None:
                # logging.exception(f"opcode was not updated, why? {node.op} {chosen_type} {left_id} {right_id} {left_type} {right_type}", exc_info=False)
                # raise Exception(f"opcode was not updated, why? {node.op} {chosen_type} {left_id} {right_id} {left_type} {right_type}")

            # spirv_line_str = f"titan_id_{self.get_and_increment_intermediate_id()}"
            spirv_line_str = self.get_new_intermediate_id()
            self.add_line(
                self.Sections.FUNCTIONS,
                f"%{spirv_line_str} = {opcode} {chosen_type_id} %{left_id.strip('%')} %{right_id.strip('%')}"
            )
            self.add_intermediate_id(f"{spirv_line_str}", chosen_type)

            # TODO: check which type is not None, and propagate that back up
            # TODO: should we change the type for a symbol?
            return spirv_line_str, return_ctx
        
        elif isinstance(node, ast.UnaryOp):

            if isinstance(node.op, ast.USub):
                value = node.operand.value

                # if type(value) not in [int, float, bool]:
                    # logging.exception(f"got unexpected constant value type {type(value)}", exc_info=False)
                    # raise Exception(f"got unexpected constant value type {type(value)}")
                
                assert type(value) in [int, float, bool], f"got unexpected constant value type: {type(value)}"

                c_ctx = self.ConstContext(type(value), value * -1)

                if not self.const_exists(c_ctx):
                    # id = f"%const_{self._return_string_from_type(type(value))}_n{str(value).replace('.', '_')}"
                    id = f"%const_{DataType(type(value)).name.lower()}_n{str(value).replace('.', '_')}"
                    self.add_const_if_nonexistant(c_ctx, True)
                    return id, c_ctx
                else:
                    return self.get_const_id(value*-1, type(value)), c_ctx
                
            else:
                logging.exception(f"unhandled additional operator in unaryop class {node.op}", exc_info=False)
                raise Exception(f"unhandled additional operator in unaryop class {node.op}")
                # return f"{node.op.__class__.__name__} {node.operand.value} {type(node.operand.value)} ({isinstance(node.op,ast.USub)})"

        elif isinstance(node, ast.Name):
            # if not self.symbol_exists(node.id):
                # logging.exception(f"symbol '{node.id}' does not exist", exc_info=False)
                # raise Exception(f"symbol '{node.id}' does not exist")
            
            assert self.symbol_exists(node.id), f"symbol '{node.id}' does not exist"

            return f"{node.id}", self.get_symbol_type(node.id)

        elif isinstance(node, ast.Constant):

            # TODO: maybe use titan_types instead of python types?
            # BUG: if using DataType, _eval_line will fail with type mismatch error
            #      but if left alone, it sometimes creates duplicate constant lines?
            #      reproduce with simple_neuron -> duplicate "%const_integer_0"
            #      may be worth switching over to using bidicts?
            c_ctx = self.ConstContext(DataType(type(node.value)), node.value)
            # c_ctx = self.ConstContext(type(node.value), node.value)

            if not self.const_exists(c_ctx):
                # TODO: check if type also exists?
                # id = f"%const_{self._return_string_from_type(type(node.value))}_{node.value}"
                id = f"%const_{DataType(type(node.value)).name.lower()}_{str(node.value).replace('.', '_')}"
                # self.spirv_helper.add_const(c_ctx, id)
                self.add_const_if_nonexistant(c_ctx)
                return id, c_ctx
            else:
                return self.get_const_id(node.value, DataType(type(node.value))), c_ctx
        
        elif isinstance(node, ast.IfExp):
            self.visit_IfExp(node)

            # return the context of the comparison node, because that'll indicate the type
            # whereas the the ifexp_selector would only be bool due to the comparison condition
            ctx = self.get_type_of_intermediate_id(self._latest_compare_id[1:])
            return self._latest_ifexp_selector_id, ctx

        elif isinstance(node, ast.Compare):
            self.visit_Compare(node)

            ctx = self.get_type_of_intermediate_id(self._latest_compare_id[1:])
            return self._latest_compare_id, ctx
        
        elif isinstance(node, ast.Call):

            module_name = node.func.value.id
            function_name = node.func.attr

            exists_in_normal_mapping = module_name in self._import_mapping
            exists_in_inverse_mapping = module_name in self._import_mapping.inverse

            # check if explicitly using numpy for arrays etc
            module_is_numpy = False
            if exists_in_normal_mapping:
                module_is_numpy = True if self._import_mapping[module_name] == "numpy" else False
            elif exists_in_inverse_mapping:
                module_is_numpy = True if self._import_mapping.inverse[module_name] == "numpy" else False


            assert module_is_numpy, f"unhandled call object for {module_name}, probably incompatible"
            assert function_name in ["empty", "zeroes", "ones"], f"unhandled/unimplemented numpy function being accessed: {function_name}"

            logging.warn("initialisation of arrays with a specific value/values is not supported, do not rely on this behaviour")

            type_as_str = None
            for keyword in node.keywords:
                if keyword.arg == "dtype":
                    type_as_str = keyword.value.id
            
            assert not type_as_str is None, f"unable to set type for array"

            # add just in case
            type_as_datatype = DataType(self._get_python_type_from_string(type_as_str))
            primative_type_id = self.add_type_if_nonexistant(
                self.TypeContext(type_as_datatype),
                f"%type_{type_as_datatype.name.lower()}"
            )

            array_size = node.args[0]            
            assert not isinstance(array_size, tuple), f"TODO: tuples not supported for defining array shapes"
            
            array_size_id, array_size_ctx = self._eval_line(array_size)
            assert array_size_ctx.value > 0, f"array size cannot be less than or equal to 0, got {array_size_ctx.value} instead"

            t_ctx_array = self.TypeContext(
                primative_type=DataType(self._get_python_type_from_string(type_as_str)),
                is_array=True,
                is_pointer=False,
                array_size=array_size_ctx.value
            )

            t_id_array = self.add_type_if_nonexistant(t_ctx_array, f"%array_{type_as_str}_{array_size_ctx.value}")
        
            # making the assumtion that any arrays being defined in here will defined inside the function
            # and therefore will have the Function storage location

            t_ctx_array_ptr = self.TypeContext(
                primative_type= DataType(self._get_python_type_from_string(type_as_str)),
                storage_type= StorageType.FUNCTION_VAR,
                is_pointer= True,
                is_array= True,
                array_size= array_size_ctx.value
            )

            # NOTE: need to handle different storage locations? or will that be done somewhere else?
            t_id_array_ptr = self.add_type_if_nonexistant(t_ctx_array_ptr, f"%array_ptr_{type_as_str}_{array_size_ctx.value}_{StorageType.FUNCTION_VAR.name.lower()}")

            return t_id_array_ptr, t_ctx_array_ptr

        elif isinstance(node, ast.Assign):
            type_id, type_ctx = self._eval_line(node.value)

            # special case: array definition
            if isinstance(node.value, ast.Call):
                symbol_name = node.targets[0].id

                # if the symbol doesn't already exist, we can be confident that it hasn't been declared yet
                # can define as StorageType.FUNCTION_VAR because arrays in parameters will be handled differently
                self.add_symbol_if_nonexistant(symbol_name, type_ctx.primative_type, StorageType.FUNCTION_VAR, type_id, type_ctx.array_size)

                return "%" + symbol_name, type_ctx
            
            else:
                raise Exception(f"unexpected node: {type(node.value)}")


        elif isinstance(node, ast.Subscript):
            """ this stage will return a temporary ID related to the OpAccessChain operand"""
            
            assert self.symbol_exists(node.value.id), f"symbol '{node.value.id}' doesn't exist"

            index_id, _ = self._eval_line(node.slice)
            array_ctx = self.get_symbol_info(node.value.id)

            element_ctx = self.TypeContext(
                array_ctx.type,
                array_ctx.location,
                is_pointer=True
            )
            element_type_id = self.get_type_id(element_ctx)

            temp_id = self.get_new_intermediate_id()

            self.add_line(
                self.Sections.FUNCTIONS,
                f"%{temp_id} = OpAccessChain {element_type_id} %{node.value.id} %{index_id.strip('%')}"
            )

            # function does not account for pointer, potential fix needed?
            self.add_intermediate_id(temp_id, DataType(array_ctx.type), is_accessing_array=True)

            return temp_id, element_ctx

        elif isinstance(node, ast.Slice):
            raise Exception(f"slicing not implemented: {node}")

        else:
            logging.exception(f"unexpected {type(node)} to parse in eval_line, probably not implemented yet", exc_info=False)
            raise Exception(f"unexpected {type(node)} to parse in eval_line, probably not implemented yet")

    def _eval_line_wrap(self, node):
        """ Works on ast.Assign or ast.AnnAssign nodes
        """
        
        # this will call _eval_line on various nodes, including IfExp instead of going through visit_IfExp
        # is this going to be an issue?

        if isinstance(node, ast.Assign):
            assert len(node.targets) == 1, f"multiple assignments not supported"
            
            # if we're assinging via a call specifically
            if isinstance(node.value, ast.Call):
                evaluated = self._eval_line(node)
                # logging.debug(f" = {evaluated}")
                return evaluated

            # for target in node.targets:
            target = node.targets[0]
            # logging.debug(f"{target.id}")

            evaluated = self._eval_line(node.value)
            # logging.debug(f" = {evaluated}")
            return evaluated

        elif isinstance(node, ast.AnnAssign):
            # logging.debug(f"{node.target.id}")
            
            evaluated = self._eval_line(node.value)
            # logging.debug(f" = {evaluated}")
            return evaluated