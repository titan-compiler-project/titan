import pytest
import common.grammar as g
import common.operators as o


@pytest.mark.parametrize("num_val_list, expected_type_list",[
    (["0", "1", "-1", "0.0", "1.0", "-1.0"], [int, int, int, float, float, float])
])
def test_python_number(num_val_list, expected_type_list):
    for x in range(0, len(num_val_list)):
        num_val = num_val_list[x]
        expected_type = expected_type_list[x]

        parsed = g.TitanPythonGrammar.number.parse_string(num_val, parse_all=True)
        print(f"value '{num_val}' is expected to be {expected_type} but is actually {type(parsed[0])}")

        assert expected_type == type(parsed[0])

    
@pytest.mark.parametrize("param_str", [
    "", "a", "_a", "a, b", "_a, _b", "a, b, _c", "a, _b, _c"
])
def test_param_list(param_str):
    g.TitanPythonGrammar.function_parameter_list.parse_string(param_str, parse_all=True)

# TODO: expand this once grammar.TitanPythonGrammar.arithmetic_expression is fixed
# TODO: add more cases, i.e. nested expressions maybe
@pytest.mark.parametrize("expression, expected_class", [
    ("1", int), ("-1", o.UnaryOp), ("a + b", o.BinaryOp)
])
def test_arithmetic(expression, expected_class):

    x = g.TitanPythonGrammar.arithmetic_expression.parse_string(expression, parse_all=True)

    assert expected_class == type(x[0])
