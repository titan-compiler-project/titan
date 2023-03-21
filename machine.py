from enum import Enum, auto

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

    class Types(Enum):
        VOID = auto()
        INT = auto()
        CONST = auto()
        PTR = auto()
        OUTPUT = auto()
        INPUT = auto()
        VAR_FUNCTION_SCOPE = auto()

    class Sections(Enum):
        CAPABILITY_AND_EXTENSION = auto()
        ENTRY_AND_EXEC_MODES = auto()
        ANNOTATIONS = auto()
        TYPES = auto()
        FUNCTIONS = auto()
    
    def __init__(self):
        self.generated_spirv = {
            self.Sections.CAPABILITY_AND_EXTENSION.name: [],
            self.Sections.ENTRY_AND_EXEC_MODES.name: [],
            self.Sections.ANNOTATIONS.name: [],
            self.Sections.TYPES.name: [],
            self.Sections.FUNCTIONS.name: []
        }

        self.declared_types = {} # id: TYPE
        self.declared_ids = {} # id: ?
        self.location = 0

    def append_code(self, section: Sections, code):
        self.generated_spirv[section.name].append(code)