from __future__ import annotations # https://peps.python.org/pep-0484/#the-problem-of-forward-declarations
import type as t
from typing import NamedTuple, List
from symbols import Operation


class NodeContext(NamedTuple):
    line_no: int = 0
    id: str = ""
    type_id: str = ""
    input_left: Node = None
    input_right: Node = None
    # operation: str = ""
    operation: Operation = None


    # tick: int = 0 # tick is ignored when the node(s) are populated


class Node:

    @staticmethod
    def _set_tick_during_init(context: NodeContext):
        left_node_is_none = context.input_left == None
        right_node_is_none = context.input_right == None

        if left_node_is_none and right_node_is_none:
            return 0
        elif left_node_is_none:
            return context.input_right.tick
        elif right_node_is_none:
            return context.input_left.tick
        else:
            return max(context.input_left.tick, context.input_right.tick) + 1


    def __init__(self, context: NodeContext):
        self.spirv_line_no = context.line_no
        self.spirv_id = context.id
        self.input_left = context.input_left
        self.input_right = context.input_right
        self.operation = context.operation
        self.tick = self._set_tick_during_init(context)


    # TODO: make this look a lot better- how to do multi line strings without tabs?
    def __str__(self):
        return f"({self.__class__.__name__}: [{self.spirv_line_no}:{self.spirv_id}], \
left: [{self.input_left.spirv_id if self.input_left is not None else None}], \
right: [{self.input_right.spirv_id if self.input_right is not None else None}], \
operation: {self.operation}, tick: {self.tick})"


    def __repr__(self):
        return f"({self.__class__.__name__}: [{self.spirv_line_no}:{self.spirv_id}], left: [{self.input_left}], right: [{self.input_right}], op: {self.operation}, tick: {self.tick})"