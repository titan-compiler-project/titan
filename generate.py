import machine as m
import symbols as s
import type as t
import operators as o

def generate_spirv_asm(machine_object: m.Machine, symbol_table: s.SymbolTable):

    # checking if we have a top module/entry point defined
    # TODO: package this up in another function
    if machine_object.name_of_top_module == None:
        func_count = len(machine_object.functions)

        if func_count == 0:
            raise Exception("no parsed source code to generate SPIR-V from", "no_source")
            return -1
        elif func_count > 1:
            raise Exception(f"undefined top module when there are {func_count} modules, use the -t option to set the top.", "no_top_set")
            return -1
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
            id = f"%{param}"
            entrypoint_param_list += f" {id}"

        for returned in entry.returns:
            id = f"%{returned}"
            entrypoint_param_list += f" {id}"


    spirv.append_code(
        spirv.Sections.ENTRY_AND_EXEC_MODES,
        f"OpEntryPoint Fragment %{machine_object.name_of_top_module} {entrypoint_param_list}"
    )

    del entrypoint_param_list

    spirv.append_code(
        spirv.Sections.ENTRY_AND_EXEC_MODES,
        f"OpExecutionMode %{machine_object.name_of_top_module} OriginUpperLeft"
    )

    # testing
    # spirv.add_type(spirv.TypeContext(t.DataType.INTEGER, t.StorageType.OUT, False, False), r"%id_xd")

    for symbol, info in symbol_table.content.items():
        # print(f"{symbol} {info.datatype} {info.operation}")

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

    for t_ctx, id in spirv.declared_types.items():
        # print(f"{t_ctx}, {id}, {t_ctx.primative_type}")

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

            case _:
                raise Exception("got unknown type while trying to generate SPIR-V", "unknown_type")

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
                raise Exception("not implemented", "not_implemented")
            
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
                        raise Exception("not implemented", "not_implemented")
                    
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
                        raise Exception("not implemented", "not_implemented")

    # define globals
    for func in machine_object.functions:
        # TODO: the same for params

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
                        raise Exception("not implemented", "not_implemented")

    
    def _eval_line(line):
        # print(f"{line} is of type {type(line)}")

        if isinstance(line, o.UnaryOp):
            # check if operator is negative
            #   check if operand is int OR float
            #       true: negate and overwrite the number in place
            #             check if constant exists, create if not

            type_of_operand = type(line.operands)

            # TODO: redundant?
            if line.operator == "-":
                if type_of_operand == (int or float):
                    # TODO: modified in place, is this a good idea?
                    # line.operands = line.operands * -1
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
                    return spirv.get_const_id(c_ctx)

                else:
                    # TODO
                    # use Op(S|F)Negate when dealing with variables
                    raise Exception("got unexpected type whilst parsing arithmetic", "unexpected_type")
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
            return spirv.get_const_id(c_ctx)
        elif isinstance(line, str):
            # gonna assume that this is a symbol
            print(f"st: {line}")
            if symbol_table.exists(line):
                return f"%{line}"

        elif isinstance(line, o.BinaryOp):
            # check type of operand
            #       if str then check if symbol exists
            #           raise error if not
            #       if int/float then check if const exists
            #           make if not
            #       if unary then self call
            #           - get returned id
            #       if binary then self call
            #           - get returned id
            #
            #       build expression?
            #       return id?

            # for operand in line.operands:
            #     if isinstance(operand, o.BinaryOp) or isinstance(operand, o.UnaryOp):
            #         print(operand)
            #         x = _eval_line(operand)
            #         print(x)
            #     else:
            #         print(f"operand: {operand}")

            a = _eval_line(line.operands[0])
            b = _eval_line(line.operands[1])


            print(f"line: {line}")
            print(f"\toperands: 0: {line.operands[0]}\t1: {line.operands[1]}")
            print(f"\top: {line.operator}")
            print(f"\ta: {a}")
            print(f"\tb: {b}")

            if a is not None and b is not None:
                return f"%testid"
    
    
    # start doing each function def and body eval
    for func in machine_object.functions:

        info = symbol_table.get(func.name)

        match info.datatype:
            case t.DataType.VOID:
                func_id = spirv.get_func_id(t.DataType.VOID)
                type_id = spirv.get_type_id(spirv.TypeContext(t.DataType.VOID, None, False, False))
                spirv.append_code(
                    spirv.Sections.FUNCTIONS,
                    f"%func_{func.name} = OpFunction {type_id} None {func_id}"
                )
            case _:
                raise Exception("not implemented", "not_implemented")

        spirv.append_code(
            spirv.Sections.FUNCTIONS,
            f"%func_label_{func.name} = OpLabel"
        )

        for entry in func.body:
            # testing
            # print(type(entry[2]))
            x = _eval_line(entry[2])
            # print(f"{entry} -------- {x}")

            # try:
            #     print(f"{entry[0]} {entry[1]} {entry[2]} len2: {len(entry[2].operands)}")
            #     print(f"\t0: {entry[2].operands[0]} is of type {type(entry[2].operands[0])}")
            #     print(f"\t1: {entry[2].operands[1]} is of type {type(entry[2].operands[1])}")
            #     print(f"\t is second operand the binaryop class: {isinstance(entry[2].operands[1], o.BinaryOp)}")
            #     print(f"\t is second operand the unaryop class: {isinstance(entry[2].operands[1], o.UnaryOp)}")
            # except TypeError:
            #     print(f"{entry[0]} {entry[1]} {entry[2]} len2: ?")
            # except AttributeError:
            #     print(f"{entry[0]} {entry[1]} {entry[2]} len2: ?")

    print()
    print()
    spirv.print_contents()
    # print()
    # print(f"types: {spirv.declared_types}")
    # print()
    # print(f"functions: {spirv.declared_function_types}")


def test_parse_action(tokens):
    # print(f"CALLED {tokens}")

    print("called")
    for x in range(0, len(tokens)):
        for y in range(0, len(tokens[x])):
            print(f"{x} {y}: {tokens[x][y]}")

    return None

def test_parse_action_statement(tokens):
    # print(f"statment test: {tokens}")
    return None


def generate_symbols(machine_object: m.Machine, symbol_table: s.SymbolTable):
    
    # for x in range(0, len(machine_object.functions)):
    #     print(f"{x}: {machine_object.functions[x]}")

        # the functions parameter will always contain:
        # - the function name
        # - the function parameters
        # - the body of the function
        # - the returns

        # 1. check and store function name in symbol table
        # 2. check and store function params
        # 3. check and store function returns
        # 4. check, evaluate and build body symbols?

        # for function in machine_object.functions:
        #     # check if function exists
        #     if not symbol_table.exists(function.name):
        #         # symbol_table.add(function.name, symbols.Information(symbols.DataType.NONE, symbols.Operation.FUNCTION_DECLARATION, None))
        #         symbol_table.add(function.name, symbols.Information(symbols.DataType.NONE, symbols.Operation.FUNCTION_DECLARATION))

        #     # check function params
        #     if len(function.params) != 0:
        #         for x in function.params:
        #             print(x)

    #############################################################################

    for function in machine_object.functions:
        
        # check if func is already declared
        if not symbol_table.exists(function.name):
            # print(f"function '{function.name}' does not exist in symbol table")
            symbol_table.add(function.name, s.Information(s.DataType.VOID, s.Operation.FUNCTION_DECLARATION))

            # now that the function is declared, check its input params
            if len(function.params) > 0:
                for param in function.params:
                    if not symbol_table.exists(param):
                        # print(f"param '{param}' does not exist in symbol table")
                        symbol_table.add(param, s.Information(s.DataType.INTEGER, s.Operation.FUNCTION_IN_VAR_PARAM))
            # else:
                # print("function does not have any input parameters")

            # check its output params
            if len(function.returns) > 0:
                for param in function.returns:
                    if not symbol_table.exists(param):
                        # print(f"param '{param}' does not exist in symbol table")
                        symbol_table.add(param, s.Information(s.DataType.INTEGER, s.Operation.FUNCTION_OUT_VAR_PARAM))
            # else:
                # print("function does not have any output parameters")


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

            # print(function.body)
            # print()
            # print(f"body: {function.body.dump()}")
            # print()
            # print(type(function.body))