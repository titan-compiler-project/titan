from enum import Enum, auto
from typing import NamedTuple, TypedDict
# import typing
import type

class Machine:

    def __init__(self):
        self.options = []
        self.output_options = []
        self.processed_text = []
        self.files = []
        self.parsed_modules = []
        self.functions = []
        self.name_of_top_module = None

    # def set_options(self, options):
    #     self.options = options

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

        self.declared_types: declared_type_dict_hint = {}
        self.declared_function_types: declared_func_type_dict_hint = {}

        self.location = 0

        # self.declared_types = {} # TYPE: id
        # self.declared_function_types = {} #TYPE: id 
        # self.declared_input_types = {}
        # self.declared_output_types = {}
        # self.declared_ids = {} # id: ?


    def append_code(self, section: Sections, code):
        self.generated_spirv[section.name].append(code)

    def print_contents(self):
        print("-"*10)
        for section, code in self.generated_spirv.items():
            print(f"{section}")
            for entry in code:
                print(f"\t{entry}")
        print("-"*10)


    # ==== type helper functions ====
    def type_exists(self, type: TypeContext):
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


    # def add_id(self, id, value):
    #     self.declared_ids[id] = value

    # def type_exists(self, type: type.DataType):
    #     return True if type in self.declared_types else False
    
    # def function_type_exists(self, type: type.DataType):
    #     return True if type in self.declared_function_types else False
    
    # def get_type_id(self, type: type.DataType):
    #     return self.declared_types[type]
    
    # def get_function_type_id(self, type: type.DataType):
    #     return self.declared_function_types[type]
