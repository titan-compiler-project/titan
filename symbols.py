from enum import Enum
from typing import NamedTuple, TYPE_CHECKING

# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
if TYPE_CHECKING:
    from pyparsing import ParserElement

class DataType(Enum):
    NONE = 0
    INTEGER = 1
    FLOAT = 2
    BOOLEAN = 3

    
class Operation(Enum):
    VARIABLE_DECLARATION = 0
    CONSTANT_DECLARATION = 1
    FUNCTION_DECLARATION = 2
    ASSIGNMENT = 3
    ADD = 4
    SUB = 5
    MULT = 6
    DIV = 7


class Information(NamedTuple):
    datatype: DataType
    operation: Operation
    line_no = int
    line: ParserElement


class SymbolTable():

    # python dict?
    
    content = {}

    def __init__(self):
        pass

    # add entry
    def add(self, expression, information: Information):
        self.content.update({expression: information})

    # delete entry
    # return using key
    # if exists bool