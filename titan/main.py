import io, logging, datetime, argparse, os

from rich.logging import RichHandler

from compiler.helper import CompilerContext
from compiler.spirv import SPIRVAssembler
from compiler.verilog import VerilogAssember

def run_argparse() -> argparse.Namespace:
    """ Handles setting up and executing `argparse.ArgumentParser`.

        Returns:
            Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description = "Compile a subset of Python into SystemVerilog. Visit https://titan-compiler-project.github.io/titan for more info."
    )

    parser.add_argument("source_file", help="python source file to compile")
    parser.add_argument("-t", "--top", help="specify the top function")
    parser.add_argument("-asm", help="output the SPIR-V assembly code", action="store_true")
    parser.add_argument("-s", help="only run the SPIR-V generation", action="store_true", dest="run_spirv_only")
    parser.add_argument("-v", "--verbose", help="output debug messages", action="store_true")
    parser.add_argument("-dd", "--dark-dots", help="use dark theme when creating Graphviz dot graphs", action="store_true")
    parser.add_argument("-y", "--gen-yosys", help="generate simple yosys script to visualise module", action="store_true")

    return parser.parse_args()


def main():
    """ Entry point for the program.
    
        Calls to handle CLI options, parsing, generating and writing.

    """
    
    args = run_argparse()
    compiler_ctx = CompilerContext(args)


    logging.basicConfig(
        level=logging.DEBUG if compiler_ctx.user_wants_verbose_info else logging.INFO,
        handlers=[
            logging.FileHandler("compiler_log.txt"),
            # logging.StreamHandler()
            RichHandler(show_time=False, markup=True)
        ],
        # format=f"[%(levelname)s] [%(module)s.%(funcName)s, line: %(lineno)d]: %(message)s"
        format=f"%(message)s"
    )

    logging.info(f"--- New run, time is: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ---")
    logging.debug(f"arguments: {args}")

    logging.debug(f"output folder exists? {os.path.exists('output')}")
    os.makedirs("output", exist_ok=True)

    logging.info(f"Generating SPIR-V from {compiler_ctx.files[0]} ...")
    spirv_assembler = SPIRVAssembler(compiler_ctx.files[0], disable_debug=False)
    spirv_assembler.compile()

    if compiler_ctx.user_wants_spirv_asm:
        spirv_assembler.output_to_file(os.path.basename(compiler_ctx.files[0])[:-3])

    # early exit, no need for RTL
    if compiler_ctx.user_only_wants_spirv:
        return

    logging.info(f"Generating RTL ...")
    verilog_assembler = VerilogAssember(spirv_assembler.create_file_as_string())
    verilog_assembler.compile(os.path.basename(compiler_ctx.files[0])[:-3], 
                              gen_yosys_script=compiler_ctx.gen_yosys_script,
                              dark_dots=compiler_ctx.use_dark_theme_for_dots
                              )


if __name__ == "__main__":
    main()