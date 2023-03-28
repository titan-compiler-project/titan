from enum import Enum, auto

class DataType(Enum):
    NONE = auto()
    VOID = auto()
    INTEGER = int
    FLOAT = float
    BOOLEAN = bool
    # CONSTANT = auto()
    # PTR_INT = auto()
    # PTR_FLOAT = auto()
    # PTR_BOOL = auto()
    # PTR_CONST = auto()

class StorageType(Enum):
    IN = auto()
    OUT = auto()
    FUNCTION_VAR = auto()