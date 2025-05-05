from unittest.mock import patch
from argparse import Namespace
import sys

import pytest

from tests.fixtures.args import *

from titan.main import run_argparse
from titan.compiler.helper import CompilerContext
from titan.common.options import Options


def __patch_sysargv(patch_args: list[str]) -> Namespace:
    with patch.object(sys, "argv", patch_args):
        parsed_args = run_argparse()

    return parsed_args

def test_argparse_simple(base_args: list[str]) -> None:
    """
    Test: Are the arguments are correctly being added to ``CompilerContext``?

    Args:
        base_args (list[str]): ``sys.argv``-like array containing the script name & input source file

    """
    parsed_args = __patch_sysargv(base_args)

    ctx = CompilerContext(parsed_args)

    assert ctx.compiler_args == parsed_args, "mismatched arguments saved"
    assert ctx.user_wants_spirv_asm is False
    assert ctx.has_user_defined_top is False
    assert ctx.user_only_wants_spirv is False
    assert ctx.user_wants_verbose_info is False
    assert ctx.use_dark_theme_for_dots is False
    assert ctx.gen_comms is True


def test_argparse_top_module(args_top_module: list[str]) -> None:
    """
    Test: Is the "top" option is being correctly handled?

    Args:
        args_top_module (list[str]): ``sys.argv``-like array containing the ``-t`` option
    """
    parsed_args = __patch_sysargv(args_top_module)
    ctx = CompilerContext(parsed_args)

    assert ctx.has_user_defined_top is True
    assert ctx.get_top_module_name() == "custom_top_function"
  
    # TODO: for some reason I can't use the 'in' operator to find the enum
    #       assert Options.DEFINE_TOP_MODULE in ctx.options
    assert ctx.options[0].value == Options.DEFINE_TOP_MODULE.value


def test_argparse_spirv_asm(args_spirv_asm: list[str]) -> None:
    """
    Test: Is the "SPIR-V ASM output" option being correctly handled?

    Args:
        args_spirv_only (list[str]): ``sys.argv``-like array containing the ``-asm`` option
    """
    parsed_args = __patch_sysargv(args_spirv_asm)
    ctx = CompilerContext(parsed_args)

    assert ctx.output_options[0].value == Options.OUTPUT_SPIRV_ASM.value


def test_argparse_only_spirv(args_only_spirv: list[str]) -> None:
    """
    Test: Is the "only generate SPIR-V" option being correctly handled?

    Args:
        args_only_spirv (list[str]): ``sys.argv``-like array containing the ``-s`` option
    """
    parsed_args = __patch_sysargv(args_only_spirv)
    ctx = CompilerContext(parsed_args)

    assert ctx.user_only_wants_spirv is True
