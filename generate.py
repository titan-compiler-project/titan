import machine
import symbols as s
def generate_spirv_asm(machine_object: machine.Machine):

    # for function in machine_object.functions:
    #     for statement in function.body:
    #         print(statement)

    # print()

    # for results in machine_object.parsed_modules:
    #     print(results)

    return None

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


def generate_symbols(machine_object: machine.Machine, symbol_table: s.SymbolTable):
    
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
            symbol_table.add(function.name, s.Information(s.DataType.NONE, s.Operation.FUNCTION_DECLARATION))

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
                    print(entry)

                    if not symbol_table.exists(entry[0]):
                        symbol_table.add(entry[0], s.Information(s.DataType.INTEGER, s.Operation.VARIABLE_DECLARATION))



                # print(entry.get_name('assignment'))

            # print(function.body)
            # print()
            # print(f"body: {function.body.dump()}")
            # print()
            # print(type(function.body))