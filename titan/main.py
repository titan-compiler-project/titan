import sys, io, logging, datetime
from pathlib import Path
from common.options import Options
import machine, parse, generate, symbols
from common.errors import TitanErrors

import ast_crawl

# py -3.10-64 main.py

def _parse_options(machine_object):

    got_top_module = False
    dont_repeat = False
    for x in range(1, len(sys.argv)):

        # need to skip over because the -t flag takes 2 params
        if got_top_module and not dont_repeat:
            dont_repeat = True
            continue

        option = sys.argv[x]

        if option[0] == "-":
            option_string = option[1:]
            match option_string:
                case Options.OUTPUT_PREPROCESSED.value:
                    machine_object.output_options.append(Options.OUTPUT_PREPROCESSED)

                case Options.OUTPUT_SPIRV_ASM.value:
                    machine_object.output_options.append(Options.OUTPUT_SPIRV_ASM)

                case Options.DEFINE_TOP_MODULE.value:
                    machine_object.options.append(Options.DEFINE_TOP_MODULE)

                    machine_object.name_of_top_module = sys.argv[x + 1]
                    got_top_module = True
                case _:
                    # raise Exception(f"unknown option '{option}', exiting.", "bad_option")
                    raise Exception(f"{TitanErrors.PARSE_BAD_OPTION.value} \"{option}\"", TitanErrors.PARSE_BAD_OPTION.name)
            
        elif option[-3:] == ".py":
            file_exists = Path(option).is_file()

            if file_exists:
                machine_object.files.append(option)
            else:
                # raise Exception(f"file '{option}' does not exist, exiting.", "no_file")
                raise Exception(f"{TitanErrors.NON_EXISTENT_FILE.value} \"{option}\"", TitanErrors.NON_EXISTENT_FILE.name)
        else:
            # raise Exception(f"unable to parse '{option}', exiting.", "parse_option_fail")
            raise Exception(f"{TitanErrors.PARSE_OPTION_FAILURE.value} \"{option}\"", TitanErrors.PARSE_OPTION_FAILURE.name)
        

def _print_debug(machine_object: machine.Machine):
    print("="*10)
    print(f"Options: {machine_object.options}")
    print(f"Output Options: {machine_object.output_options}")
    print(f"Processed Text: {machine_object.processed_text}")
    print(f"Parsed Modules: {machine_object.parsed_modules}")
    print(f"Functions =")
    for entry in machine_object.functions:
        print(f"\tname: {entry.name}")
        print(f"\t\t - params: {entry.params}")
        print(f"\t\t - body: {entry.body}")
        print(f"\t\t - returns: {entry.returns}")
    print(f"Top: {machine_object.name_of_top_module}")
    print("="*10)


def main():

    # debug
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler("compiler_log.txt"),
            logging.StreamHandler()
        ],
        format=f"[%(levelname)s] [%(module)s.%(funcName)s, line: %(lineno)d]: %(message)s"
    )

    logging.info(f"--- New run, time is: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ---")
    logging.debug(f"Arguments: {sys.argv}")

    machine_object = machine.Machine()
    symbol_table = symbols.SymbolTable()

    # argument parse call and error handle
    if len(sys.argv[1:]) == 0:
        logging.error("Got no arguments. Exiting.")
        return -1
    else:
        try:
            _parse_options(machine_object)
        except Exception as err:
            logging.error(f"{err.args[0]} ({err.args[1]})")
            return -1                    
            
    # handle python -> spirv
    # parse.preprocess(machine_object)
    # parse.parse_processed_python(machine_object)
    # generate.generate_symbols(machine_object, symbol_table)
    # generate.generate_spirv_asm(machine_object, symbol_table)

    # handle spirv -> verilog
    # parse_result = parse.parse_spriv(machine_object)


    logging.info(f"Generating SPIR-V from {machine_object.files[0]} ...")
    # assumes that there is only one file
    input_python_file = machine_object.files[0]
    x = ast_crawl.GenerateSPIRVFromAST(input_python_file)
    x.crawl() # generates spirv TODO: rename function probably

    parse_result = None
    with io.StringIO(x.create_file_as_string()) as y:
        parse_result = parse.TitanSPIRVGrammar.spirv_body.parse_file(y)

    logging.info(f"Generating RTL...")
    generate.generate_verilog(parse_result)

if __name__ == "__main__":
    main()