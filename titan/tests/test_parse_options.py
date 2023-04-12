import pytest, sys
from unittest.mock import patch

from main import _parse_options
from options import Options
from machine import Machine


# https://docs.pytest.org/en/6.2.x/parametrize.html
@pytest.mark.parametrize("options, expected", [
    (f"-{Options.OUTPUT_PREPROCESSED.value}", [Options.OUTPUT_PREPROCESSED]),
    (f"-{Options.OUTPUT_SPIRV_ASM.value}", [Options.OUTPUT_SPIRV_ASM]),
    ([f"-{Options.OUTPUT_SPIRV_ASM.value}", f"-{Options.OUTPUT_PREPROCESSED.value}"], [Options.OUTPUT_SPIRV_ASM, Options.OUTPUT_PREPROCESSED])
])
def test_output_options(options, expected):
    test_args = ['main.py']

    if type(options) != str:
        for option in options:
            test_args.append(option)
    else:
        test_args.append(options)

    print(f"{test_args}")

    m = Machine()

    # https://stackoverflow.com/questions/18668947/how-do-i-set-sys-argv-so-i-can-unit-test-it
    with patch.object(sys, 'argv', test_args):
        _parse_options(m)

        assert expected == m.output_options


@pytest.mark.parametrize("args, out_opts, opts, top_name",[
    ([f"-{Options.DEFINE_TOP_MODULE.value}", "top_test"], [], [Options.DEFINE_TOP_MODULE], "top_test")
])
def test_options_with_top_name(args, out_opts, opts, top_name):
    test_args = ["main.py"]

    for arg in args:
        test_args.append(arg)

    print(f"{test_args}")

    m = Machine()

    with patch.object(sys, 'argv', test_args):
        _parse_options(m)

        assert top_name == m.name_of_top_module
        assert out_opts == m.output_options
        assert opts == m.options