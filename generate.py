import machine
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
