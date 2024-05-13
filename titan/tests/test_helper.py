import pytest, sys, os
from unittest.mock import patch
from typing import NamedTuple
from random import choice
from bidict import bidict

# https://stackoverflow.com/questions/16780014/import-file-from-parent-directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.helper import *
from main import run_argparse

class OptionsTuple(NamedTuple):
    source_file: str = ""       # source_file
    top: bool = False           # -t, --top
    asm: bool = False           # -asm
    spirv_only: bool = False    # -s
    verbose: bool = False       # -v, --verbose


def _generate_dummy_args() -> tuple[list, OptionsTuple]:
    """ Randomly generates a set of arguments.
    
        Returns:
            Tuple containing a list of args to overwrite sys.argv with, and `OptionsTuple`.
    """
    # no zeroth element to align with OptionsTuple
    args_lookup = bidict({
        1: "-t", 2: "-asm", 3: "-s", 4: "-v"
    })

    # need dummy file
    args = ["script.py"]

    # im sure i could just iterate through all of these instead
    options = OptionsTuple(
        source_file="file.py",
        # top=choice([True, False]), # unused at the moment
        top=False,  # force to false
        asm=choice([True, False]),
        spirv_only=choice([True, False]),
        verbose=choice([True, False]),
    )
    
    # NOTE: ignoring -t option for now, not well supported in compiler
    # also needs additional string specified
    for i in range(2, len(options)):
        if options[i]:  # if option is set to true
            args.append(args_lookup[i])

    args.append(options.source_file)

    return args, options


def test_argparse():
    """ Tests `main.run_argparse`
     
        Expecting to have correct attributes set after parsing arguments.
    """

    args, options = _generate_dummy_args()

    with patch.object(sys, "argv", args):
        parsed_args = run_argparse()

    assert parsed_args.source_file == options.source_file, f"{parsed_args.source_file} != {options.source_file}"
    assert parsed_args.top == None, f"{parsed_args.top} != {options.top}"       # not set
    assert parsed_args.asm == options.asm, f"{parsed_args.asm} != {options.asm}"
    assert parsed_args.s == options.spirv_only, f"{parsed_args.s} != {options.spirv_only}"
    assert parsed_args.verbose == options.verbose, f"{parsed_args.verbose} != {options.verbose}"


def test_compiler_context():
    """ Tests `compiler.helper.CompilerContext`

        Expecting to have correct attributes set and functions returning matching values.
    """

    args, options = _generate_dummy_args()

    with patch.object(sys, "argv", args):
        patched_args = run_argparse()

    compiler_context = CompilerContext(patched_args)

    assert compiler_context.user_wants_spirv_asm() == options.asm, f"{compiler_context.user_wants_spirv_asm()} != {options.asm}"
    assert compiler_context.has_user_defined_top() == options.top, f"{compiler_context.has_user_defined_top()} != {options.top}"
    assert compiler_context.get_top_module_name() == None, f"{compiler_context.get_top_module_name()} != None"
    assert compiler_context.user_only_wants_spirv() == options.spirv_only, f"{compiler_context.user_only_wants_spirv()} != {options.spirv_only}"
    assert compiler_context.user_wants_verbose_info() == options.verbose, f"{compiler_context.user_wants_verbose_info()} != {options.verbose}"

if __name__ == "__main__":
    test_argparse()
    test_compiler_context()