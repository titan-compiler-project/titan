from enum import Enum, auto
from typing import NamedTuple, TYPE_CHECKING
from common.type import *

# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
# if TYPE_CHECKING:
#     from pyparsing import ParserElement

# TODO: maybe seperate into two enums? currently being used for
#       symbol table generation and dataflow graph generation
class Operation(Enum):
    """ Enum containing possible operations, such as declaration or arithmetic."""
    # vars
    VARIABLE_DECLARATION = auto()
    CONSTANT_DECLARATION = auto()
    GLOBAL_VAR_DECLARATION = auto()
    GLOBAL_CONST_DECLARATION = auto()
    
    # funcs
    FUNCTION_DECLARATION = auto()
    FUNCTION_IN_VAR_PARAM = auto()
    FUNCTION_OUT_VAR_PARAM = auto()

    # operations
    ASSIGNMENT = auto()
    STORE = auto()
    LOAD = auto()
    ADD = "+"
    SUB = "-"
    MULT = "*"
    DIV = "/"
    
    # comparisons
    DECISION = auto()
    LESS_THAN = "<"
    LESS_OR_EQ = "<="
    GREATER_THAN = ">"
    GREATER_OR_EQ = ">="
    EQUAL_TO = "=="
    NOT_EQUAL_TO = "!="

    # logical
    SHIFT_LEFT = "<<"
    SHIFT_RIGHT = ">>"

    # misc
    NOP = auto()

# https://stackoverflow.com/questions/58492047/how-to-add-member-subsets-to-a-python-enum
class Operation_Type(set, Enum):
    """ Enum containing sets of ``titan.common.symbols.Operation``, bundled into common groups.
    
        Note:
            These groups are:

            - ``ARITHMETIC``
            - ``GENERIC_CONSTANT_DECLARATION``
            - ``GENERIC_VARAIBLE_DECLARATION``
            - ``COMPARISON``
            - ``BITWISE``
    """
    ARITHMETIC = {Operation.ADD, Operation.SUB, Operation.MULT, Operation.DIV}
    GENERIC_CONSTANT_DECLARATION = {Operation.CONSTANT_DECLARATION, Operation.GLOBAL_CONST_DECLARATION}
    GENERIC_VARIABLE_DECLARATION = {Operation.VARIABLE_DECLARATION, Operation.GLOBAL_VAR_DECLARATION}
    COMPARISON = {Operation.LESS_THAN, Operation.LESS_OR_EQ, 
                  Operation.GREATER_THAN, Operation.GREATER_OR_EQ, 
                  Operation.EQUAL_TO, Operation.NOT_EQUAL_TO}
    BITWISE = {Operation.SHIFT_LEFT, Operation.SHIFT_RIGHT}

class LiteralSymbolGroup(set, Enum):
    """ Enum containing symbols corresponding to operations."""
    ARITHMETIC = {"+", "-", "*", "/"}
    COMPARISON = {">=", ">", "<", "<=", "==", "!="}
    BITWISE = {"<<" , ">>"}

class Information(NamedTuple):
    """ Tuple to store information about the datatype and what operation is being performed."""
    datatype: DataType
    operation: Operation
    #line_no = int
    #line = None #: ParserElement


class SymbolTable():
    """ Simple symbol table class.
    
        Attributes:
            content: Dictionary to store the symbols.
    """
    # TODO: come up with a better solution -- using a dict for unique
    # variable names will not work when the scope changes
    # OR ---- new symbol table every scope change?
    content = {}

    def __init__(self):
        pass

    # add entry
    def add(self, expression, information: Information):
        """ Add an entry to the symbol table.

            Args:
                expression: Symbol to add.
                information: Store information about the operation.
        """
        self.content.update({expression: information})

    # delete entry
    def delete(self, expression):
        """ Delete an entry from the symbol table.
        
            Args:
                expression: Symbol to delete.
        """
        del self.content[expression]

    # return using key
    def get(self, expression) -> Information:
        """ Get information about the symbol.
        
            Args:
                expression: Symbol to query.

            Returns:
                Information about the symbol.
        """
        return self.content.get(expression)

    # if exists bool
    def exists(self, expression) -> bool:
        """ Check if a symbol exists.

            Args:
                expression: Symbol to check.

            Returns:
                True if symbol exists, else False.
        """
        return True if expression in self.content else False