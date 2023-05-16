import options
import machine as m
import symbols as s
import type as t
import operators as o
import dataflow as d
import pyparsing as pp
from errors import TitanErrors
from typing import NamedTuple
# from pyparsing import ParseResults

def generate_spirv_asm(machine_object: m.Machine, symbol_table: s.SymbolTable):

    # checking if we have a top module/entry point defined
    # TODO: package this up in another function
    if machine_object.name_of_top_module == None:
        func_count = len(machine_object.functions)

        if func_count == 0:
            # raise Exception("no parsed source code to generate SPIR-V from", "no_source")
            raise Exception(TitanErrors.NO_PARSED_SOURCE_CODE.value, TitanErrors.NO_PARSED_SOURCE_CODE.name)
        elif func_count > 1:
            # raise Exception(f"undefined top module when there are {func_count} modules, use the -t option to set the top.", "no_top_set")
            raise Exception(TitanErrors.UNDEFINED_TOP_MODULE.value, TitanErrors.UNDEFINED_TOP_MODULE.name)
        else:
            machine_object.name_of_top_module = machine_object.functions[0].name

    del func_count

    spirv = m.SPIRV_ASM()

    spirv.append_code(
        spirv.Sections.CAPABILITY_AND_EXTENSION,
        "OpCapability Shader"
    )

    spirv.append_code(
        spirv.Sections.CAPABILITY_AND_EXTENSION,
        "OpMemoryModel Logical GLSL450"
    )

    entrypoint_param_list = ""

    for entry in machine_object.functions:
        for param in entry.params:
            id = f"%{param.parameter}"
            entrypoint_param_list += f" {id}"

        for returned in entry.returns:
            id = f"%{returned}"
            entrypoint_param_list += f" {id}"


    spirv.append_code(
        spirv.Sections.ENTRY_AND_EXEC_MODES,
        # TODO: this does not account for multiple functions!!!
        f"OpEntryPoint Fragment %{machine_object.name_of_top_module} \"{machine_object.name_of_top_module}\" {entrypoint_param_list}"
    )

    del entrypoint_param_list

    spirv.append_code(
        spirv.Sections.ENTRY_AND_EXEC_MODES,
        f"OpExecutionMode %{machine_object.name_of_top_module} OriginUpperLeft"
    )

    for symbol, info in symbol_table.content.items():
        t_ctx = spirv.TypeContext(info.datatype, None, False, False)
        
        if not spirv.type_exists(t_ctx):
            spirv.add_type(t_ctx, f"%type_{info.datatype.name}")

        spirv.append_code(
            spirv.Sections.DEBUG_STATEMENTS,
            f"OpName %{symbol} \"{symbol}\""
        )

        if info.operation == s.Operation.FUNCTION_OUT_VAR_PARAM:
            spirv.append_code(
                spirv.Sections.ANNOTATIONS,
                f"OpDecorate %{symbol} Location {spirv.location}"
            )
            spirv.location += 1

        if info.operation == s.Operation.FUNCTION_IN_VAR_PARAM:
            spirv.append_code(
                spirv.Sections.ANNOTATIONS,
                f"OpDecorate %{symbol} Location {spirv.location}"
            )

            spirv.append_code(
                spirv.Sections.ANNOTATIONS,
                f"OpDecorate %{symbol} Flat"
            )

            spirv.location += 1

    for t_ctx, id in spirv.declared_types.items():

        match t_ctx.primative_type:
            case t.DataType.INTEGER:
                spirv.append_code(
                    spirv.Sections.TYPES_CONSTS_VARS,
                    f"{id} = OpTypeInt 32 1"
                )

            case t.DataType.VOID:
                spirv.append_code(
                    spirv.Sections.TYPES_CONSTS_VARS,
                    f"{id} = OpTypeVoid"
                )

            case t.DataType.FLOAT:
                spirv.append_code(
                    spirv.Sections.TYPES_CONSTS_VARS,
                    f"{id} = OpTypeFloat 32"
                )

            case _:
                # raise Exception("got unknown type while trying to generate SPIR-V", "unknown_type")
                raise Exception(f"{TitanErrors.PARSED_UNKNOWN_TYPE.value} : {t_ctx} for {id}", TitanErrors.PARSED_UNKNOWN_TYPE.name)

    for symbol, info in symbol_table.content.items():
        if info.operation == s.Operation.FUNCTION_DECLARATION:
            func_type_id = f"%type_function_{info.datatype.name}"

            if not spirv.func_type_exists(info.datatype):
                spirv.add_func_type(info.datatype, func_type_id)

            type_id = spirv.get_type_id(spirv.TypeContext(info.datatype, None, False, False))
            spirv.append_code(
                spirv.Sections.TYPES_CONSTS_VARS,
                f"{func_type_id} = OpTypeFunction {type_id}"
            )

    # generate pointer types
    for symbol, info in symbol_table.content.items():
        
        match info.operation:
            case s.Operation.FUNCTION_IN_VAR_PARAM:
                # raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (function input variable parameter)", TitanErrors.NOT_IMPLEMENTED.name)
            
                ptr_id = f"%ptr_input_"

                match info.datatype:
                    case t.DataType.INTEGER:
                        ptr_id += info.datatype.name

                        t_ctx = spirv.TypeContext(t.DataType.INTEGER, t.StorageType.IN, False, True)

                        if not spirv.type_exists(t_ctx):
                            spirv.add_type(t_ctx, ptr_id)

                            spirv.append_code(
                                spirv.Sections.TYPES_CONSTS_VARS,
                                f"{ptr_id} = OpTypePointer Input {spirv.get_type_id(spirv.TypeContext(info.datatype, None, False, False))}"
                            )
                    case _:
                        raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (function input variable parameter datatype ({info.datatype}) declaration)", TitanErrors.NOT_IMPLEMENTED.name)

            case s.Operation.FUNCTION_OUT_VAR_PARAM:
                ptr_id = f"%ptr_output_"

                match info.datatype:
                    case t.DataType.INTEGER:
                        # check if ptr int exists as datatype
                        ptr_id += info.datatype.name
                        t_ctx = spirv.TypeContext(t.DataType.INTEGER, t.StorageType.OUT, False, True)
                        if not spirv.type_exists(t_ctx):
                            spirv.add_type(t_ctx, ptr_id)
                            spirv.append_code(
                                spirv.Sections.TYPES_CONSTS_VARS,
                                f"{ptr_id} = OpTypePointer Output {spirv.get_type_id(spirv.TypeContext(info.datatype, None, False, False))}"
                            )
                    case _:
                        # raise Exception("not implemented", "not_implemented")
                        raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (function output variable parameter datatype ({info.datatype}) declaration)", TitanErrors.NOT_IMPLEMENTED.name)
                    
            case s.Operation.VARIABLE_DECLARATION:
                ptr_id = f"%ptr_funcvar_"

                match info.datatype:
                    case t.DataType.INTEGER:
                        ptr_id += info.datatype.name
                        t_ctx = spirv.TypeContext(t.DataType.INTEGER, t.StorageType.FUNCTION_VAR, False, True)

                        if not spirv.type_exists(t_ctx):
                            spirv.add_type(t_ctx, ptr_id)
                            spirv.append_code(
                                spirv.Sections.TYPES_CONSTS_VARS,
                                f"{ptr_id} = OpTypePointer Function {spirv.get_type_id(spirv.TypeContext(info.datatype))}"
                            )
                    case _:
                        # raise Exception("not implemented", "not_implemented")
                        raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (variable datatype ({info.datatype}) declaration)", TitanErrors.NOT_IMPLEMENTED.name)

    for func in machine_object.functions:
        # TODO: the same for params

        print(f"SYMBOL TABLE: {symbol_table.content}")

        for input in func.params:
            # print(input)
            # print(input.parameter)

            if symbol_table.exists(input.parameter):
                info = symbol_table.get(input.parameter)
                print(info)

                match info.datatype:
                    case t.DataType.INTEGER:
                        id = spirv.get_type_id(spirv.TypeContext(t.DataType.INTEGER, t.StorageType.IN, False, True))

                        spirv.append_code(
                            spirv.Sections.TYPES_CONSTS_VARS,
                            f"%{input.parameter} = OpVariable {id} Input"
                        )


        for returned in func.returns:
            if symbol_table.exists(returned):
                info = symbol_table.get(returned)

                match info.datatype:
                    case t.DataType.INTEGER:
                        id = spirv.get_type_id(spirv.TypeContext(t.DataType.INTEGER, t.StorageType.OUT, False, True))

                        # TODO: need a way to store symbols and their spirv representation (link between symbols.py and machine.SPIRV_ASM)
                        spirv.append_code(
                            spirv.Sections.TYPES_CONSTS_VARS,
                            f"%{returned} = OpVariable {id} Output"
                        )

                    case _:
                        # raise Exception("not implemented", "not_implemented")
                        raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (returned variable type ({info.datatype}) id)", TitanErrors.NOT_IMPLEMENTED.name)



    def _extract_type(info):
        if info is None:
            # raise Exception("unable to extract type", "fail_type_extract")
            raise Exception(TitanErrors.TYPE_EXTRACT_FAILED.value, TitanErrors.TYPE_EXTRACT_FAILED.name)
        else:
            match type(info):
                case spirv.ConstContext:
                    return info.primative_type
                case s.Information:
                    return info.datatype.value
                case _:
                    # raise Exception("got unknown type", "unknown_type_while_extracting")
                    raise Exception(f"{TitanErrors.UNKNOWN_TYPE_EXTRACTED.value} ({info})", TitanErrors.UNKNOWN_TYPE_EXTRACTED.name)

    # TODO: move this outside of the generate_spirv_asm function
    def _eval_line(line):

        if isinstance(line, o.UnaryOp):
            type_of_operand = type(line.operands)

            # TODO: redundant?
            if line.operator == "-":
                if type_of_operand == (int or float):
                    temp_negate = line.operands * -1 # doing this in a temp var to mess up class

                    c_ctx = spirv.ConstContext(type_of_operand, temp_negate)
                    if not spirv.const_exists(c_ctx):
                        type_str = t.DataType(type_of_operand).name

                        # splice to remove negative sign, just in case spirv doesn't like those kinds of ids
                        spirv.add_const(c_ctx, f"%const_{type_str}_n{str(temp_negate)[1:]}")

                        prim_t_id = spirv.get_type_id(
                            spirv.TypeContext(
                                t.DataType(type_of_operand),
                                None, False, False
                            )
                        )

                        spirv.append_code(
                            spirv.Sections.TYPES_CONSTS_VARS,
                            f"{spirv.get_const_id(c_ctx)} = OpConstant {prim_t_id} {temp_negate}" 
                        )

                        # TODO: recursive function, so return the id
                    return spirv.get_const_id(c_ctx), c_ctx

                else:
                    # TODO
                    # use Op(S|F)Negate when dealing with variables
                    # raise Exception("got unexpected type whilst parsing arithmetic", "unexpected_type")
                    raise Exception(TitanErrors.UNKNOWN_TYPE_IN_ARITHMETIC.value, TitanErrors.UNKNOWN_TYPE_IN_ARITHMETIC.name)
            # ---- the unary op is only ever used when there is a negative value, redundant to have this here?
            # else:
            #     if type_of_operand == (int or float):
            #         c_ctx = spirv.ConstContext(type_of_operand, line.operands)

            #         if not spirv.const_exists(c_ctx):
            #             type_str = t.DataType(type_of_operand).name
            #             spirv.add_const(c_ctx, f"%const_{type_str}_{line.operands}")
            #             spirv.append_code(
            #                 spirv.Sections.TYPES_CONSTS_VARS,
            #                 f"{spirv.get_const_id(c_ctx)} = OpConstant {line.operands}"
            #             )
            #     else:
            #         # TODO
            #         raise Exception("got unexpected type whilst parsing arithmetic", "unexpected_type")

        elif isinstance(line, int):
            # getting an int means that its positive, cus otherwise it would have been wrapped in the UnaryOp class by the parser
            c_ctx = spirv.ConstContext(int, line)
            if not spirv.const_exists(c_ctx):
                type_str = t.DataType(type(line)).name
                
                prim_t_id = spirv.get_type_id(
                    spirv.TypeContext(
                        t.DataType(type(line)),
                        None, False, False
                    )
                )
                spirv.add_const(c_ctx, f"%const_{type_str}_{line}")

                spirv.append_code(
                    spirv.Sections.TYPES_CONSTS_VARS,
                    f"{spirv.get_const_id(c_ctx)} = OpConstant {prim_t_id} {line}"
                )
            return spirv.get_const_id(c_ctx), c_ctx
        
        elif isinstance(line, str):
            # gonna assume that this is a symbol
            if symbol_table.exists(line):
                return f"%{line}", symbol_table.get(line)
            else:
                # raise Exception("symbol does not exist!", "no_symbol")
                raise Exception(f"{TitanErrors.NON_EXISTENT_SYMBOL.value} ({line})", TitanErrors.NON_EXISTENT_SYMBOL.name)

        elif isinstance(line, o.BinaryOp):
            id_0, info_0 = _eval_line(line.operands[0])
            id_1, info_1 = _eval_line(line.operands[1])

            t_0 = _extract_type(info_0)
            t_1 = _extract_type(info_1)

            if t_0 is not t_1:
                # raise Exception("type mismatch", "type_mismatch")
                raise Exception(f"{TitanErrors.TYPE_MISMATCH.value} t_0 = {t_0}, t_1 = {t_1}", TitanErrors.TYPE_MISMATCH.name)    

            # print(f"line: {line}")
            # print(f"operator: {line.operator}")
            # print(f"\ta: {line.operands[0]} returns {id_0} with info {info_0} with type {t_0}")
            # print(f"\tb: {line.operands[1]} returns {id_1} with info {info_1} with type {t_1}")

            line_id = f"%titan_id_{spirv.id}"

            if not spirv.line_exists(line_id):
                spirv.add_line(line_id, t.DataType(t_0))

                opcode = "Op"

                if t_0 is int:
                    opcode += "I"
                    match line.operator:
                        case "+":
                            opcode += "Add"
                        case "-":
                            opcode += "Sub"
                        case "*":
                            opcode += "Mul"
                        case "/":
                            opcode = "OpSDiv"
                        case _:
                            # raise Exception("got unknown operator when trying to generate opcode", "unknown_operator")
                            raise Exception(f"{TitanErrors.UNKNOWN_OPERATOR_DURING_GENERATION.value} ({line.operator})", TitanErrors.UNKNOWN_OPERATOR_DURING_GENERATION.name)
                elif t_0 is float:
                    opcode += "F"
                    match line.operator:
                        case "+":
                            opcode += "Add"
                        case "-":
                            opcode += "Sub"
                        case "*":
                            opcode += "Mul"
                        case "/":
                            opcode += "Div"
                        case _:
                            # raise Exception("got unknown operator when trying to generate opcode", "unknown_operator")
                            raise Exception(f"{TitanErrors.UNKNOWN_OPERATOR_DURING_GENERATION.value} ({line.operator})", TitanErrors.UNKNOWN_OPERATOR_DURING_GENERATION.name)
                else:
                    # raise Exception("got unknown type when trying to generate opcode", "unknown_type")
                    raise Exception(f"{TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.value}", TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.name)
                        
                # we already checked if the types matches so it doesn't really matter if we mix its use
                prim_t_id_0 = spirv.get_type_id(
                    spirv.TypeContext(
                        t.DataType(t_0),
                        None,
                        False,
                        False
                    )
                )

                if symbol_table.exists(id_0[1:]):
                    # print(id_0[1:])
                    temp_id = f"%t_{id_0[1:]}"
                    spirv.append_code(
                        spirv.Sections.FUNCTIONS,
                        f"{temp_id} = OpLoad {prim_t_id_0} {id_0}"
                    )

                    id_0 = temp_id

                if symbol_table.exists(id_1[1:]):
                    # print(id_1[1:])
                    temp_id = f"%t_{id_1[1:]}"
                    spirv.append_code(
                        spirv.Sections.FUNCTIONS,
                        f"{temp_id} = OpLoad {prim_t_id_0} {id_1}"
                    )

                    id_1 = temp_id


                spirv.append_code(
                    spirv.Sections.FUNCTIONS,
                    f"{line_id} = {opcode} {prim_t_id_0} {id_0} {id_1}"
                )
                

            spirv.id += 1
            return line_id, info_0
    

    # start doing each function def and body eval
    for func in machine_object.functions:

        info = symbol_table.get(func.name)

        match info.datatype:
            case t.DataType.VOID:
                func_id = spirv.get_func_id(t.DataType.VOID)
                type_id = spirv.get_type_id(spirv.TypeContext(t.DataType.VOID, None, False, False))
                spirv.append_code(
                    spirv.Sections.FUNCTIONS,
                    f"%{func.name} = OpFunction {type_id} None {func_id}"
                )
            case _:
                # raise Exception("not implemented", "not_implemented")
                raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (function type ({info.datatype}) declaration)", TitanErrors.NOT_IMPLEMENTED.name)

        spirv.append_code(
            spirv.Sections.FUNCTIONS,
            f"%func_label_{func.name} = OpLabel"
        )

        # define in-function variables
        for symbol, info in symbol_table.content.items():
            if info.operation == s.Operation.VARIABLE_DECLARATION:

                type_id = spirv.get_type_id(
                    spirv.TypeContext(
                        info.datatype,
                        s.StorageType.FUNCTION_VAR,
                        False,
                        True
                    )
                )

                spirv.append_code(
                    spirv.Sections.FUNCTIONS,
                    f"%{symbol} = OpVariable {type_id} Function"
                )

        for entry in func.body:

            # TODO: maybe make a wrapper function so that we don't need to drop one of the return values?
            line_id, _ = _eval_line(entry[2])
            # print(f"line: {entry} has final evaluation id of {line_id}")

            if entry[1] == "=":
                opcode = "OpStore"

                spirv.append_code(
                    spirv.Sections.FUNCTIONS,
                    f"{opcode} %{entry[0]} {line_id}"
                )


        spirv.append_code(
            spirv.Sections.FUNCTIONS,
            "OpReturn"
        )

        spirv.append_code(
            spirv.Sections.FUNCTIONS,
            "OpFunctionEnd"
        )

    # debug
    # print()
    # print()
    # spirv.print_contents()
    machine_object.SPIRV_asm_obj = spirv
    # print()
    # print()
    # print(f"generated: {spirv.generated_lines}")
    # print()
    # print()
    # print(symbol_table.content)

    if options.Options.OUTPUT_SPIRV_ASM in machine_object.output_options:
        spirv.output_to_file(machine_object.name_of_top_module)


def test_parse_action(tokens):
    # print(f"CALLED {tokens}")

    print("called")
    for x in range(0, len(tokens)):
        for y in range(0, len(tokens[x])):
            # print(f"{x} {y}: {tokens[x][y]}")
            continue

    return None

def test_parse_action_statement(tokens):
    # print(f"statment test: {tokens}")
    return None


def _get_datatype_from_string(type_string):
    match type_string:
        case "int":
            return s.DataType.INTEGER
        case "float":
            return s.DataType.FLOAT
        case "bool":
            return s.DataType.BOOLEAN
        case _:
            raise Exception(f"{TitanErrors.UNEXPECTED.value} unexpected type {type_string}", TitanErrors.UNEXPECTED.name)            


def generate_symbols(machine_object: m.Machine, symbol_table: s.SymbolTable):

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
                    print(f"[WARN]: return value for {param} is {function.return_type} (multiple return types are not yet supported) (generate.generate_symbols line:492)")
                    
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
                        symbol_table.add(entry[0], s.Information(s.DataType.INTEGER, s.Operation.VARIABLE_DECLARATION))



                # print(entry.get_name('assignment'))



class _FunctionLocation(NamedTuple):
    start_pos: int
    end_pos: int
    name: str

def _get_spirv_function_locations(parsed_spirv):
    # TODO: figure out how to improve this
    line_no = fn_start = 0
    fn_name = ""
    fn_locations = []
    for line in parsed_spirv:
        match line.opcode:
            case "Function":
                fn_start = line_no
                fn_name = line.id[1:] # slice to remove '%'
            case "FunctionEnd":
                fn_locations.append(_FunctionLocation(fn_start, line_no, fn_name))
                fn_name = ""

        line_no += 1

    del fn_start, line_no, fn_name
    return fn_locations



# generates nodes and then generates text
def generate_verilog(parsed_spirv: pp.ParseResults):
    verilog = m.Verilog_ASM()               

    fn_name = ""
    fn_locations = _get_spirv_function_locations(parsed_spirv)

    # print(f"SPIRV: {parsed_spirv}")

    # deal with headers
    for x in range(0, fn_locations[0].start_pos):
        line = parsed_spirv[x]
        print(line)

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
                raise Exception(TitanErrors.NOT_IMPLEMENTED.value, TitanErrors.NOT_IMPLEMENTED.name)
            
            case "TypeBool":
                raise Exception(TitanErrors.NOT_IMPLEMENTED.value, TitanErrors.NOT_IMPLEMENTED.name)
            
    
    for fn_count in range(0, len(fn_locations)):
        fn = fn_locations[fn_count]

        # for pos in range()
        for pos in range(fn.start_pos, fn.end_pos + 1):
            line = parsed_spirv[pos]
            print(line)

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

                case _:
                    if line.opcode == "Function" or "Label" or "Return" or "FunctionEnd":
                        continue
                    else:
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


    print()
    verilog.generate_dot_graph()
    # print(verilog.declared_symbols)
    verilog.clean_graph()
    _generate_verilog_text(verilog)
    verilog.generate_dot_graph("clean_nodes")
    # print("t_a" in verilog.declared_symbols)


def _generate_verilog_text(v: m.Verilog_ASM):

    print(f"{v.content}\n\n{v.declared_symbols}\n\n{v.marked_symbols_for_deletion}\n\n")

    writer = m.Verilog_Text()

    writer.append_code(
        writer.Sections.MODULE_AND_PORTS,
        f"// generated by titan, dont modify anything otherwise it might break =)"
    )

    for fn in v.content.keys():

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
            print(tick)

            io_length_tracker = 0
            for node in sorted_nodes[tick]:
                print(f"\t{node}")

                if node.operation is s.Operation.GLOBAL_VAR_DECLARATION:
                    # this should only ever get hit on tick 0 but just in case
                    if tick != 0:
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
                            raise Exception(f"{TitanErrors.UNEXPECTED.value}\nnode: {node}", TitanErrors.UNEXPECTED.name)


                if node.operation in s.Operation_Type.ARITHMETIC:
                    if node.spirv_id not in v.declared_symbols:
                        # print("no")

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


                    def __get_correct_id(node: d.Node):
                        if node.operation in s.Operation_Type.GENERIC_CONSTANT_DECLARATION:
                            return node.data[0]
                        else:
                            return node.spirv_id[1:]


                    # line += f"{node.input_left.spirv_id[1:]} {op_symbol} {node.input_right.spirv_id[1:]};"

                    line += f"{__get_correct_id(node.input_left)} {op_symbol} {__get_correct_id(node.input_right)};"

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