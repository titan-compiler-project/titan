from enum import Enum, auto
import symbols

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
    

class SPIRV_ASM:

    # TODO: DELETE AND MERGE WITH symbols.py
    # class Types(Enum):
    #     VOID = auto()
    #     INT = auto()
    #     CONST = auto()
    #     PTR = auto()
    #     OUTPUT = auto()
    #     INPUT = auto()
    #     VAR_FUNCTION_SCOPE = auto()

    class Sections(Enum):
        CAPABILITY_AND_EXTENSION = auto()
        ENTRY_AND_EXEC_MODES = auto()
        DEBUG_STATEMENTS = auto()
        ANNOTATIONS = auto()
        TYPES_CONSTS_VARS = auto()
        FUNCTIONS = auto()
    
    def __init__(self):
        self.generated_spirv = {
            self.Sections.CAPABILITY_AND_EXTENSION.name: [],
            self.Sections.ENTRY_AND_EXEC_MODES.name: [],
            self.Sections.DEBUG_STATEMENTS.name: [],
            self.Sections.ANNOTATIONS.name: [],
            self.Sections.TYPES_CONSTS_VARS.name: [],
            self.Sections.FUNCTIONS.name: []
        }

        self.declared_types = {} # TYPE: id
        self.declared_function_types = {} #TYPE: id 
        self.declared_ids = {} # id: ?
        self.location = 0

    def append_code(self, section: Sections, code):
        self.generated_spirv[section.name].append(code)

    def add_id(self, id, value):
        self.declared_ids[id] = value


    # def type_exists(self, type: Types):
        # return True if type in self.declared_types else False
    
    def type_exists(self, type: symbols.DataType):
        return True if type in self.declared_types else False
    
    def function_type_exists(self, type: symbols.DataType):
        return True if type in self.declared_function_types else False
    
    def get_type_id(self, type: symbols.DataType):
        return self.declared_types[type]
    
    def get_function_type_id(self, type: symbols.DataType):
        return self.declared_function_types[type]

    def print_contents(self):
        print("-"*10)
        for section, code in self.generated_spirv.items():
            print(f"{section}")
            for entry in code:
                print(f"\t{entry}")
        print("-"*10)