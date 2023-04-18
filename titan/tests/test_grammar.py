import pytest
import grammar as g


@pytest.mark.parametrize("num_val",[
    "0", "1", "-1", "0.0", "1.0", "-1.0"
])
def test_python_number(num_val):
    
    g.TitanPythonGrammar.number.parse_string(num_val, parse_all=False)