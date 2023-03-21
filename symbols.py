from enum import Enum, auto
from typing import NamedTuple, TYPE_CHECKING

# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
# if TYPE_CHECKING:
#     from pyparsing import ParserElement

class DataType(Enum):
    NONE = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()

    
class Operation(Enum):
    VARIABLE_DECLARATION = auto()
    CONSTANT_DECLARATION = auto()
    FUNCTION_DECLARATION = auto()
    FUNCTION_IN_VAR_PARAM = auto()
    FUNCTION_OUT_VAR_PARAM = auto()
    ASSIGNMENT = auto()
    ADD = auto()
    SUB = auto()
    MULT = auto()
    DIV = auto()


class Information(NamedTuple):
    datatype: DataType
    operation: Operation
    #line_no = int
    #line = None #: ParserElement


class SymbolTable():

    # TODO: come up with a better solution -- using a dict for unique
    # variable names will not work when the scope changes
    # OR ---- new symbol table every scope change?
    content = {}

    def __init__(self):
        pass

    # add entry
    def add(self, expression, information: Information):
        self.content.update({expression: information})

    # delete entry
    def delete(self, expression):
        del self.content[expression]

    # return using key
    def get(self, expression):
        return self.content.get(expression)

    # if exists bool
    def exists(self, expression):
        return True if expression in self.content else False