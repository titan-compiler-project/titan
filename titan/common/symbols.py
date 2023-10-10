from enum import Enum, auto
from typing import NamedTuple, TYPE_CHECKING
from common.type import *

# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
# if TYPE_CHECKING:
#     from pyparsing import ParserElement

# TODO: maybe seperate into two enums? currently being used for
#       symbol table generation and dataflow graph generation
class Operation(Enum):
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
    ARITHMETIC = {Operation.ADD, Operation.SUB, Operation.MULT, Operation.DIV}
    GENERIC_CONSTANT_DECLARATION = {Operation.CONSTANT_DECLARATION, Operation.GLOBAL_CONST_DECLARATION}
    GENERIC_VARIABLE_DECLARATION = {Operation.VARIABLE_DECLARATION, Operation.GLOBAL_VAR_DECLARATION}
    COMPARISON = {Operation.LESS_THAN, Operation.LESS_OR_EQ, 
                  Operation.GREATER_THAN, Operation.GREATER_OR_EQ, 
                  Operation.EQUAL_TO, Operation.NOT_EQUAL_TO}
    BITWISE = {Operation.SHIFT_LEFT, Operation.SHIFT_RIGHT}

class LiteralSymbolGroup(set, Enum):
    ARITHMETIC = {"+", "-", "*", "/"}
    COMPARISON = {">=", ">", "<", "<=", "==", "!="}
    BITWISE = {"<<" , ">>"}

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