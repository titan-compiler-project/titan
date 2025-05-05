import pytest

from tests.fixtures.node import *

from titan.compiler import node
from titan.common.symbols import Operation
from titan.common.type import DataType


class TestNodeContext:
    def test_create_basic_node(self, base_node_ctx: node.NodeContext) -> None:
        """
        Test: Create a basic node using a very simple ``NodeContext`` object

        Args:
            base_node_ctx (titan.compiler.node.NodeContext): Basic ``NodeContext`` object
        """

        basic_node = node.Node(base_node_ctx)

        assert basic_node.spirv_line_no == 0
        assert basic_node.spirv_id == "%base_node"
        assert basic_node.type_id == "%type_integer"
        assert basic_node.input_left is None
        assert basic_node.input_right is None
        assert basic_node.operation is Operation.NOP
        assert basic_node.data == []
        assert basic_node.is_comparison is False
        assert basic_node.array_id == ""
        assert basic_node.array_index_id == ""


class TestNode:
    def test_node_tick_calculation(self) -> None:
        """
        Test: Is the tick correctly calculated when given different values?
        """

        left_node = node.Node(
            node.NodeContext(id="%left_node")
            )
        
        right_node = node.Node(
            node.NodeContext(id="%right_node")
            )

        # No parents
        test_node = node.Node(
            node.NodeContext(input_left=None, input_right=None)
        )
        assert test_node.tick == 0
        del test_node

        # Left parent only
        test_node = node.Node(
            node.NodeContext(input_left=left_node)
        )
        assert test_node.tick == 1
        del test_node

        # Right parent only
        test_node = node.Node(
            node.NodeContext(input_right=right_node)
        )
        assert test_node.tick == 1
        del test_node

        # Left & right parent
        test_node = node.Node(
            node.NodeContext(input_left=left_node, input_right=right_node)
        )
        assert test_node.tick == 1
        del test_node

        # No parents & comparison but no data
        with pytest.raises(Exception):
            test_node = node.Node(
                node.NodeContext(is_comparison=True, data=[])
            )


        # No parents & comparison but data
        test_node = node.Node(
            node.NodeContext(is_comparison=True, data=[left_node])
        )
        assert test_node.tick == 1
        del test_node

        # Left + right parent & comparison
        comparison_node = node.Node(
            node.NodeContext(id="%comparison_node")
            )
        
        comparison_node.tick = 3 # set a different tick

        test_node = node.Node(
            node.NodeContext(input_left=left_node, input_right=right_node,
                            is_comparison=True, data=[comparison_node]
                            )
        )
        assert test_node.tick == 4
        del test_node


    def test_node_update_inputs(self) -> None:
        """
        Test: is the ``Node`` object being correctly updated when adding new parents?

        We should see the tick being updated correctly based on its new inputs.
        """

        input_node_1 = node.Node(
            node.NodeContext(id="%in_1")
        )

        input_node_1.tick = 4

        base_node = node.Node(
            node.NodeContext(id="%base_node")
        )

        assert base_node.tick == 0

        # add left input
        base_node.update_input(0, input_node_1)
        assert base_node.tick == 5

        # clear inputs
        base_node.update_input(0, None)
        assert base_node.tick == 0

        # add right input
        input_node_1.tick = 7
        base_node.update_input(1, input_node_1)
        assert base_node.tick == 8

        # clear inputs
        base_node.update_input(1, None)
        assert base_node.tick == 0

        # add left, right & comparison input
        input_node_2 = node.Node(
            node.NodeContext(id="%in_2")
        )

        input_node_2.tick = 2

        comparison_node = node.Node(
            node.NodeContext(id="%compare_1")
        )

        comparison_node.tick = 9

        # at this point, input_node_1 = 7, input_node_2 = 2, comparison_node = 9
        # we expect the tick to be 10
        
        # NOTE: when we set the tick during initialisation, our calculation is:
        #       return Node._calculate_tick(0, 0, context.data[0].tick)
        #       but when we call update input, we pass the left & right node ticks properly:
        #       return Node._calculate_tick(l_node_val, r_node_val, self.data[0].tick)
        #
        #       why? is this a potential source of bugs? should be explained better
        base_node.is_comparison = True
        base_node.data = [comparison_node]
        base_node.update_input(0, input_node_1)
        base_node.update_input(1, input_node_2)
        assert base_node.tick == 10


class TestNodeAssembler:

    def test_create_module_fn(self) -> None:
        """
        Test: Is a ``NodeModuleData`` object with the correct properies being created?
        """

        assembler = node.NodeAssembler()
        assembler.create_module("test_module")

        assert "test_module" in assembler.content.keys() 
        assert isinstance(assembler.content["test_module"], node.NodeModuleData)

    def test_add_body_node_to_module_fn(self, default_node_assembler: node.NodeAssembler) -> None:
        """
        Test: Can we add a node to the body of a module?

        Args:
            default_node_assembler (titan.compiler.node.NodeAssembler): Pre-made node assembler
        """

        assembler = default_node_assembler # rename for easier reference

        body_node = node.Node(
            node.NodeContext(id="%body_node_1", operation=Operation.ADD)
        )

        assembler.add_body_node_to_module("default_module", body_node)
        assert body_node in assembler.content["default_module"].body_nodes["%body_node_1"]
        
        body_node.operation = Operation.NOP
        assembler.add_body_node_to_module("default_module", body_node)
        # check if in list
        assert body_node in assembler.content["default_module"].body_nodes["%body_node_1"]
        # if its actually the last one added
        assert body_node is assembler.content["default_module"].body_nodes["%body_node_1"][-1]
        # if its got the correct operation
        assert assembler.content["default_module"].body_nodes["%body_node_1"][-1].operation is Operation.NOP


    def test_type_context_in_module(self, default_node_assembler: node.NodeAssembler) -> None:
        """
        Test: Can we add, get and check a type context object in a given module?
        
        Args:
            default_node_assembler (titan.compiler.node.NodeAssembler): Pre-made node assembler
        """

        assembler = default_node_assembler

        type_ctx = node.NodeTypeContext(
            type=DataType.INTEGER, data=[], is_pointer=False,
            alias="", is_array=False, array_dimension_id=""
        )

        # add
        assembler.add_type_context_to_module("default_module", "%type_integer", type_ctx)
        assert type_ctx is assembler.content["default_module"].types["%type_integer"]

        # check if exists
        assert assembler.type_exists_in_module("default_module", "%type_integer")
        assert not assembler.type_exists_in_module("default_module", "%fake_type_that_doesnt_exist")

        # get
        retrieved_type_ctx = assembler.get_type_context_from_module("default_module", "%type_integer")
        assert retrieved_type_ctx is type_ctx
