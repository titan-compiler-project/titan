import pytest

from titan.compiler import node
from titan.common.symbols import Operation

@pytest.fixture(name="base_node_ctx")
def fixture_create_base_node_ctx() -> node.NodeContext:
    """
    Fixture: Create a basic NodeContext object

    Returns:
        A simple ``NodeContext`` object that can be used to create a ``Node``
    """

    return node.NodeContext(
        line_no=0, id="%base_node", type_id="%type_integer", 
        input_left=None, input_right=None, operation=Operation.NOP,
        data=[], is_comparison=False, array_id="", array_index_id=""
    )

@pytest.fixture(name="default_node_assembler")
def fixture_create_default_node_assembler() -> node.NodeAssembler:
    """
    Fixture: Create a node assembler for tests

    Returns:
        A simple ``NodeAssembler`` object containing a "default_module" available for use
    """
    assembler = node.NodeAssembler()
    assembler.create_module("default_module")
    return assembler