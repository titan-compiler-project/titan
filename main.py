import sys
from pathlib import Path
import machine
from options_enum import Options

# py -3.10-64 main.py

def parse_options(machine_object):

    for option in sys.argv[1:]:
        # print(option)

        if option[0] == "-":
            option_string = option[1:]
            match option_string:
                case Options.OUTPUT_PREPROCESSED.value:
                    # add to machine list
                    # generate preprocessed thing
                    machine_object.options.append(Options.OUTPUT_PREPROCESSED.name)
                case Options.OUTPUT_SPIRV_ASM.value:
                    machine_object.options.append(Options.OUTPUT_SPIRV_ASM.name)
                case _:
                    raise Exception(f"unknown option '{option_string}', exiting.", "bad_option")
            
        elif option[-3:] == ".py":
            print("got filename")
            print(f"file exist? {Path(sys.argv[1]).is_file()}")
        else:
            raise Exception(f"unable to parse '{option}', exiting.", "parse_option_fail")
        


def main():

    print(sys.argv)

    machine_object = machine.Machine()

    if len(sys.argv[1:]) == 0:
        print(f"got no arguments")
    else:
        try:
            parse_options(machine_object)
        except Exception as err:
            if err.args[1] == "bad_option":
                print(f"{err.args[0]}")
                return -1
            if err.args[1] == "parse_option_fail":
                print(f"{err.args[0]}")
                return -1
            
    # debug
    print(machine_object.options)
    print(machine_object.files)
    print(machine_object.processed_text)


if __name__ == "__main__":
    main()  