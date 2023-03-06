import sys
from pathlib import Path
import machine
from options_enum import Options

# py -3.10-64 main.py

def parse_options():

    for option in sys.argv[1:]:
        # print(option)

        if option[0] == "-":
            option_string = option[1:]
            match option_string:
                case Options.OUTPUT_PREPROCESSED.value:
                    pass
                case Options.OUTPUT_SPIRV_ASM.value:
                    pass
                case _:
                    raise Exception(f"unknown option '{option_string}', exiting.", "bad_option")
            
        else:
            print("GOT SOMETHING ELSE")
        


def main():

    print(sys.argv)

    # if len(sys.argv[1:]) != 1:
    if len(sys.argv[1:]) == 0:
        print(f"got no arguments")
    else:
        # print(f"got arg: {sys.argv[1]}")
        try:
            parse_options()
        except Exception as err:
            # print(err.args)
            # print(err.args[1])
            if err.args[1] == "bad_option":
                print(f"{err.args[0]}")
                return -1
        print(f"file exist? {Path(sys.argv[1]).is_file()}")


if __name__ == "__main__":
    main()  