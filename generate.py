import machine, symbols
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


def generate_symbols(machine_object: machine.Machine, symbol_table: symbols.SymbolTable):
    
    for x in range(0, len(machine_object.functions)):
        print(f"{x}: {machine_object.functions[x]}")

        # the functions parameter will always contain:
        # - the function name
        # - the function parameters
        # - the body of the function
        # - the returns

        # 1. check and store function name in symbol table
        # 2. check and store function params
        # 3. check and store function returns
        # 4. check, evaluate and build body symbols?

        for function in machine_object.functions:
            # check if function exists
            if not symbol_table.exists(function.name):
                # symbol_table.add(function.name, symbols.Information(symbols.DataType.NONE, symbols.Operation.FUNCTION_DECLARATION, None))
                symbol_table.add(function.name, symbols.Information(symbols.DataType.NONE, symbols.Operation.FUNCTION_DECLARATION))

            # check function params
            if len(function.params) != 0:
                for x in function.params:
                    print(x)