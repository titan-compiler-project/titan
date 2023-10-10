from enum import Enum, auto

class DataType(Enum):
    VOID = auto()
    NONE = None
    INTEGER = int
    FLOAT = float
    BOOLEAN = bool

class StorageType(Enum):
    IN = auto()
    OUT = auto()
    FUNCTION_VAR = auto()
    NONE = auto()