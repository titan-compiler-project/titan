from enum import Enum

class TitanErrors(Enum):

    PARSE_BAD_OPTION = "unknown option"
    PARSE_OPTION_FAILURE = "unable to parse option" 
    NON_EXISTENT_FILE = "file does not exist or could not be found"
    NO_PARSED_SOURCE_CODE = "no parsed source code to generate SPIR-V from"
    UNDEFINED_TOP_MODULE = "undefined top module when there are multiple modules, use the -t option to set the top"
    PARSED_UNKNOWN_TYPE = "got unknown type while trying to generate SPIR-V"
    NOT_IMPLEMENTED = "feature not implemented (yet)"
    TYPE_EXTRACT_FAILED = "unable to extract type"
    UNKNOWN_TYPE_EXTRACTED = "got unknown type while extracting"
    UNKNOWN_TYPE_IN_ARITHMETIC = "got unknown type whilst parsing arithmetic"
    TYPE_MISMATCH = "type mismatch"
    UNKNOWN_OPERATOR_DURING_GENERATION = "got unknown operator whilst trying to generate opcode"
    UNKNOWN_TYPE_DURING_GENERATION = "got unknown type when trying to generate opcode"
    NON_EXISTENT_SYMBOL = "symbol does not exist"
    UNKNOWN_SPIRV_OPCODE = "unknown SPIR-V opcode"
    UNEXPECTED = "unexpected exception"
    BAD_TYPES = "bad/unsupported type(s) for operation"