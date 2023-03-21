import sys
from pathlib import Path
# import machine
from options import Options
import machine, parse, generate, symbols

# py -3.10-64 main.py

def parse_options(machine_object):

    got_top_module = False
    # for option in sys.argv[1:]:
    for x in range(1, len(sys.argv)):

        # need to skip over because the -t flag takes 2 params
        if got_top_module:
            continue

        # print(f"x: {x}")
        option = sys.argv[x]
        # print(option)

        if option[0] == "-":
            option_string = option[1:]
            match option_string:
                case Options.OUTPUT_PREPROCESSED.value:
                    machine_object.output_options.append(Options.OUTPUT_PREPROCESSED)
                case Options.OUTPUT_SPIRV_ASM.value:
                    machine_object.output_options.append(Options.OUTPUT_SPIRV_ASM)
                case Options.DEFINE_TOP_MODULE.value:
                    machine_object.options.append(Options.DEFINE_TOP_MODULE)
                    # TODO: how to find current pos in sys.argv and to look ahead one?
                    # this must be the top module name
                    # print(f"top: {sys.argv[x+1]}")
                    machine_object.name_of_top_module = sys.argv[x + 1]
                    got_top_module = True
                    # raise Exception(f"option {option} not yet implemented", "not_implemented")
                case _:
                    raise Exception(f"unknown option '{option}', exiting.", "bad_option")
            
        elif option[-3:] == ".py":
            file_exists = Path(option).is_file()

            if file_exists:
                machine_object.files.append(option)
            else:
                # print(f"file {option} does not exist.")
                raise Exception(f"file '{option}' does not exist, exiting.", "no_file")
        else:
            raise Exception(f"unable to parse '{option}', exiting.", "parse_option_fail")
        

def _print_debug(machine_object: machine.Machine):
    print("="*10)
    print(f"Options: {machine_object.options}")
    print(f"Output Options: {machine_object.output_options}")
    print(f"Processed Text: {machine_object.processed_text}")
    print(f"Parsed Modules: {machine_object.parsed_modules}")
    print(f"Functions = {machine_object.functions}")
    print(f"Top: {machine_object.name_of_top_module}")
    print("="*10)


def main():

    print(f"SYS ARG: {sys.argv}")

    machine_object = machine.Machine()
    symbol_table = symbols.SymbolTable()

    # argument parse call and error handle
    if len(sys.argv[1:]) == 0:
        print(f"got no arguments")
    else:
        try:
            parse_options(machine_object)
        except Exception as err:
            print(f"{err.args[0]} ({err.args[1]})")
            return -1

            # if err.args[1] == "bad_option":
            #     print(f"{err.args[0]}")
            #     return -1
            # if err.args[1] == "parse_option_fail":
            #     print(f"{err.args[0]}")
            #     return -1
                    
            
    # debug
    # print()
    # print(machine_object.options)
    # print(machine_object.output_options)
    # print(machine_object.files)
    # print(machine_object.processed_text)
    # print()


    parse.preprocess(machine_object)

    # _print_debug(machine_object)

    # debug
    # print()
    # print(f"OPTIONS: {machine_object.options}")
    # print(f"OUTPUT OPTIONS: {machine_object.output_options}")
    # print(f"FILES: {machine_object.files}")

    # print()

    parse.parse_processed_python(machine_object)

    # _print_debug(machine_object)

    # print(f"PROCESSED: {machine_object.processed_text}")
    # print(f"MODULES: {machine_object.parsed_modules}")


    # for file in machine_object.processed_text:
    #     for line in file:
    #         print(line)

    # print(f"FUNCTIONS:")
    # for x in machine_object.functions:
    #     print(x)

    # generate.generate_spirv_asm(machine_object)

    generate.generate_symbols(machine_object, symbol_table)

    _print_debug(machine_object)

    # print(symbol_table.content)
    # for entry in symbol_table.content:
        # print(entry)

    print()
    for key, value in symbol_table.content.items():
        print(f"{value[0].name} - {key} - {value[1].name}")


    generate.generate_spirv_asm(machine_object, symbol_table)


if __name__ == "__main__":
    main()  