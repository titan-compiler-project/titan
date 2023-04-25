import pytest
import dataflow as d
from typing import List

def test_node_creation():

    node_1 = d.Node(
        d.NodeContext(
            0, "%test_id_1", None, None, "const"
        )
    )

    assert node_1.spirv_line_no == 0
    assert node_1.spirv_id == "%test_id_1"
    assert node_1.input_left == None
    assert node_1.input_right == None
    assert node_1.operation == "const"
    assert node_1.tick == 0


# TODO: add more cases, i.e. handling (L: None, R: Node)
# @pytest.mark.parametrize("tick_list, expected_tick", [
    # ([3, 4], 5)
# ])
# def test_tick_propagation(tick_list, expected_tick):
def test_tick_propagation():
    
    # node_list = []
    node_list: List[d.Node] = []

    for x in range(0, 2):
        print(x)
        node_list.append(
            d.Node(d.NodeContext(
                x, f"%id_line_{x}", None, None, "OpCode"
            ))
        )

    node_list.append(
        d.Node(
            d.NodeContext(
                3, f"%end_node", node_list[0], node_list[1], "OpCode"
            )
        )
    )

    assert node_list[2].tick == 1