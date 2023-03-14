import pyparsing as pp
from typing import NamedTuple

class TitanPythonGrammar(NamedTuple):

    # keywords
    keyword_def = pp.Keyword("def")
    keyword_return = pp.Keyword("return")
    keyword_None = pp.Keyword("None")
    
    function_name = pp.pyparsing_common.identifier
    variable_name = pp.pyparsing_common.identifier
    
    # symbols
    l_br, r_br = map(pp.Literal, "()")
    l_cbr, r_cbr = map(pp.Literal, "{}")
    colon = pp.Literal(":")

    # numbers
    integer = pp.Word(pp.nums)
    float = integer + "." + pp.Word(pp.nums)
    number = integer | float

    function_parameter_list = pp.delimited_list(variable_name) | pp.empty
    function_return_list = pp.Group(pp.delimited_list(variable_name | number | keyword_None))
    function_call = function_name + l_br + function_parameter_list + r_br
    function_definition = keyword_def.suppress() + function_name.set_results_name("function_name") + l_br.suppress() + function_parameter_list.set_results_name("function_param_list") + r_br.suppress() + colon.suppress()

    arithmetic_expression = pp.infix_notation(variable_name | number, [
        ('-', 1, pp.OpAssoc.RIGHT),
        (pp.one_of("* /"), 2, pp.OpAssoc.LEFT),
        (pp.one_of("+ -"), 2, pp.OpAssoc.LEFT)
    ])

    statement = pp.Group(variable_name + "=" + arithmetic_expression | function_call)

    function_body = pp.Group(pp.ZeroOrMore(statement)).set_results_name("function_statements") + pp.Optional(keyword_return.suppress()  + function_return_list.set_results_name("function_returns"))

    module = pp.ZeroOrMore(
        pp.Group(
            function_definition + l_cbr.suppress() + function_body + r_cbr.suppress()
            )
    )