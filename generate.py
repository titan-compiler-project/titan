import machine as m
import symbols as s
import type as t

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
        print(f"{symbol} {info.datatype} {info.operation}")

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
        print(f"{t_ctx}, {id}, {t_ctx.primative_type}")

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


    spirv.print_contents()
    print()
    print(f"types: {spirv.declared_types}")
    print()
    print(f"functions: {spirv.declared_function_types}")
    

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