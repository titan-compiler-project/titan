import pytest

@pytest.fixture(name="base_args")
def fixture_args_base() -> list[str]:
    """
    Fixture: Generate a base argument array

    Returns:
        A ``sys.argv``-like array, containing dummy values for the script name and source input file
    """
    args = ["main.py", "source_file.py"]
    return args

@pytest.fixture(name="args_top_module")
def fixture_args_top_module(base_args: list[str]) -> list[str]:
    """
    Fixture: Add the "top" option to an existing list of arguments
 
    Args:
        base_args (list[str]): Base ``sys.argv``-like array, input via a pytest fixture

    Returns:
        A modified ``sys.argv``-like array, including the ``-t`` option with a specified name
    """
    base_args += ["-t", "custom_top_function"]
    return base_args

@pytest.fixture(name="args_spirv_asm")
def fixture_args_spirv_asm(base_args: list[str]) -> list[str]:
    """
    Fixture: Add the "-asm" option to an existing list of arguments
 
    Args:
        base_args (list[str]): Base ``sys.argv``-like array, input via a pytest fixture

    Returns:
        A modified ``sys.argv``-like array, including the ``-asm`` option
    """
    base_args += ["-asm"]
    return base_args


@pytest.fixture(name="args_only_spirv")
def fixture_args_only_spirv(base_args: list[str]) -> list[str]:
    """
    Fixture: Add the "-s" option to an existing list of arguments
 
    Args:
        base_args (list[str]): Base ``sys.argv``-like array, input via a pytest fixture

    Returns:
        A modified ``sys.argv``-like array, including the ``-s`` option
    """
    base_args += ["-s"]
    return base_args
