import io, logging, datetime, argparse, os
import machine, parse, generate, common.symbols as symbols

from compiler.helper import CompilerContext

import ast_crawl

# py -3.10-64 main.py

def main():
    """ Entry point for the program.
    
        Calls to handle CLI options, parsing, generating and writing.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler("compiler_log.txt"),
            logging.StreamHandler()
        ],
        format=f"[%(levelname)s] [%(module)s.%(funcName)s, line: %(lineno)d]: %(message)s"
    )


    parser = argparse.ArgumentParser(
        description = "Compile a subset of Python into SystemVerilog. Visit https://titan-compiler-project.github.io/titan for more info."
    )

    parser.add_argument("source_file", help="python source file to compile")
    parser.add_argument("-t", "--top", help="specify the top function")
    parser.add_argument("-asm", help="output the SPIR-V assembly code", action="store_true")

    args = parser.parse_args()

    logging.info(f"--- New run, time is: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ---")
    logging.info(f"arguments: {args}")


    compiler_ctx = CompilerContext(args)


    # FIXME: currently only works on file
    logging.info(f"Generating SPIR-V from {compiler_ctx.files[0]} ...")
    input_python_file = compiler_ctx.files[0]

    x = ast_crawl.GenerateSPIRVFromAST(input_python_file)
    x.crawl() # generates spirv TODO: rename function probably

    # dump file in pwd instead of given filepath of source file
    if compiler_ctx.user_wants_spirv_asm:
        x.output_to_file(os.path.basename(compiler_ctx.files[0])[:-3])

    parse_result = None
    with io.StringIO(x.create_file_as_string()) as y:
        parse_result = parse.TitanSPIRVGrammar.spirv_body.parse_file(y)

    logging.info(f"Generating RTL...")
    generate.generate_verilog(parse_result)

if __name__ == "__main__":
    main()