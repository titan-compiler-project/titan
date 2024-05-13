import common.errors

import logging

from enum import Enum
from pathlib import Path

class Options(Enum):
    """ Enum containing all valid options."""
    OUTPUT_PREPROCESSED = "oPP"
    OUTPUT_SPIRV_ASM = "oSA"
    DEFINE_TOP_MODULE = "t"

def parse_options(machine_object, args):
    """ Method responsible for parsing the CLI options and assigning them to the appropriate places.
    
        Note:
            This method was replaced with Python's own ``argparse`` library.
    """
    got_top_module = False
    dont_repeat = False

    for i in range(1, len(args)):
        option = args[i]
        
        if got_top_module and not dont_repeat:
            dont_repeat = True
            continue

        if option[0] == "-":
            option_string = option[1:]

            match option_string:
                case Options.OUTPUT_PREPROCESSED.value:
                    machine_object.output_options.append(Options.OUTPUT_PREPROCESSED)

                case Options.OUTPUT_SPIRV_ASM.value:
                    machine_object.output_options.append(Options.OUTPUT_SPIRV_ASM)

                case Options.DEFINE_TOP_MODULE.value:
                    machine_object.options.append(Options.DEFINE_TOP_MODULE)
                    machine_object.name_of_top_module = args[i + 1]
                    got_top_module = True
                
                case _:
                    logging.exception(f"{common.errors.TitanErrors.PARSE_BAD_OPTION.value} \"{option}\" ({common.errors.TitanErrors.PARSE_BAD_OPTION.name})")
                    raise Exception(f"{common.errors.TitanErrors.PARSE_BAD_OPTION.value} \"{option}\" ({common.errors.TitanErrors.PARSE_BAD_OPTION.name})")
                
        elif option[-3:] == ".py":
            file_exists = Path(option).is_file()

            if file_exists:
                machine_object.files.append(option)
            else:
                logging.exception(f"{common.errors.TitanErrors.PARSE_OPTION_FAILURE.value} \"{option}\" ({common.errors.TitanErrors.PARSE_OPTION_FAILURE.name})")
                raise Exception(f"{common.errors.TitanErrors.PARSE_OPTION_FAILURE.value} \"{option}\" ({common.errors.TitanErrors.PARSE_OPTION_FAILURE.name})")