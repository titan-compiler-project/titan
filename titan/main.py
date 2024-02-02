import io, logging, datetime, argparse, os

from compiler.helper import CompilerContext
from compiler.spirv import SPIRVAssembler
from compiler.verilog import VerilogAssember

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
    parser.add_argument("-s", help="only run the SPIR-V generation", action="store_true")

    args = parser.parse_args()

    logging.info(f"--- New run, time is: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ---")
    logging.info(f"arguments: {args}")


    compiler_ctx = CompilerContext(args)


    logging.info(f"Generating SPIR-V from {compiler_ctx.files[0]} ...")
    spirv_assembler = SPIRVAssembler(compiler_ctx.files[0], disable_debug=False)
    spirv_assembler.compile()

    if compiler_ctx.user_wants_spirv_asm():
        spirv_assembler.output_to_file(os.path.basename(compiler_ctx.files[0])[:-3])

    if compiler_ctx.user_only_wants_spirv():
        return

    logging.info(f"Generating RTL...")
    verilog_assembler = VerilogAssember(spirv_assembler.create_file_as_string())
    verilog_assembler.compile(os.path.basename(compiler_ctx.files[0])[:-3])


if __name__ == "__main__":
    main()