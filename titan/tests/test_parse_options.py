import pytest, sys
from unittest.mock import patch

from main import _parse_options
from options import Options
from machine import Machine


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

    with patch.object(sys, 'argv', test_args):
        _parse_options(m)

        assert expected == m.output_options