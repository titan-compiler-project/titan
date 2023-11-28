from __future__ import annotations # https://peps.python.org/pep-0484/#the-problem-of-forward-declarations
import common.type as t
from typing import NamedTuple, List
from common.symbols import Operation


class NodeContext(NamedTuple):
    line_no: int = 0
    id: str = ""
    type_id: str = ""
    input_left: Node = None
    input_right: Node = None
    operation: Operation = None
    data: List() = []
    is_comparison: bool = False # hack because i didn't realise that OpSelect had so many parameters


    # tick: int = 0 # tick is ignored when the node(s) are populated


class Node:
    
    @staticmethod
    def _calculate_tick(left_node, right_node, comparison_node = None):
        # print("-[_calculate_tick] hit")
        
        if comparison_node is None:
            if left_node is None and right_node is None:
                return 0
            elif left_node is None:
                return right_node + 1
            elif right_node is None:
                return left_node + 1
            else:
                return max(left_node, right_node) + 1
        else:
            if left_node is None and right_node is None:
                return comparison_node + 1
            elif left_node is None:
                return max(right_node, comparison_node) + 1
            elif right_node is None:
                return max(left_node, comparison_node) + 1
            else:
                return max(left_node, right_node, comparison_node) + 1

    @staticmethod
    def _set_tick_during_init(context: NodeContext):
        # left_node_is_none = context.input_left == None
        # right_node_is_none = context.input_right == None

        l_node_val = None if context.input_left == None else context.input_left.tick
        r_node_val = None if context.input_right == None else context.input_right.tick

        if context.is_comparison:
            # return Node._calculate_tick(l_node_val, r_node_val, context.data[0].tick)
            # TODO: do we have to account for the tick of the input nodes, if the selector is guaranteed to come after?
            #                                                                               is it even guaranteed to come right after? idk
            return Node._calculate_tick(0, 0, context.data[0].tick) 
        else:
            return Node._calculate_tick(l_node_val, r_node_val)


    def __init__(self, context: NodeContext):
        self.spirv_line_no = context.line_no
        self.spirv_id = context.id
        self.type_id = context.type_id
        self.input_left = context.input_left
        self.input_right = context.input_right
        self.operation = context.operation
        self.data = context.data
        self.is_comparison = context.is_comparison
        self.tick = self._set_tick_during_init(context)


    def _update_tick(self):
        left_node_is_none = self.input_left == None
        right_node_is_none = self.input_right == None

        l_node_val = None if left_node_is_none else self.input_left.tick
        r_node_val = None if right_node_is_none else self.input_right.tick

        if self.is_comparison:
            return Node._calculate_tick(l_node_val, r_node_val, self.data[0].tick)
        else:
            return Node._calculate_tick(l_node_val, r_node_val)

        # if left_node_is_none and right_node_is_none:
        #     return 0
        # elif left_node_is_none:
        #     return self.input_right.tick + 1
        # elif right_node_is_none:
        #     return self.input_left.tick + 1
        # else:
        #     return max(self.input_left.tick, self.input_right.tick) + 1


    def update_input(self, pos: int, new_node: Node):        
        if pos == 0: # left node
            self.input_left = new_node
        elif pos == 1: # right node
            self.input_right = new_node

        self.tick = self._update_tick()

    # TODO: make this look a lot better- how to do multi line strings without tabs?
    # def __str__(self):
        # return f"({self.__class__.__name__}: [{self.spirv_line_no}:{self.spirv_id}], \
# left: [{self.input_left.spirv_id if self.input_left is not None else None}], \
# right: [{self.input_right.spirv_id if self.input_right is not None else None}], \
# operation: {self.operation}, data: {self.data}, tick: {self.tick})"

    # TODO: make this look better
    def __str__(self):
        return f"({self.__class__.__name__}: [{self.spirv_line_no}:{self.spirv_id}], type_id: [{self.type_id}], left: [{None if self.input_left is None else self.input_left.spirv_id}], right: [{None if self.input_right is None else self.input_right.spirv_id}], op: {self.operation}, data: {self.data},  is_comparison: {self.is_comparison}, tick: {self.tick})"


    def __repr__(self):
        return f"({self.__class__.__name__}: [{self.spirv_line_no}:{self.spirv_id}], type_id: [{self.type_id}], left: [{self.input_left}], right: [{self.input_right}], op: {self.operation}, data: {self.data},  is_comparison: {self.is_comparison}, tick: {self.tick})"