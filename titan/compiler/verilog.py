import logging, io
from typing import NamedTuple, List
from enum import Enum, auto

from compiler.node import NodeAssembler, Node, NodeContext, NodeModuleData, NodeTypeContext
from common.grammar import TitanSPIRVGrammar
from common.symbols import Operation, Operation_Type, DataType, StorageType
from common.errors import TitanErrors


class VerilogAssember():
    """ VerilogAssembler class. 
    
        Contains functionality to create Verilog from Nodes.
    """

    class FunctionLocation(NamedTuple):
        """ Tuple to track the start and end position of a SPIR-V function.
        
            Attributes:
                start_position: Start position of function.
                end_position: End position of function.
                name: Function name.
        """
        start_position: int
        end_position: int
        name: str

    class Sections(Enum):
        """ Enum describing different sections of the verilog file."""
        MODULE_AND_PORTS = auto()
        INTERNAL = auto()
        ALWAYS_BLOCK = auto()
        ASSIGNMENTS = auto()

    spirv_assembly = None
    parsed_spirv = None
    node_assembler: NodeAssembler = None

    generated_verilog_text = {
        Sections.MODULE_AND_PORTS: [],
        Sections.INTERNAL: [],
        Sections.ALWAYS_BLOCK: [],
        Sections.ASSIGNMENTS: []
    }


    def __init__(self, spirv_assembly: str):
        """ 
            Params:
                spirv_assembly: SPIR-V assembly code as one large string.
        """
        self.spirv_assembly = spirv_assembly
        self._parse_spirv_pyparsing()

    def _parse_spirv_pyparsing(self):
        """ Parses SPIR-V using ``pyparsing``.
        
            Works on the internal ``spirv_assembly`` attribute of the class, assigning the 
            value to ``parsed_spirv``.
        """
        with io.StringIO(self.spirv_assembly) as fake_file:
            self.parsed_spirv = TitanSPIRVGrammar.spirv_body.parse_file(fake_file)

    def _get_spirv_function_locations(self, parsed_spirv) -> List:
        """ Determine location of SPIR-V functions from parsed SPIR-V assembly. """
        # TODO: figure out how to improve this
        line_no = fn_start = 0
        fn_name = ""
        fn_locations = []
        _marked_start = False
        _marked_end = False
        for line in parsed_spirv:
            match line.opcode:
                case "Function":
                    fn_start = line_no
                    fn_name = line.id[1:] # slice to remove '%'
                    _marked_start = True
                case "FunctionEnd":
                    fn_locations.append(self.FunctionLocation(fn_start, line_no, fn_name))
                    fn_name = ""
                    _marked_end = True      

            line_no += 1

        assert _marked_start and _marked_end, f"failed to determine start/end point of function: start? {_marked_start}, end? {_marked_end}"
        return fn_locations

    def append_code(self, section: Sections, code: str):
        """ Add code.
        
            Args:
                section: Section to add to.
                code: Code to add.
        """
        self.generated_verilog_text[section].append(code)

    def write_to_file(self, filename: str):
        """ Write verilog content out to a file.
        
            Args:
                filename: Name of file to create/overwrite.
        """
        logging.info(f"Writing RTL to file ({filename}.sv)")
        with open(f"{filename}.sv", "w") as f:
            for section, list_of_lines in self.generated_verilog_text.items():
                logging.debug(f"Writing section {section.name}")

                for line in list_of_lines:
                    f.write(line)
                    f.write(f"\n")

    def compile(self, filename: str, gen_yosys_script: bool = False):
        """ Function to begin compiling. Calls other relevant functions. 
        
            Args:
                filename: Name of file to create/overwrite when writing Verilog.
                gen_yosys_script: Create a Yosys script to visualise the verilog.
        """
        node_assember = self.compile_nodes()
        self.node_assembler = node_assember

        self.node_assembler.generate_dot_graph()
        self.node_assembler.clean_graph()
        self.node_assembler.generate_dot_graph("clean_nodes")


        self.compile_text()
        self.write_to_file(filename)

        if gen_yosys_script:
            with open(f"yosys_script_{filename}.txt", "w+") as f:
                f.write(f"read_verilog -sv {filename}.sv; proc; opt; memory; opt; show;")

    def compile_nodes(self):
        """ Generate Nodes from parsed SPIR-V assembly. 

            Note:
                Verilog and SystemVerilog are used interchangeably.
        """

        spirv_fn_name = None
        spirv_fn_locations = self._get_spirv_function_locations(self.parsed_spirv)

        node_assembler = NodeAssembler()

        # deal with headers
        for line_no in range(0, spirv_fn_locations[0].start_position):
            line = self.parsed_spirv[line_no]
            logging.debug(line)

            match line.opcode:
                case "EntryPoint":
                    spirv_fn_name = line.opcode_args[2][1:-1]
                    node_assembler.create_module(spirv_fn_name)

                case "Constant":
                    if line.id not in node_assembler.declared_symbols:
                        node_assembler.declared_symbols.append(line.id)

                    if node_assembler.type_exists_in_module(spirv_fn_name, line.opcode_args[0]):
                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no,
                                    line.id,
                                    line.opcode_args[0],
                                    None, None,
                                    Operation.GLOBAL_CONST_DECLARATION,
                                    [line.opcode_args[1]]
                                )
                            )
                        )
                    else:
                        logging.exception(f"{TitanErrors.NON_EXISTENT_SYMBOL.value} ({line.opcode_args[0]} on line {line_no}) ({TitanErrors.NON_EXISTENT_SYMBOL.name})", exc_info=False)
                        raise Exception(f"{TitanErrors.NON_EXISTENT_SYMBOL.value} ({line.opcode_args[0]} on line {line_no})", TitanErrors.NON_EXISTENT_SYMBOL.name)
        
                case "Variable":
                    if line.id not in node_assembler.declared_symbols:
                        node_assembler.declared_symbols.append(line.id)

                    match line.opcode_args[1]:
                        case "Output":
                            node_assembler.add_output_to_module(spirv_fn_name, line.id[1:])
                            node_assembler.add_body_node_to_module(
                                spirv_fn_name,
                                Node(
                                    NodeContext(
                                        line_no, line.id,
                                        node_assembler.get_primative_type_id_from_id(spirv_fn_name, line.opcode_args[0]),
                                        None, None,
                                        Operation.GLOBAL_VAR_DECLARATION,
                                        [Operation.FUNCTION_OUT_VAR_PARAM]
                                    )
                                )
                            )

                        case "Input":
                            node_assembler.add_input_to_module(spirv_fn_name, line.id[1:])
                            node_assembler.add_body_node_to_module(
                                spirv_fn_name,
                                Node(
                                    NodeContext(
                                        line_no, line.id,
                                        node_assembler.get_primative_type_id_from_id(spirv_fn_name, line.opcode_args[0]),
                                        None, None,
                                        Operation.GLOBAL_VAR_DECLARATION,
                                        [Operation.FUNCTION_IN_VAR_PARAM]
                                    )
                                )
                            )

                case "TypePointer":
                    node_assembler.add_type_context_to_module(
                        spirv_fn_name,
                        line.id,
                        NodeTypeContext(
                            node_assembler.get_datatype_from_id(spirv_fn_name, line.opcode_args[1]), # returns types.DataType
                            [], True, line.opcode_args[1]
                        )
                    )

                case "TypeInt":
                    node_assembler.add_type_context_to_module(
                        spirv_fn_name, line.id,
                        NodeTypeContext(
                            DataType.INTEGER, line.opcode_args.as_list()
                        )
                    )

                case "TypeFloat":
                    # TODO
                    logging.exception(f"{TitanErrors.NOT_IMPLEMENTED.value} TypeFloat ({TitanErrors.NOT_IMPLEMENTED.name})", exc_info=False)
                    raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} TypeFloat", TitanErrors.NOT_IMPLEMENTED.name)
                
                case "TypeBool":
                    node_assembler.add_type_context_to_module(
                        spirv_fn_name, line.id,
                        NodeTypeContext(
                            DataType.BOOLEAN, [], False, ""
                        )
                    )


        # handle body
        #                            v total spirv functions
        for counter in range(0, len(spirv_fn_locations)):
            spirv_fn = spirv_fn_locations[counter]

            for position in range(spirv_fn.start_position, spirv_fn.end_position+1):
                line = self.parsed_spirv[position]
                logging.debug(f"current SPIRV line is: {line}")

                match line.opcode:
                    case "Variable":
                        if line.id not in node_assembler.declared_symbols:
                            node_assembler.declared_symbols.append(line.id)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id,
                                    node_assembler.get_primative_type_id_from_id(spirv_fn_name, line.opcode_args[0]),
                                    None, None,
                                    Operation.VARIABLE_DECLARATION
                                )
                            )
                        )

                    case "Store":
                        if node_assembler.node_exists(spirv_fn_name, line.opcode_args[1]):
                            logging.debug(f"{line.opcode_args[1]} is to be STOREd in {line.opcode_args[0]}")
                            value_node = node_assembler.get_node(spirv_fn_name, line.opcode_args[1])
                            node_assembler.modify_node(spirv_fn_name, line.opcode_args[0], 0, value_node, Operation.STORE)
                        else:
                            logging.exception(f"node does not exist {spirv_fn_name} {line.opcode_args[1]}", exc_info=False)
                            raise Exception(f"node does not exist {spirv_fn_name} {line.opcode_args[1]}")
                        
                    case "Load":
                        value_node = node_assembler.get_node(spirv_fn_name, line.opcode_args[1])

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0], value_node, None,
                                    Operation.LOAD
                                )
                            )
                        )

                    case "IAdd":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node, Operation.ADD
                                )
                            )
                        )

                    case "ISub":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node, Operation.SUB
                                )
                            )
                        )

                    case "IMul":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node, Operation.MULT
                                )
                            )
                        )

                    case "SDiv":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node, Operation.DIV
                                )
                            )
                        )

                    case "Select":
                        #                          0           1               2             3
                        # %result_id = OpSelect %type_id %comparison_id %true_value_id %false_value_id
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line, [2, 3])

                        compare_node = node_assembler.get_node(spirv_fn_name, line.opcode_args[1])

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node, Operation.DECISION, [compare_node], True
                                )
                            )
                        )

                    case "IEqual" | "FOrdEqual":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node,
                                    Operation.EQUAL_TO
                                )
                            )
                        )

                    case "INotEqual" | "FOrdNotEqual":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node,
                                    Operation.NOT_EQUAL_TO
                                )
                            )
                        )

                    case "SLessThan" | "FOrdLessThan":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node,
                                    Operation.LESS_THAN
                                )
                            )
                        )

                    case "SLessThanEqual" | "FOrdLessThanEqual":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node,
                                    Operation.LESS_OR_EQ
                                )
                            )
                        )

                    case "SGreaterThan" | "FOrdGreaterThan":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node,
                                    Operation.GREATER_THAN
                                )
                            )
                        )

                    case "SGreaterThanEqual" | "FOrdGreaterThanEqual":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node,
                                    Operation.GREATER_OR_EQ
                                )
                            )
                        )

                    case "ShiftLeftLogical":
                        # left_node = thing to shift
                        # right_node = how much to shift by
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node,
                                    Operation.SHIFT_LEFT
                                )
                            )
                        )

                    # NOTE: this might need to handle "OpShiftRightArithmetic"
                    # NOTE? why does this case statement have the "Op" prefix but none of the others do?
                    case "ShiftRightLogical":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    position, line.id, line.opcode_args[0],
                                    left_node, right_node,
                                    Operation.SHIFT_RIGHT
                                )
                            )
                        )

                    case _:
                        # TODO: make this less ugly
                        assert line.opcode in ["Function", "Label", "Return", "FunctionEnd"], f"unknown spirv opcode: {line.opcode}"
                        continue
                        
        return node_assembler
    
    def compile_text(self):
        """ Generate Verilog source code from Nodes. """


        def _get_correct_id(node: Node):
            """ Determine the correct ID/value to return.
            
                Needed because literal constant values need to be returned
                instead of the ID for them.

                Args:
                    node: Node to determine ID for.

                TODO:
                    Rename the function to something that describes it better.
            """
            if node.operation in Operation_Type.GENERIC_CONSTANT_DECLARATION:
                return node.data[0]
            
            # added for handling comparison node
            if node.operation is Operation.STORE:
                return node.input_left.spirv_id[1:]
            else:
                return node.spirv_id[1:]
            
        self.append_code(
            self.Sections.MODULE_AND_PORTS,
            f"// generated by titan, dont modify anything otherwise it might break =)"
        )

        for module in self.node_assembler.content.keys():
            self.append_code(
                self.Sections.MODULE_AND_PORTS,
                f"module {module} ("
            )

            self.append_code(
                self.Sections.MODULE_AND_PORTS,
                f"\tinput logic clk_i,"
            )

            self.append_code(
                self.Sections.ALWAYS_BLOCK,
                f"\talways_ff @ (posedge clk_i) begin"
            )

            module_data = self.node_assembler.content[module]
            sorted_nodes = self.node_assembler._sort_body_nodes_by_tick(module)

            for tick in range(len(sorted_nodes.keys())):
                logging.debug(f"tick {tick} has {len(sorted_nodes[tick])} nodes")

                io_length_tracker = 0
                for x in range(len(sorted_nodes[tick])):
                    node = sorted_nodes[tick][x]
                    logging.debug(f"NODE: {node.spirv_id} {node}")

                    if node.operation is Operation.GLOBAL_VAR_DECLARATION:
                        assert tick == 0, f"variable declaration outside of tick 0"

                        type_ctx = self.node_assembler.get_type_context_from_module(module, node.type_id)
                        width = int(type_ctx.data[0])

                        ender = "\n);" if io_length_tracker == (len(module_data.inputs) + len(module_data.outputs)) - 1 else ","

                        match node.data[0]:
                            case Operation.FUNCTION_IN_VAR_PARAM:
                                self.append_code(
                                    self.Sections.MODULE_AND_PORTS,
                                    f"\tinput logic [{width-1}:0] {node.spirv_id[1:]}{ender}"
                                )
                            
                            case Operation.FUNCTION_OUT_VAR_PARAM:
                                self.append_code(
                                    self.Sections.MODULE_AND_PORTS,
                                    f"\toutput logic [{width-1}:0] {node.spirv_id[1:]}{ender}"
                                )
                        io_length_tracker += 1


                    # TODO: explain
                    if node.operation is Operation.STORE and len(node.data) == 1:
                        match node.data[0]:
                            case Operation.FUNCTION_OUT_VAR_PARAM:
                                self.append_code(
                                    self.Sections.ASSIGNMENTS,
                                    f"\tassign {node.spirv_id[1:]} = {node.input_left.spirv_id[1:]};"
                                )
                            case _:
                                logging.exception(f"{TitanErrors.UNEXPECTED.value} node: {node} ({TitanErrors.UNEXPECTED.name})", exc_info=False)
                                raise Exception(f"{TitanErrors.UNEXPECTED.value} node: {node}", TitanErrors.UNEXPECTED.name)
                            
                    if node.operation in Operation_Type.ARITHMETIC:
                        if node.spirv_id not in self.node_assembler.declared_symbols:
                            width = int(self.node_assembler.get_type_context_from_module(module, node.type_id).data[0])

                            self.append_code(
                                self.Sections.INTERNAL,
                                f"\tlogic [{width-1}:0] {node.spirv_id[1:]};"
                            )

                        line = f"\t\t{node.spirv_id[1:]} <= "
                        op_symbol = None

                        match node.operation:
                            case Operation.ADD:
                                op_symbol = "+"
                            case Operation.SUB:
                                op_symbol = "-"
                            case Operation.MULT:
                                op_symbol = "*"
                            case Operation.DIV:
                                op_symbol = "/"
                            case _:
                                logging.exception(f"unexpected node operation: {node.operation}")
                                raise Exception(f"unexpected node operation: {node.operation}")

                        if op_symbol is None:
                            raise Exception("op_symbol is None, but it should've been populated")

                        line += f"{_get_correct_id(node.input_left)} {op_symbol} {_get_correct_id(node.input_right)};"

                        self.append_code(self.Sections.ALWAYS_BLOCK, line)


                    if node.operation in Operation_Type.COMPARISON:
                        defer_node_creation = False

                        logging.debug(f"checking 1 tick ahead..({tick} + 1 = {tick+1})")

                        # TODO explain
                        for future_node in sorted_nodes[tick+1]:
                            if defer_node_creation:
                                break

                            if future_node.operation == Operation.DECISION:
                                if future_node.data[0].spirv_id == node.spirv_id:
                                    logging.debug("found a reference")
                                    defer_node_creation = True
                                else:
                                    logging.debug("no reference found")

                        logging.debug(f"stopped checking 1 tick ahead..")

                        if not defer_node_creation:
                            self.append_code(
                                self.Sections.INTERNAL,
                                f"\tlogic {node.spirv_id[1:]};"
                            )

                            compare_op = Operation(node.operation).value
                            line = f"\t\t{node.spirv_id[1:]} <= {_get_correct_id(node.input_left)} {compare_op} {_get_correct_id(node.input_right)};"

                            self.append_code(
                                self.Sections.ALWAYS_BLOCK,
                                line
                            )

                    if node.operation is Operation.DECISION:
                        logging.debug(f"in decision: {node}")
                        comparison_node = node.data[0]

                        # comparison node holds the comparison operator, and the comparison itself
                        # the paried decision node holds the expected results

                        # so i.e. c = a >= 10 ? 5 : 0 would require the comparison node to construct a >= 10
                        # and the paried decision node for the ? 5 : 0 section

                        # we dont want to create a logic value for the comparison node because that can just be abstracted away
                        # so instead we will create the logic value for the decision node

                        width = int(self.node_assembler.get_type_context_from_module(module, node.type_id).data[0])

                        self.append_code(
                            self.Sections.INTERNAL,
                            f"\tlogic [{width-1}:0] {node.spirv_id[1:]};"
                        )

                        compare_op = Operation(comparison_node.operation).value
                        
                        # TODO: __get_correct_id(node) was returning the string representation of the node instead, why?
                        line = f"\t\t{node.spirv_id[1:]} <= {_get_correct_id(comparison_node.input_left)} {compare_op} {_get_correct_id(comparison_node.input_right)} ? {_get_correct_id(node.input_left)} : {_get_correct_id(node.input_right)};"

                        self.append_code(
                            self.Sections.ALWAYS_BLOCK,
                            line
                        )


                    if node.operation in Operation_Type.BITWISE:
                        width = int(self.node_assembler.get_type_context_from_module(module, node.type_id).data[0])
                        
                        self.append_code(
                            self.Sections.INTERNAL,
                            f"\tlogic [{width-1}:0] {node.spirv_id[1:]}"
                        )

                        line = f"\t\t{_get_correct_id(node)} <= {_get_correct_id(node.input_left)} {Operation(node.operation).value} {_get_correct_id(node.input_right)};"

                        self.append_code(
                            self.Sections.ALWAYS_BLOCK,
                            line
                        )
            
            self.append_code(
                self.Sections.ALWAYS_BLOCK,
                f"\tend"
            )

            self.append_code(
                self.Sections.ASSIGNMENTS,
                "endmodule"
            )