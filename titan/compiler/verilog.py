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
        logging.debug(f"processing SPIR-V headers...")
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

                        node_type_context = node_assembler.get_type_context_from_module(spirv_fn_name, line.opcode_args[0])

                        assert node_type_context.type != (DataType.VOID or DataType.NONE), f"got invalid type for constant"

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=line_no, id=line.id, type_id=line.opcode_args[0],
                                    operation=Operation.GLOBAL_CONST_DECLARATION,

                                    # this calls the correct conversion function to have literal value stored in data, instead of string
                                    # node_type_context.type.value == Datatype.INTEGER/FLOAT/BOOL.value == int()/float()/bool()
                                    data=[node_type_context.type.value(line.opcode_args[1])]
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
                                        line_no=line_no, id=line.id,
                                        type_id=node_assembler.get_primative_type_id_from_id(spirv_fn_name, line.opcode_args[0]),
                                        operation=Operation.GLOBAL_VAR_DECLARATION,
                                        data=[Operation.FUNCTION_OUT_VAR_PARAM]
                                    )
                                )
                            )

                        case "Input":
                            node_assembler.add_input_to_module(spirv_fn_name, line.id[1:])
                            node_assembler.add_body_node_to_module(
                                spirv_fn_name,
                                Node(
                                    NodeContext(
                                        line_no=line_no, id=line.id,
                                        type_id=node_assembler.get_primative_type_id_from_id(spirv_fn_name, line.opcode_args[0]),
                                        operation=Operation.GLOBAL_VAR_DECLARATION,
                                        data=[Operation.FUNCTION_IN_VAR_PARAM]
                                    )
                                )
                            )

                case "TypePointer":
                    node_assembler.add_type_context_to_module(
                        spirv_fn_name,
                        line.id,
                        NodeTypeContext(
                            type=node_assembler.get_datatype_from_id(spirv_fn_name, line.opcode_args[1]), # returns types.DataType
                            is_pointer=True, alias=line.opcode_args[1]
                        )
                    )

                case "TypeInt":
                    node_assembler.add_type_context_to_module(
                        spirv_fn_name, line.id,
                        NodeTypeContext(
                            type=DataType.INTEGER, data=line.opcode_args.as_list()
                        )
                    )

                case "TypeFloat":
                    # TODO
                    logging.exception(f"{TitanErrors.NOT_IMPLEMENTED.value} TypeFloat ({TitanErrors.NOT_IMPLEMENTED.name})", exc_info=False)
                    raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} TypeFloat", TitanErrors.NOT_IMPLEMENTED.name)
                
                case "TypeBool":
                    node_assembler.add_type_context_to_module(
                        spirv_fn_name, line.id,
                        NodeTypeContext(type=DataType.BOOLEAN)
                    )

                case "TypeArray":
                    node_assembler.add_type_context_to_module(
                        spirv_fn_name, line.id,
                        NodeTypeContext(
                            type=node_assembler.get_datatype_from_id(spirv_fn_name, line.opcode_args[0]),
                            is_array=True, array_dimension_id=line.opcode_args[1]
                        )
                    )

                # dont do anything for these
                case "TypeVoid": pass
                case "TypeFunction": pass
                case "Capability": pass
                case "MemoryModel": pass
                case "ExecutionMode": pass
                case "Name": pass
                case "Decorate": pass

                case _:
                    raise Exception(f"unhandled header opcode: {line.opcode}")


        logging.debug(f"processing SPIR-V function(s)...")
        # handle body
        #                            v total spirv functions
        for counter in range(0, len(spirv_fn_locations)):
            spirv_fn = spirv_fn_locations[counter]

            for position in range(spirv_fn.start_position, spirv_fn.end_position+1):
                line = self.parsed_spirv[position]
                logging.debug(f"{line}")

                match line.opcode:
                    case "Variable":
                        if line.id not in node_assembler.declared_symbols:
                            node_assembler.declared_symbols.append(line.id)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id,
                                    type_id=node_assembler.get_primative_type_id_from_id(spirv_fn_name, line.opcode_args[0]),
                                    operation=Operation.VARIABLE_DECLARATION
                                )
                            )
                        )

                    case "Store":

                        assert node_assembler.node_exists(spirv_fn_name, line.opcode_args[0]), f"node does not exist: {line.opcode_args[0]}"
                        assert node_assembler.node_exists(spirv_fn_name, line.opcode_args[1]), f"node does not exist: {line.opcode_args[1]}"
                        assert not node_assembler.is_symbol_an_input(spirv_fn_name, line.opcode_args[0]), f"cannot assign value to input variable"
                        logging.debug(f"'{line.opcode_args[1]}' is being stored in '{line.opcode_args[0]}'")

                        target_node = node_assembler.get_node(spirv_fn_name, line.opcode_args[0])
                        value_node = node_assembler.get_node(spirv_fn_name, line.opcode_args[1])

                        store_node_ctx = NodeContext(
                            line_no=position, id=line.opcode_args[0], 
                            type_id=target_node.type_id, input_left=value_node, operation=Operation.STORE
                        )

                        node_assembler.add_body_node_to_module(spirv_fn_name, Node(store_node_ctx))


                        
                    case "Load":
                        value_node = node_assembler.get_node(spirv_fn_name, line.opcode_args[1])

                        operation = Operation.ARRAY_LOAD if value_node.operation is Operation.ARRAY_INDEX else Operation.LOAD

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0], 
                                    input_left=value_node, operation=operation
                                )
                            )
                        )

                    case "IAdd":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node, operation=Operation.ADD
                                )
                            )
                        )

                    case "ISub":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node, operation=Operation.SUB
                                )
                            )
                        )

                    case "IMul":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node, operation=Operation.MULT
                                )
                            )
                        )

                    case "SDiv":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node, operation=Operation.DIV
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
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node, 
                                    operation=Operation.DECISION, 
                                    data=[compare_node], 
                                    is_comparison=True
                                )
                            )
                        )

                    case "IEqual" | "FOrdEqual":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node,
                                    operation=Operation.EQUAL_TO
                                )
                            )
                        )

                    case "INotEqual" | "FOrdNotEqual":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node,
                                    operation=Operation.NOT_EQUAL_TO
                                )
                            )
                        )

                    case "SLessThan" | "FOrdLessThan":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node,
                                    operation=Operation.LESS_THAN
                                )
                            )
                        )

                    case "SLessThanEqual" | "FOrdLessThanEqual":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node,
                                    operation=Operation.LESS_OR_EQ
                                )
                            )
                        )

                    case "SGreaterThan" | "FOrdGreaterThan":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node,
                                    operation=Operation.GREATER_THAN
                                )
                            )
                        )

                    case "SGreaterThanEqual" | "FOrdGreaterThanEqual":
                        left_node, right_node = node_assembler.get_left_and_right_nodes(spirv_fn_name, line)

                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node,
                                    operation=Operation.GREATER_OR_EQ
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
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node,
                                    operation=Operation.SHIFT_LEFT
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
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    input_left=left_node, input_right=right_node,
                                    operation=Operation.SHIFT_RIGHT
                                )
                            )
                        )

                    case "AccessChain":
                        array_node = node_assembler.get_node(spirv_fn_name, line.opcode_args[1])
                        node_assembler.add_body_node_to_module(
                            spirv_fn_name,
                            Node(
                                NodeContext(
                                    line_no=position, id=line.id, type_id=line.opcode_args[0],
                                    operation=Operation.ARRAY_INDEX, input_left=array_node,
                                    array_id=line.opcode_args[1], array_index_id=line.opcode_args[2]
                                )
                            )
                        )

                    # dont do anything with these
                    case "Function": pass
                    case "Label": pass
                    case "Return": pass
                    case "FunctionEnd": pass

                    case _:
                        raise Exception(f"unknown SPIR-V opcode: '{line.opcode}' -- {line}")
                    
        return node_assembler
    
    def compile_text(self):
        """ Generate SystemVerilog source code based on Nodes. """

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
            f"// automatically generated, dont modify otherwise it might break =)"
        )


        for module in self.node_assembler.content.keys():
            self.append_code(self.Sections.MODULE_AND_PORTS, f"module {module} (")
            self.append_code(self.Sections.MODULE_AND_PORTS, f"\tinput logic clock_i,")
            self.append_code(self.Sections.ALWAYS_BLOCK, f"\talways_ff @ (posedge clock_i) begin")
            
            module_data = self.node_assembler.content[module]
            sorted_nodes = self.node_assembler._sort_body_nodes_by_tick(module)

            for tick in range(len(sorted_nodes.keys())):
                logging.debug(f"tick {tick} has {len(sorted_nodes[tick])} nodes")

                io_length_tracker = 0

                for node_index in range(len(sorted_nodes[tick])):
                    node = sorted_nodes[tick][node_index]

                    logging.debug(f"node: {node.spirv_id} {node}")

                    match node.operation:

                        case Operation.GLOBAL_VAR_DECLARATION:
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


                        case Operation.VARIABLE_DECLARATION:
                            node_type_id = self.node_assembler.get_primative_type_id_from_id(module, node.type_id)
                            type_context = self.node_assembler.get_type_context_from_module(module, node_type_id)

                            if type_context.is_array:
                                # define array in sv
                                array_shape_node = self.node_assembler.get_node(module, type_context.array_dimension_id)
                                array_shape = array_shape_node.data[0]
                                assert type(array_shape) is int, f"unexpected type for array shape, expected int but got {type(array_shape)}. (only 1d arrays supported currently)"

                                assert array_shape >= 1, f"array shape must define array of 2 or more elements"
                                width = int(self.node_assembler.get_primative_type_context_from_datatype(module, type_context.type).data[0])

                                self.append_code(self.Sections.INTERNAL, f"\tlogic [{width-1}:0] {node.spirv_id[1:]} [0:{array_shape-1}];")

                            else:
                                logging.debug(f"not generating logic/reg for {node.spirv_id[1:]}: {node}")


                        case Operation.STORE:
                            if self.node_assembler.is_symbol_an_output(module, node.spirv_id[1:]):
                                self.append_code(self.Sections.ASSIGNMENTS, f"\tassign {node.spirv_id[1:]} = {node.input_left.spirv_id[1:]};")
                            else:
                                logging.debug(f"not creating assign statement for {node.spirv_id}: {node}")

                        case _ if node.operation in Operation_Type.ARITHMETIC:
                            if node.spirv_id not in self.node_assembler.declared_symbols:
                                width = int(self.node_assembler.get_type_context_from_module(module, node.type_id).data[0])

                                self.append_code(self.Sections.INTERNAL, f"\tlogic [{width-1}:0] {node.spirv_id[1:]};")

                            assert type(node.operation.value) is str, f"didn't get a string for operator, is it set correctly? {node.operation}"
                            line = f"\t\t{node.spirv_id[1:]} <= {_get_correct_id(node.input_left)} {node.operation.value} {_get_correct_id(node.input_right)};"

                            self.append_code(self.Sections.ALWAYS_BLOCK, line)

                        case _ if node.operation in Operation_Type.COMPARISON:
                            defer_node_creation = False
                            
                            logging.debug(f"checking 1 tick ahead..({tick} + 1 = {tick+1})")
                            for future_node in sorted_nodes[tick+1]:
                                if defer_node_creation: break

                                if future_node.operation == Operation.DECISION:
                                    if future_node.data[0].spirv_id == node.spirv_id:
                                        logging.debug(f"found a reference")
                                        defer_node_creation = True
                                    else:
                                        logging.debug("no reference found")

                            logging.debug("stopped checking 1 tick ahead")

                            # TODO: better variable name
                            if not defer_node_creation:
                                self.append_code(self.Sections.INTERNAL, f"\tlogic {node.spirv_id[1:]};")

                                assert type(node.operation.value) is str, f"didn't get a string for operator, is it set correctly? {node.operation}"

                                line = f"\t\t{node.spirv_id[1:]} <= {_get_correct_id(node.input_left)} {node.operation.value} {_get_correct_id(node.input_right)};"
                                self.append_code(self.Sections.ALWAYS_BLOCK, line)
                            else:
                                continue

                        case Operation.DECISION:
                            logging.debug(f"in decision: {node}")
                            comparison_node = node.data[0]

                            # comparison node holds the comparison operator, and the comparison itself
                            # the paried decision node holds the expected results

                            # so i.e. c = a >= 10 ? 5 : 0 would require the comparison node to construct a >= 10
                            # and the paried decision node for the ? 5 : 0 section

                            # we dont want to create a logic value for the comparison node because that can just be abstracted away
                            # so instead we will create the logic value for the decision node

                            width = int(self.node_assembler.get_type_context_from_module(module, node.type_id).data[0])

                            self.append_code(self.Sections.INTERNAL, f"\tlogic [{width-1}:0] {node.spirv_id[1:]};")

                            comparison_symbol = comparison_node.operation.value
                            assert type(comparison_node.operation.value) is str, f"didn't get a string for operator, is it set correctly? {comparison_node.operation} {comparison_node.operation.value}"
                            
                            # TODO: __get_correct_id(node) was returning the string representation of the node instead, why?
                            line = f"\t\t{node.spirv_id[1:]} <= {_get_correct_id(comparison_node.input_left)} {comparison_symbol} {_get_correct_id(comparison_node.input_right)} ? {_get_correct_id(node.input_left)} : {_get_correct_id(node.input_right)};"
                            self.append_code(self.Sections.ALWAYS_BLOCK, line)

                        case _ if node.operation in Operation_Type.BITWISE:
                            width = int(self.node_assembler.get_type_context_from_module(module, node.type_id).data[0])
                            
                            self.append_code(self.Sections.INTERNAL, f"\tlogic [{width-1}:0] {node.spirv_id[1:]}")

                            line = f"\t\t{_get_correct_id(node)} <= {_get_correct_id(node.input_left)} {Operation(node.operation).value} {_get_correct_id(node.input_right)};"
                            self.append_code(self.Sections.ALWAYS_BLOCK, line)

                        case Operation.GLOBAL_CONST_DECLARATION: pass # dont need to generate any text

                        case Operation.ARRAY_INDEX:
                            
                            load_store_node = None

                            for future_node in sorted_nodes[tick+1]:
                                if future_node.operation == (Operation.ARRAY_LOAD or Operation.ARRAY_STORE) and future_node.input_left.spirv_id == node.spirv_id:
                                    load_store_node = future_node
                            

                            assert load_store_node != None, f"failed to find a corresponding array load/store node in one tick ahead {tick} + 1 = {tick+1}"

                            # generate sv text based whether node is load/store

                            match load_store_node.operation:
                                case Operation.ARRAY_LOAD:
                                    assert not self.node_assembler.is_symbol_an_output(module, load_store_node.input_left.spirv_id), f"cannot load value from output port"

                                    # TODO: get width for int type, hardcoded for now
                                    self.append_code(self.Sections.INTERNAL, f"\tlogic [31:0] {load_store_node.spirv_id[1:]};")

                                    array_type_id = self.node_assembler.get_type_context_from_module(
                                        module,
                                        self.node_assembler.get_node(module, node.array_id).type_id # get array  node
                                    )

                                    array_max_size = self.node_assembler.get_node(module, array_type_id.array_dimension_id).data[0]
                                    array_index = self.node_assembler.get_node(module, node.array_index_id).data[0]

                                    # TODO: tuples
                                    assert type(array_max_size) is int, f"array_max_size should have been int but got {type(array_max_size)} instead"

                                    assert array_index < array_max_size, f"array_index was not less than array_max_size: {array_index} < {array_max_size}"

                                    # assign in body
                                    self.append_code(self.Sections.ALWAYS_BLOCK, f"\t\t{load_store_node.spirv_id[1:]} <= {node.array_id[1:]}[{array_index}];")

                                case Operation.ARRAY_STORE:
                                    raise Exception("TODO")
                                
                        case Operation.ARRAY_LOAD: pass
                            
                        case _:
                            raise Exception(f"unhandled node during systemverilog generation: {node}")

            self.append_code(self.Sections.ALWAYS_BLOCK, f"\tend")
            self.append_code(self.Sections.ASSIGNMENTS, "endmodule")