from common.options import Options
import common.options
from common.errors import TitanErrors

import sys, io, logging, datetime
from pathlib import Path
import machine, parse, generate, common.symbols as symbols

import ast_crawl

# py -3.10-64 main.py

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
            common.options.parse_options(machine_object, sys.argv)
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