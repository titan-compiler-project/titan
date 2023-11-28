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

def generate_spirv_asm(machine_object: m.Machine, symbol_table: s.SymbolTable):

    # checking if we have a top module/entry point defined
    # TODO: package this up in another function
    if machine_object.name_of_top_module == None:
        func_count = len(machine_object.functions)

        if func_count == 0:
            # raise Exception("no parsed source code to generate SPIR-V from", "no_source")
            logging.exception(f"{TitanErrors.NO_PARSED_SOURCE_CODE.value} ({TitanErrors.NO_PARSED_SOURCE_CODE.name})", exc_info=False)
            raise Exception(TitanErrors.NO_PARSED_SOURCE_CODE.value, TitanErrors.NO_PARSED_SOURCE_CODE.name)
        elif func_count > 1:
            # raise Exception(f"undefined top module when there are {func_count} modules, use the -t option to set the top.", "no_top_set")
            logging.exception(f"{TitanErrors.UNDEFINED_TOP_MODULE.value} ({TitanErrors.UNDEFINED_TOP_MODULE.name})", exc_info=False)
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

    # TODO: might need a way to change the bit size for types
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
                logging.exception(f"{TitanErrors.PARSED_UNKNOWN_TYPE.value} : {t_ctx} for {id} ({TitanErrors.PARSED_UNKNOWN_TYPE.name})", exc_info=False)
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
                        logging.exception(f"{TitanErrors.NOT_IMPLEMENTED} (function input variable parameter datatype ({info.datatype}) declaration) ({TitanErrors.NOT_IMPLEMENTED.name})", exc_info=False)
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
                        logging.exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (function output variable parameter datatype ({info.datatype}) declaration) ({TitanErrors.NOT_IMPLEMENTED.name})", exc_info=False)
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
                        logging.exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (variable datatype ({info.datatype}) declaration) ({TitanErrors.NOT_IMPLEMENTED.name})", exc_info=False)
                        raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (variable datatype ({info.datatype}) declaration)", TitanErrors.NOT_IMPLEMENTED.name)

    for func in machine_object.functions:
        # TODO: the same for params

        logging.debug(f"SYMBOL TABLE: {symbol_table.content}")

        for input in func.params:
            # print(input)
            # print(input.parameter)

            if symbol_table.exists(input.parameter):
                info = symbol_table.get(input.parameter)
                logging.debug(info)

                match info.datatype:
                    case t.DataType.INTEGER:
                        id = spirv.get_type_id(spirv.TypeContext(t.DataType.INTEGER, t.StorageType.IN, False, True))

                        spirv.append_code(
                            spirv.Sections.TYPES_CONSTS_VARS,
                            f"%{input.parameter} = OpVariable {id} Input"
                        )

                    case _:
                        logging.exception(f"{TitanErrors.UNEXPECTED.value}: generate_spirv_asm got an unhandled datatype ({info.datatype}) ({TitanErrors.UNEXPECTED.name})", exc_info=False)
                        raise Exception(f"{TitanErrors.UNEXPECTED.value}: generate_spirv_asm got an unhandled datatype ({info.datatype})", TitanErrors.UNEXPECTED.name)


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
                        logging.exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (returned variable type ({info.datatype}) id) ({TitanErrors.NOT_IMPLEMENTED.name})", exc_info=False)
                        raise Exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (returned variable type ({info.datatype}) id)", TitanErrors.NOT_IMPLEMENTED.name)



    def _extract_type(info):
        if info is None:
            # raise Exception("unable to extract type", "fail_type_extract")
            logging.exception(f"{TitanErrors.TYPE_EXTRACT_FAILED.value} ({TitanErrors.TYPE_EXTRACT_FAILED.name})", exc_info=False)
            raise Exception(TitanErrors.TYPE_EXTRACT_FAILED.value, TitanErrors.TYPE_EXTRACT_FAILED.name)
        else:
            match type(info):
                case spirv.ConstContext:
                    return info.primative_type
                case s.Information:
                    return info.datatype.value
                case _:
                    # raise Exception("got unknown type", "unknown_type_while_extracting")
                    logging.exception(f"{TitanErrors.UNKNOWN_TYPE_EXTRACTED.value} ({info}) ({TitanErrors.UNKNOWN_TYPE_EXTRACTED.name})", exc_info=False)
                    raise Exception(f"{TitanErrors.UNKNOWN_TYPE_EXTRACTED.value} ({info})", TitanErrors.UNKNOWN_TYPE_EXTRACTED.name)

    # TODO: move this outside of the generate_spirv_asm function
    def _eval_line(line):

        logging.debug(f"[_eval_line]: line is type {type(line)} containing {line}")

        if isinstance(line, o.TernaryCondOp):
            # check if bool datatype has been created
            t_ctx = spirv.TypeContext(t.DataType.BOOLEAN)
            if not spirv.type_exists(t_ctx):
                spirv.add_type(t_ctx, f"%type_{t.DataType.BOOLEAN.name}")

                spirv.append_code(
                    spirv.Sections.TYPES_CONSTS_VARS,
                    f"{spirv.get_type_id(t_ctx)} = OpTypeBool"
                )
            
            a = true_val_id, true_val_ctx = _eval_line(line.true_val)
            b = false_val_id, false_val_ctx = _eval_line(line.false_val)
            c = cond_id, cond_ctx = _eval_line(line.condition)

            selector_line_id = f"%titan_id_{spirv.id}"

            if not spirv.line_exists(selector_line_id):
                spirv.add_line(selector_line_id, cond_ctx.datatype)

            true_val_type = _extract_type(true_val_ctx)
            false_val_type = _extract_type(false_val_ctx)

            # sanity check
            if true_val_type != false_val_type:
                logging.exception(f"{TitanErrors.TYPE_MISMATCH.value} value {true_val_ctx} with id {true_val_id} does not match value {false_val_ctx} with id {false_val_id} ({TitanErrors.TYPE_MISMATCH.name})", exc_info=False)
                raise Exception(f"{TitanErrors.TYPE_MISMATCH.value} value {true_val_ctx} with id {true_val_id} does not match value {false_val_ctx} with id {false_val_id}")


            target_type_id = spirv.get_type_id(spirv.TypeContext(t.DataType(true_val_type)))

            spirv.append_code(
                spirv.Sections.FUNCTIONS,
                f"{selector_line_id} = OpSelect {target_type_id} {cond_id} {true_val_id} {false_val_id}"
            )

            spirv.id += 1
            return selector_line_id, spirv.TypeContext(t.DataType(true_val_type))
            

        elif isinstance(line, o.UnaryOp):
            type_of_operand = type(line.operands)

            # TODO: redundant?
            if line.operator == "-":
                if type_of_operand == (int or float):
                    temp_negate = line.operands * -1 # doing this in a temp var to avoid messing up the class

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
                    logging.exception(f"{TitanErrors.UNKNOWN_TYPE_IN_ARITHMETIC.value} ({TitanErrors.UNKNOWN_TYPE_IN_ARITHMETIC.name})", exc_info=False)
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

        elif isinstance(line, int) or isinstance(line, float):
            # getting an int means that its positive, cus otherwise it would have been wrapped in the UnaryOp class by the parser
            
            c_ctx = spirv.ConstContext(type(line), line) # create context using line and its type
            if not spirv.const_exists(c_ctx):
                type_str = t.DataType(type(line)).name


                # set "is_constant" to false because we want the primative type, and that isn't applied to the original type 
                primative_type_ctx = spirv.TypeContext(
                    t.DataType(type(line)), None, False, False
                )

                # this should handle unexpected constants
                if not spirv.type_exists(primative_type_ctx):
                    spirv.add_type(primative_type_ctx, f"%type_{type_str}")


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
                logging.exception(f"{TitanErrors.NON_EXISTENT_SYMBOL.value} ({line}) ({TitanErrors.NON_EXISTENT_SYMBOL.name})", exc_info=False)
                raise Exception(f"{TitanErrors.NON_EXISTENT_SYMBOL.value} ({line})", TitanErrors.NON_EXISTENT_SYMBOL.name)

        elif isinstance(line, o.BinaryOp):
            id_0, info_0 = _eval_line(line.operands[0])
            id_1, info_1 = _eval_line(line.operands[1])

            t_0 = _extract_type(info_0)
            t_1 = _extract_type(info_1)

            if t_0 is not t_1:
                if line.operator not in s.LiteralSymbolGroup.BITWISE:
                    logging.exception(f"{TitanErrors.TYPE_MISMATCH.value} t_0 = {t_0}, t_1 = {t_1} on line {line} ({TitanErrors.TYPE_MISMATCH.name})", exc_info=False)
                    raise Exception(f"{TitanErrors.TYPE_MISMATCH.value} t_0 = {t_0}, t_1 = {t_1} on line {line}", TitanErrors.TYPE_MISMATCH.name)    

            # print(f"line: {line}")
            # print(f"operator: {line.operator}")
            # print(f"\ta: {line.operands[0]} returns {id_0} with info {info_0} with type {t_0}")
            # print(f"\tb: {line.operands[1]} returns {id_1} with info {info_1} with type {t_1}")

            line_id = f"%titan_id_{spirv.id}"

            if not spirv.line_exists(line_id):
                spirv.add_line(line_id, t.DataType(t_0))

                opcode = None
                
                # special_opset is set to the operation type just incase the opcode needs to be treated differently
                special_opset = None
                compare_op = None


                # begin matching the operator
                match line.operator:

                    # handle arithmetic (see symbols.py)
                    case line.operator if line.operator in s.LiteralSymbolGroup.ARITHMETIC:
                        op = s.Operation(line.operator)

                        # handle different types
                        if t_0 is int:
                            match op:
                                case s.Operation.ADD:
                                    opcode = "OpIAdd"
                                case s.Operation.SUB:
                                    opcode = "OpISub"
                                case s.Operation.MULT:
                                    opcode = "OpIMul"
                                case s.Operation.DIV:
                                    opcode = "OpSDiv"
                        elif t_0 is float:
                            match op:
                                case s.Operation.ADD:
                                    opcode = "OpFAdd"
                                case s.Operation.SUB:
                                    opcode = "OpFSub"
                                case s.Operation.MULT:
                                    opcode = "OpFMult"
                                case s.Operation.DIV:
                                    opcode = "OpFDiv"
                        else:
                            logging.exception(f"{TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.value} for arithmetic operator ({TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.name})", exc_info=False)
                            raise Exception(f"{TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.value} for arithmetic operator", TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.name)

                    # handle comparison
                    case line.operator if line.operator in s.LiteralSymbolGroup.COMPARISON:
                        special_opset = s.Operation_Type.COMPARISON
                        compare_op = s.Operation(line.operator)

                        if t_0 is int:
                            match compare_op:
                                case s.Operation.EQUAL_TO:
                                    opcode = "OpIEqual"
                                case s.Operation.NOT_EQUAL_TO:
                                    opcode = "OpINotEqual"
                                case s.Operation.LESS_THAN:
                                    opcode = "OpSLessThan"
                                case s.Operation.LESS_OR_EQ:
                                    opcode = "OpSLessThanEqual"
                                case s.Operation.GREATER_THAN:
                                    opcode = "OpSGreaterThan"
                                case s.Operation.GREATER_OR_EQ:
                                    opcode = "OpSGreaterThanEqual"
                        elif t_0 is float:
                            # there's ordered and unordered comparisons, not 100% on the differences so we'll be sticking to ordered for now
                            # https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html#OpFOrdEqual
                            # https://stackoverflow.com/questions/8627331/what-does-ordered-unordered-comparison-mean

                            match compare_op:
                                case s.Operation.EQUAL_TO:
                                    opcode = "OpFOrdEqual"
                                case s.Operation.NOT_EQUAL_TO:
                                    opcode = "OpFOrdNotEqual"
                                case s.Operation.LESS_THAN:
                                    opcode = "OpFOrdLessThan"
                                case s.Operation.LESS_OR_EQ:
                                    opcode = "OpFOrdLessThanEqual"
                                case s.Operation.GREATER_THAN:
                                    opcode = "OpFOrdGreaterThan"
                                case s.Operation.GREATER_OR_EQ:
                                    opcode = "OpFOrdGreaterThanEqual"

                        else:
                            logging.exception(f"{TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.value} for comparison operator ({TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.name})", exc_info=False)
                            raise Exception(f"{TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.value} for comparison operator", TitanErrors.UNKNOWN_TYPE_DURING_GENERATION.name)

                    case line.operator if line.operator in s.LiteralSymbolGroup.BITWISE:

                        if t_0 is float:
                            logging.exception(f"{TitanErrors.BAD_TYPES.value}: bitwise shift operators require the result variable to be of type integer ({TitanErrors.BAD_TYPES.name})", exc_info=False)
                            raise Exception(f"{TitanErrors.BAD_TYPES.value}: bitwise shift operators require the result variable to be of type integer", TitanErrors.BAD_TYPES.name)

                        if t_1 is float:
                            logging.exception(f"{TitanErrors.BAD_TYPES.value}: bitwise shift value must be of type integer ({TitanErrors.BAD_TYPES.name})", exc_info=False)
                            raise Exception(f"{TitanErrors.BAD_TYPES.value}: bitwise shift value must be of type integer", TitanErrors.BAD_TYPES.name)
                        
                        special_opset = s.Operation_Type.BITWISE
                        op = s.Operation(line.operator)

                        match op:
                            case s.Operation.SHIFT_LEFT:
                                opcode = "OpShiftLeftLogical"
                            case s.Operation.SHIFT_RIGHT:
                                # there's two options in SPIR-V: OpShiftRightLogical and OpShiftRightArithmetic
                                # https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html#OpShiftRightLogical
                                # we'll be using OpShiftRightArithmetic in the SPIR-V to keep the sign in case it gets run, but it will be interpreted as OpShiftRightLogical in Verilog
                                opcode = "OpShiftRightArithmetic"

                    case _:
                        logging.exception(f"{TitanErrors.UNKNOWN_OPERATOR_DURING_GENERATION.value} - failed to match line operator {line.operator} during generation ({TitanErrors.UNKNOWN_OPERATOR_DURING_GENERATION.name})", exc_info=False)
                        raise Exception(f"{TitanErrors.UNKNOWN_OPERATOR_DURING_GENERATION.value} - failed to match line operator {line.operator} during generation", TitanErrors.UNKNOWN_OPERATOR_DURING_GENERATION.name)
                        
                # we already checked if the types matches so it doesn't really matter if we mix its use
                prim_t_id_0 = spirv.get_type_id(
                    spirv.TypeContext(
                        t.DataType(t_0), None, False, False
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

                # special logic in case we are dealing with comparison operators
                if special_opset is s.Operation_Type.COMPARISON:
                    bool_id = spirv.get_type_id(spirv.TypeContext(t.DataType.BOOLEAN))

                    spirv.append_code(
                        spirv.Sections.FUNCTIONS,
                        f"{line_id} = {opcode} {bool_id} {id_0} {id_1}"
                    )
                    
                    info_0 = s.Information(t.DataType.BOOLEAN, compare_op)

                else:
                    
                    spirv.append_code(
                        spirv.Sections.FUNCTIONS,
                        f"{line_id} = {opcode} {prim_t_id_0} {id_0} {id_1}"
                    )


            spirv.id += 1
            return line_id, info_0
        
        else:
            logging.exception(f"{TitanErrors.UNEXPECTED.value}: _eval_line function got unhandled line instance ({line} if of type {type(line)}) ({TitanErrors.UNEXPECTED.name})", exc_info=False)
            raise Exception(f"{TitanErrors.UNEXPECTED.value}: _eval_line function got unhandled line instance ({line} is of type {type(line)})", TitanErrors.UNEXPECTED.name)
    

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
                logging.exception(f"{TitanErrors.NOT_IMPLEMENTED.value} (function type ({info.datatype}) declaration) ({TitanErrors.NOT_IMPLEMENTED.name})", exc_info=False)
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
            logging.debug(f"line: {entry} has final evaluation id of {line_id}")

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
    spirv.print_contents()
    logging.debug(f"-[generate_spirv_asm] {spirv.generated_lines}")
    machine_object.SPIRV_asm_obj = spirv
    # print()
    # print()
    # print(f"generated: {spirv.generated_lines}")
    # print()
    # print()
    # print(symbol_table.content)

    if options.Options.OUTPUT_SPIRV_ASM in machine_object.output_options:
        spirv.output_to_file(machine_object.name_of_top_module)

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