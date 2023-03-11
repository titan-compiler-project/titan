import sys
from pathlib import Path
import machine
from options_enum import Options
import parse

# py -3.10-64 main.py

def parse_options(machine_object):

    for option in sys.argv[1:]:
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
        


def main():

    print(f"SYS ARG: {sys.argv}")

    machine_object = machine.Machine()

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

    # debug
    print()
    print(f"OPTIONS: {machine_object.options}")
    print(f"OUTPUT OPTIONS: {machine_object.output_options}")
    print(f"FILES: {machine_object.files}")
    print(f"PROCESSED: {machine_object.processed_text}")
    print()

    parse.parse_processed_python(machine_object)

    # for file in machine_object.processed_text:
    #     for line in file:
    #         print(line)


if __name__ == "__main__":
    main()  