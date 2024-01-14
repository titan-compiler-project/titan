import logging

import common.options as options
import machine as m
import common.symbols as s
import common.type as t
import common.operators as o
import dataflow as d
import pyparsing as pp
from common.errors import TitanErrors
from typing import NamedTuple
# from pyparsing import ParseResults

def _get_datatype_from_string(type_string):
    match type_string:
        case "int":
            return s.DataType.INTEGER
        case "float":
            return s.DataType.FLOAT
        case "bool":
            return s.DataType.BOOLEAN
        case _:
            logging.exception(f"{TitanErrors.UNEXPECTED.value} unexpected type {type_string} ({TitanErrors.UNEXPECTED.name})", exc_info=False)
            raise Exception(f"{TitanErrors.UNEXPECTED.value} unexpected type {type_string}", TitanErrors.UNEXPECTED.name)            


def generate_symbols(machine_object, symbol_table: s.SymbolTable):

    for function in machine_object.functions:
        
        # check if func is already declared
        if not symbol_table.exists(function.name):
            symbol_table.add(function.name, s.Information(s.DataType.VOID, s.Operation.FUNCTION_DECLARATION))

            # now that the function is declared, check its input params
            if len(function.params) > 0:
                for param in function.params:
                    # print(f"SYMBOL TABLE: PARAMS: {param} -- name: {param.parameter} with type {param.type}")
                    
                    if not symbol_table.exists(param.parameter):
                        # match param.type:
                        #     case "int":
                        #         datatype = s.DataType.INTEGER
                        #     case "float":
                        #         datatype = s.DataType.FLOAT
                        #     case "bool":
                        #         datatype = s.DataType.BOOLEAN
                        #     case _:
                        #         raise Exception(f"{TitanErrors.UNEXPECTED.value} (unexpected type {param.type})", TitanErrors.UNEXPECTED.name)

                        datatype = _get_datatype_from_string(param.type)

                        symbol_table.add(param.parameter, s.Information(datatype, s.Operation.FUNCTION_IN_VAR_PARAM))

                    # if not symbol_table.exists(param):
                    #     symbol_table.add(param, s.Information(s.DataType.INTEGER, s.Operation.FUNCTION_IN_VAR_PARAM))

            # check its output params
            if len(function.returns) > 0:
                for param in function.returns:
                    # print(f"[WARN]: return value for {param} is still assumed to be an integer. (generate.generate_symbols line:504)")
                    logging.warn(f"return value for {param} is {function.return_type} (multiple return types are not yet supported)")
                    
                    # if not symbol_table.exists(param):
                        # symbol_table.add(param, s.Information(s.DataType.INTEGER, s.Operation.FUNCTION_OUT_VAR_PARAM))


                    if not symbol_table.exists(param):
                        datatype = _get_datatype_from_string(function.return_type)

                        symbol_table.add(param, s.Information(datatype, s.Operation.FUNCTION_OUT_VAR_PARAM))


            # check body params
            for entry in function.body:
                # TODO: figure out why i can't access pyparsing results using the dot notation
                # this will fail on any other statements because it assumes
                #   every statement is an arithmetic one

                # checks if its an assignment, assuming that [0] is a var, [1] is = and [2] contains some operator
                if entry[1] == "=":
                    # print(entry)

                    if not symbol_table.exists(entry[0]):
                        # TODO: figure out why i'm using s.DataType.INTEGER -- maybe i should make an "unknown" type?
                        symbol_table.add(entry[0], s.Information(s.DataType.INTEGER, s.Operation.VARIABLE_DECLARATION))


class _FunctionLocation(NamedTuple):
    start_pos: int
    end_pos: int
    name: str

def _get_spirv_function_locations(parsed_spirv):
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
                fn_locations.append(_FunctionLocation(fn_start, line_no, fn_name))
                fn_name = ""
                _marked_end = True      

        line_no += 1

    if (_marked_start and _marked_end):
        return fn_locations
    else:
        logging.exception(f"failed to determine start/end point of function (start: {_marked_start}, end: {_marked_end})", exc_info=False)
        raise Exception(f"failed to determine start/end point of function (start: {_marked_start}, end: {_marked_end})")



# generates nodes and then generates text
def generate_verilog(parsed_spirv: pp.ParseResults):
    """ Generate SystemVerilog from parsed SPIR-V assembly.
    
        Loops through the parsed SPIR-V assembly, generating the corresponding SystemVerilog code.

        Args:
            parsed_spirv: Parsed SPIR-V assembly, in ``pyparsing.ParseResults`` format.

        Attributes:
            verilog: Verilog helper class.
            fn_name: Top-level function name.
            fn_locations: Line numbers of SPIR-V functions.
    """
    verilog = m.Verilog_ASM()               

    fn_name = ""
    fn_locations = _get_spirv_function_locations(parsed_spirv)

    # print(f"SPIRV: {parsed_spirv}")

    # deal with headers
    for x in range(0, fn_locations[0].start_pos):
        line = parsed_spirv[x]
        logging.debug(line)

        match line.opcode:
            case "EntryPoint":
                fn_name = line.opcode_args[2][1:-1]
                verilog.create_function(fn_name)
            
            case "Constant":
                if line.id not in verilog.declared_symbols:
                    verilog.declared_symbols.append(line.id)

                if verilog.type_exists_in_func(fn_name, line.opcode_args[0]):
                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                x,
                                line.id,
                                line.opcode_args[0],
                                None, None,
                                # s.Operation.CONSTANT_DECLARATION,
                                s.Operation.GLOBAL_CONST_DECLARATION,
                                [line.opcode_args[1]]
                            )
                        )
                    )
                else:
                    logging.exception(f"{TitanErrors.NON_EXISTENT_SYMBOL.value} ({line.opcode_args[0]} on line {x}) ({TitanErrors.NON_EXISTENT_SYMBOL.name})", exc_info=False)
                    raise Exception(f"{TitanErrors.NON_EXISTENT_SYMBOL.value} ({line.opcode_args[0]} on line {x})", TitanErrors.NON_EXISTENT_SYMBOL.name)
            
            case "Variable":
                if line.id not in verilog.declared_symbols:
                    verilog.declared_symbols.append(line.id)

                match line.opcode_args[1]:
                    case "Output":
                        verilog.add_output_to_function(fn_name, line.id[1:])
                        verilog.add_body_node_to_function(
                            fn_name,
                            d.Node(
                                d.NodeContext(
                                    x, line.id,
                                    verilog.get_primative_type_id_from_id(fn_name, line.opcode_args[0]),
                                    None, None, 
                                    # s.Operation.VARIABLE_DECLARATION
                                    s.Operation.GLOBAL_VAR_DECLARATION,
                                    [s.Operation.FUNCTION_OUT_VAR_PARAM]
                                )
                            )
                        )

                    case "Input":
                        verilog.add_input_to_function(fn_name, line.id[1:])

                        verilog.add_body_node_to_function(
                            fn_name,
                            d.Node(
                                d.NodeContext(
                                    x, line.id,
                                    verilog.get_primative_type_id_from_id(fn_name, line.opcode_args[0]),
                                    None, None, s.Operation.GLOBAL_VAR_DECLARATION,
                                    [s.Operation.FUNCTION_IN_VAR_PARAM]
                                )
                            )
                        )

                        # raise Exception(TitanErrors.NOT_IMPLEMENTED.value, TitanErrors.NOT_IMPLEMENTED.name)
            
            case "TypePointer":
                verilog.add_type_context_to_function(
                    fn_name,
                    line.id, # %ptr_something_something id
                    m._VerilogTypeContext(
                        verilog.get_datatype_from_id(fn_name, line.opcode_args[1]), # returns types.DataType
                        [], True, line.opcode_args[1] # line.opcode_args[1] = %type_something (primative)
                    )
                )
            
            case "TypeInt":
                verilog.add_type_context_to_function(
                    fn_name,
                    line.id,
                    m._VerilogTypeContext(
                        t.DataType.INTEGER,
                        # line.id,
                        line.opcode_args.as_list()
                    )
                )
            
            case "TypeFloat":
                logging.exception(f"{TitanErrors.NOT_IMPLEMENTED.value} TypeFloat ({TitanErrors.NOT_IMPLEMENTED.name})", exc_info=False)
                raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} TypeFloat", TitanErrors.NOT_IMPLEMENTED.name)
            
            case "TypeBool":
                verilog.add_type_context_to_function(
                    fn_name, line.id,
                    m._VerilogTypeContext(
                        t.DataType.BOOLEAN, [], False, ""
                    )
                )
            
    
    for fn_count in range(0, len(fn_locations)):
        fn = fn_locations[fn_count]

        # for pos in range()
        for pos in range(fn.start_pos, fn.end_pos + 1):
            line = parsed_spirv[pos]
            logging.debug(line)

            match line.opcode:

                case "Variable":
                    if line.id not in verilog.declared_symbols:
                        verilog.declared_symbols.append(line.id)

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, 
                                verilog.get_primative_type_id_from_id(fn_name, line.opcode_args[0]),
                                None, None, s.Operation.VARIABLE_DECLARATION
                            )
                        )
                    )


                case "Store":
                    # print(verilog.get_node(fn_name, line.opcode_args[0]))
                    # storage_node = verilog.get_node(fn_name, line.opcode_args[0])

                    # if verilog.does_node_exist()
                    # print(f"---fn_name {fn_name} arg {line.opcode_args[1]}")

                    if verilog.does_node_exist(fn_name, line.opcode_args[1]):
                        value_node = verilog.get_node(fn_name, line.opcode_args[1])

                        verilog.modify_node(fn_name, line.opcode_args[0], 0, value_node, s.Operation.STORE)
                    else:
                        logging.exception(f"does not exist {fn_name} {line.opcode_args[1]}", exc_info=False)
                        raise Exception(f"DOES NOT EXIST {fn_name} {line.opcode_args[1]}")
                    

                case "Load":
                    value_node = verilog.get_node(fn_name, line.opcode_args[1])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0], value_node, None,
                                s.Operation.LOAD
                            )
                        )
                    )

                # TODO: these arithmetic operations practically follow the same format, is there a way to minimise this repeating code?
                case "IAdd":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.ADD
                            )
                        )
                    )

                case "ISub":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.SUB
                            )
                        )
                    )

                    # raise Exception(TitanErrors.NOT_IMPLEMENTED.value, TitanErrors.NOT_IMPLEMENTED.name)
                case "IMul":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.MULT
                            )
                        )
                    )
                    # raise Exception(TitanErrors.NOT_IMPLEMENTED.value, TitanErrors.NOT_IMPLEMENTED.name)

                case "SDiv":
                    # print(f"--------{line.opcode_args}")
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.DIV
                            )
                        )
                    )

                case "Select":
                        #                          0           1               2             3
                        # %result_id = OpSelect %type_id %comparison_id %true_value_id %false_value_id

                        l = verilog.get_node(fn_name, line.opcode_args[2])
                        r = verilog.get_node(fn_name, line.opcode_args[3])

                        compare_node = verilog.get_node(fn_name, line.opcode_args[1])
                        # print(f"-[generate_verilog] [select case for OpSelect] {compare_node}")

                        verilog.add_body_node_to_function(
                            fn_name,
                            d.Node(
                                d.NodeContext(
                                    pos, line.id, line.opcode_args[0],
                                    l, r, s.Operation.DECISION, [compare_node], True
                                )
                            )
                        )


                # these comparison functions are practicaly the same except for the operation that gets added
                case "IEqual" | "FOrdEqual":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.EQUAL_TO
                            )
                        )
                    )

                case "INotEqual" | "FOrdNotEqual":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.NOT_EQUAL_TO
                            )
                        )
                    )
                
                case "SLessThan" | "FOrdLessThan":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.LESS_THAN
                            )
                        )
                    )
                
                case "SLessThanEqual" | "FOrdLessThanEqual":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.LESS_OR_EQ
                            )
                        )
                    )
                
                case "SGreaterThan" | "FOrdGreaterThan":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.GREATER_THAN
                            )
                        )
                    )

                case "SGreaterThanEqual" | "FOrdGreaterThanEqual":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.GREATER_OR_EQ
                            )
                        )
                    )

                case "ShiftLeftLogical":
                    l = verilog.get_node(fn_name, line.opcode_args[1]) # thing to shift
                    r = verilog.get_node(fn_name, line.opcode_args[2]) # how much to shift by

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.SHIFT_LEFT
                            )
                        )
                    )

                # TODO: this might need to handle "OpShiftRightArithmetic"
                case "OpShiftRightLogical":
                    l = verilog.get_node(fn_name, line.opcode_args[1])
                    r = verilog.get_node(fn_name, line.opcode_args[2])

                    verilog.add_body_node_to_function(
                        fn_name,
                        d.Node(
                            d.NodeContext(
                                pos, line.id, line.opcode_args[0],
                                l, r, s.Operation.SHIFT_RIGHT
                            )
                        )
                    )
                    


                case _:
                    # TODO: make this less ugly
                    if line.opcode == "Function" or line.opcode == "Label" or line.opcode == "Return" or line.opcode == "FunctionEnd":
                        continue
                    else:
                        logging.exception(f"{TitanErrors.UNKNOWN_SPIRV_OPCODE.value} ({line.opcode}) ({TitanErrors.UNKNOWN_SPIRV_OPCODE.name})", exc_info=False)
                        raise Exception(f"{TitanErrors.UNKNOWN_SPIRV_OPCODE.value} ({line.opcode})", TitanErrors.UNKNOWN_SPIRV_OPCODE.name) 





    
    # print()
    # print(verilog.content)

    # print()
    # for k, v in verilog.content.items():
    #     print(f"types: {v.types}")
    #     print(f"inputs: {v.inputs}")
    #     print(f"outputs: {v.outputs}\n")
    #     # print(f"body_nodes: {v.body_nodes}")
    #     for a, b in v.body_nodes.items():
    #         print(f"key: {a}")
    #         for node in b:
    #             print(f"\t{node}")
    #         print()


    # print()
    verilog.generate_dot_graph()
    # _generate_verilog_text(verilog)
    print(verilog.declared_symbols)
    verilog.clean_graph()
    verilog.generate_dot_graph("clean_nodes")
    _generate_verilog_text(verilog)
    # print("t_a" in verilog.declared_symbols)


def _generate_verilog_text(v: m.Verilog_ASM):
    """ Converts the nodes into actual Verilog code.

        Also generates a Yosys script to generate a graph of the module
        ``read_verilog -sv {fn}.sv; proc; opt; memory; opt; show;``
    
        Args:
            v: Verilog object containing body nodes.
    """

    def __get_correct_id(node: d.Node):
        if node.operation in s.Operation_Type.GENERIC_CONSTANT_DECLARATION:
            return node.data[0]
        else:
            return node.spirv_id[1:]

    logging.debug(f"content: {v.content}")
    logging.debug(f"declared symbols: {v.declared_symbols}")
    logging.debug(f"marked symbols for deletion: {v.marked_symbols_for_deletion}")

    writer = m.Verilog_Text()

    writer.append_code(
        writer.Sections.MODULE_AND_PORTS,
        f"// generated by titan, dont modify anything otherwise it might break =)"
    )

    for fn in v.content.keys():
    # for i in range(len(v.content.keys())):
        # fn = list(v.content.keys())[i]

        writer.append_code(
            writer.Sections.MODULE_AND_PORTS,
            f"module {fn} ("
        )

        writer.append_code(
            writer.Sections.MODULE_AND_PORTS,
            f"\tinput wire clock,"
        )

        writer.append_code(
            writer.Sections.ALWAYS_BLOCK,
            f"\talways_ff @ (posedge clock) begin"
        )

        fn_data = v.content[fn]

        # print(f"types: {fn_data.types}\n\ninputs: {fn_data.inputs}\toutputs: {fn_data.outputs}\n\nbody nodes: {fn_data.body_nodes}")

        sorted_nodes = v._sort_body_nodes_by_tick(fn)

        # for tick in sorted_nodes.keys():
        for tick in range(len(sorted_nodes.keys())):
            logging.debug(f"tick {tick} has {len(sorted_nodes[tick])} nodes")

            io_length_tracker = 0
            # for node in sorted_nodes[tick]:
            # print(f"--=-=-=-=-= LENGTH: {len(sorted_nodes[tick])}")
            for x in range(len(sorted_nodes[tick])):
                node = sorted_nodes[tick][x]
                logging.debug(f"\t{node}")

                if node.operation is s.Operation.GLOBAL_VAR_DECLARATION:
                    # this should only ever get hit on tick 0 but just in case
                    if tick != 0:
                        logging.exception(f"variable declaration outside of tick 0 ({TitanErrors.UNEXPECTED.name})", exc_info=False)
                        raise Exception("variable declaration outside of tick 0", TitanErrors.UNEXPECTED.name)

                    type_ctx = v.get_type_context_from_function(fn, node.type_id)
                    width = int(type_ctx.data[0])

                    # ender = "\n);" if io_length_tracker == len(sorted_nodes[tick]) - 1 else ","
                    ender = "\n);" if io_length_tracker == (len(fn_data.inputs) + len(fn_data.outputs)) - 1 else ","

                    match node.data[0]:
                        case s.Operation.FUNCTION_IN_VAR_PARAM:
                            writer.append_code(
                                writer.Sections.MODULE_AND_PORTS,
                                f"\tinput logic [{width-1}:0] {node.spirv_id[1:]}{ender}"
                            )

                        case s.Operation.FUNCTION_OUT_VAR_PARAM:
                            writer.append_code(
                                writer.Sections.MODULE_AND_PORTS,
                                f"\toutput wire [{width-1}:0] {node.spirv_id[1:]}{ender}"
                            )

                    io_length_tracker += 1

                
                if node.operation is s.Operation.STORE and len(node.data) == 1:
                    match node.data[0]:
                        case s.Operation.FUNCTION_OUT_VAR_PARAM:
                            writer.append_code(
                                writer.Sections.ASSIGNMENTS,
                                f"\tassign {node.spirv_id[1:]} = {node.input_left.spirv_id[1:]};"
                            )
                        case _:
                            logging.exception(f"{TitanErrors.UNEXPECTED.value} node: {node} ({TitanErrors.UNEXPECTED.name})", exc_info=False)
                            raise Exception(f"{TitanErrors.UNEXPECTED.value}\nnode: {node}", TitanErrors.UNEXPECTED.name)


                if node.operation in s.Operation_Type.ARITHMETIC:
                    if node.spirv_id not in v.declared_symbols:

                        # update this with a proper function
                        width = int(v.get_type_context_from_function(fn, node.type_id).data[0])

                        writer.append_code(
                            writer.Sections.INTERNAL,
                            f"\tlogic [{width-1}:0] {node.spirv_id[1:]};"
                        )

                    line = f"\t\t{node.spirv_id[1:]} <= "
                    op_symbol = ""

                    match node.operation:
                        case s.Operation.ADD:
                            op_symbol = "+"
                        case s.Operation.SUB:
                            op_symbol = "-"
                        case s.Operation.MULT:
                            op_symbol = "*"
                        case s.Operation.DIV:
                            op_symbol = "/"


                    # line += f"{node.input_left.spirv_id[1:]} {op_symbol} {node.input_right.spirv_id[1:]};"

                    line += f"{__get_correct_id(node.input_left)} {op_symbol} {__get_correct_id(node.input_right)};"

                    writer.append_code(
                        writer.Sections.ALWAYS_BLOCK,
                        line
                    )

                if node.operation in s.Operation_Type.COMPARISON:
                    defer_node_creation = False

                    logging.debug(f"checking 1 tick ahead...({tick} + 1 = {tick+1})")

                    for future_node in sorted_nodes[tick+1]:
                        if defer_node_creation:
                            break

                        if future_node.operation == s.Operation.DECISION:
                            if future_node.data[0].spirv_id == node.spirv_id:
                                logging.debug("found a reference")
                                defer_node_creation = True

                            else:
                                logging.debug("no reference found")

                    logging.debug(f"stopped checking 1 tick ahead...\n")

                    if not defer_node_creation:
                        # TODO: add node stuff here - need to make the logic thingy and then add a line somehow idk

                        # 1. make logic value
                        # 2. assign logic value with comparison operation

                        # logging.error(f"{v.get_type_context_from_function(fn, node.type_id)}")
                        # width = int(v.get_type_context_from_function(fn, node.type_id).data[0])
                     
                        writer.append_code(
                           writer.Sections.INTERNAL,
                            f"\tlogic {node.spirv_id[1:]};"
                        )

                        # TODO: need to get logical operators not bitwise... 
                        compare_op = s.Operation(node.operation).value
                        line = f"\t\t{node.spirv_id[1:]} <= {__get_correct_id(node.input_left)} {compare_op} {__get_correct_id(node.input_right)};"

                        writer.append_code(
                            writer.Sections.ALWAYS_BLOCK,
                            line
                        )


                
                if node.operation is s.Operation.DECISION:
                    # paired_decision_node = sorted_nodes[tick+1][x+1]
                    logging.debug(f"in decision: {node}")
                    comparison_node = node.data[0]

                    # comparison node holds the comparison operator, and the comparison itself
                    # the paried decision node holds the expected results

                    # so i.e. c = a >= 10 ? 5 : 0 would require the comparison node to construct a >= 10
                    # and the paried decision node for the ? 5 : 0 section

                    # we dont want to create a logic value for the comparison node because that can just be abstracted away
                    # so instead we will create the logic value for the decision node

                    width = int(v.get_type_context_from_function(fn, node.type_id).data[0])

                    writer.append_code(
                        writer.Sections.INTERNAL,
                        f"\tlogic [{width-1}:0] {node.spirv_id[1:]};"
                    )

                    compare_op = s.Operation(comparison_node.operation).value

                    # TODO: __get_correct_id(node) was returning the string representation of the node instead, why?
                    line = f"\t\t{node.spirv_id[1:]} <= {__get_correct_id(comparison_node.input_left)} {compare_op} {__get_correct_id(comparison_node.input_right)} ? {__get_correct_id(node.input_left)} : {__get_correct_id(node.input_right)};"

                    writer.append_code(
                        writer.Sections.ALWAYS_BLOCK,
                        line
                    )

                if node.operation in s.Operation_Type.BITWISE:

                    width = int(v.get_type_context_from_function(fn, node.type_id).data[0])

                    writer.append_code(
                        writer.Sections.INTERNAL,
                        f"\tlogic [{width-1}:0] {node.spirv_id[1:]}"
                    )

                    line = f"\t\t{__get_correct_id(node)} <= {__get_correct_id(node.input_left)} {s.Operation(node.operation).value} {__get_correct_id(node.input_right)};"

                    writer.append_code(
                        writer.Sections.ALWAYS_BLOCK,
                        line
                    )

        # writer.append_code(
        #     writer.Sections.MODULE_AND_PORTS,
        #     ")"
        # )

        writer.append_code(
            writer.Sections.ALWAYS_BLOCK,
            f"\tend"
        )

        writer.append_code(
            writer.Sections.ASSIGNMENTS,
            "endmodule"
        )

    print()
    writer.print_contents()
    writer.output_to_file(fn)

    with open(f"yosys_script_{fn}.txt", "w+") as f:
        f.write(f"read_verilog -sv {fn}.sv; proc; opt; memory; opt; show;")