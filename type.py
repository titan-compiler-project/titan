from enum import Enum, auto

class DataType(Enum):
    NONE = auto()
    VOID = auto()
    INTEGER = int
    FLOAT = float
    BOOLEAN = bool

class StorageType(Enum):
    IN = auto()
    OUT = auto()
    FUNCTION_VAR = auto()