# from __future__ import annotations
from enum import Enum
from typing import NamedTuple, TYPE_CHECKING

# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
if TYPE_CHECKING:
    from pyparsing import ParserElement

class SymbolTable():

    # python dict?
    
    content = {}

    def __init__(self):
        pass


class Types(Enum):
    NONE = 0
    INTEGER = 1
    FLOAT = 2
    BOOLEAN = 3
    CONSTANT = 4

    
class Information(NamedTuple):
    type: Types
    line_no = int
    line: ParserElement



