from enum import Enum, auto

class DataType(Enum):
    """ Enum to map primative (Python) datatypes onto more abstract keys."""
    VOID = auto()
    NONE = None
    INTEGER = int
    FLOAT = float
    BOOLEAN = bool

class StorageType(Enum):
    """ Enum to define an analog to SPIR-V's own storage operations.
    
        This is required because SPIR-V can define variables as being inputs or outputs, or function variables
        depending on where they are declared. It's important to keep track of these so that the generated SPIR-V
        is correct.
    """
    IN = auto()
    OUT = auto()
    FUNCTION_VAR = auto()
    NONE = auto()