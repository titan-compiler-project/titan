import pytest
import grammar as g


@pytest.mark.parametrize("num_val",[
    "0", "1", "-1", "0.0", "1.0", "-1.0"
])
def test_python_number(num_val):
    g.TitanPythonGrammar.number.parse_string(num_val, parse_all=True)

    
@pytest.mark.parametrize("param_str", [
    "", "a", "_a", "a, b", "_a, _b", "a, b, _c", "a, _b, _c"
])
def test_param_list(param_str):
    g.TitanPythonGrammar.function_parameter_list.parse_string(param_str, parse_all=True)

