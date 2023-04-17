import pyparsing as pp
from typing import NamedTuple
import operators as o

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
    semicolon = pp.Literal(";")

    # numbers
    integer = pp.Word(pp.nums).set_parse_action(lambda tokens: int(tokens[0]))
    # float = (pp.Word(pp.nums) + "." + pp.Word(pp.nums)).set_parse_action(lambda tokens: float(tokens[0]))
    float = pp.pyparsing_common.fnumber
    # number = integer | float
    number = pp.Or(integer, float)

    function_parameter_list = pp.delimited_list(variable_name) | pp.empty
    function_return_list = pp.Group(pp.delimited_list(variable_name | number | keyword_None))
    function_call = function_name + l_br + function_parameter_list + r_br
    function_definition = keyword_def.suppress() + function_name.set_results_name("function_name") + l_br.suppress() + function_parameter_list.set_results_name("function_param_list") + r_br.suppress() + colon.suppress()

    arithmetic_expression = pp.infix_notation(variable_name | number, [
        ('-', 1, pp.OpAssoc.RIGHT, o.UnaryOp),
        (pp.one_of("* /"), 2, pp.OpAssoc.LEFT, o.BinaryOp),
        (pp.one_of("+ -"), 2, pp.OpAssoc.LEFT, o.BinaryOp)
    ])

    assignment = (variable_name + "=" + arithmetic_expression | function_call).set_results_name("assignment")

    # an optional ";" was added to the end of the statement and function return grammars, this is so that it can still match
    # when doing the preprocessing step, and when it comes to parsing the file itself
    # TODO: this might cause issues, maybe split into two seperate variables?
    statement = pp.Group(assignment) + pp.Opt(semicolon.suppress())

    function_body = pp.Group(pp.ZeroOrMore(statement)).set_results_name("function_statements") + pp.Optional(keyword_return.suppress()  + function_return_list.set_results_name("function_returns") + pp.Opt(semicolon.suppress()))

    module = pp.ZeroOrMore(
        pp.Group(
            function_definition + l_cbr.suppress() + function_body + r_cbr.suppress()
            )
    )


class TitanSPIRVGrammar(NamedTuple):

    pp.ParserElement.set_default_whitespace_chars(" \t")
    nl = pp.Literal("\n")
    eq = pp.Literal("=").suppress()
    op = pp.Literal("Op").suppress()

    id = pp.Combine(pp.Literal("%") + pp.pyparsing_common.identifier)
    literal_string = pp.quoted_string # https://pyparsing-docs.readthedocs.io/en/latest/HowToUsePyparsing.html?highlight=string#common-string-and-token-constants

    # TODO: is there a better way to do this? would rather not have a big list of keywords
    #       - can't use pp.Word(pp.alphanums) because it will greedily consume the next line
    # keywords = pp.Keyword("Shader") | pp.Keyword("Logical") | pp.Keyword("GLSL450") | \
                # pp.Keyword("Fragment") | pp.Keyword("OriginUpperLeft") | pp.Keyword("Location") | \
                # pp.Keyword("Output") | pp.Keyword("Function") | pp.Keyword("None")

    opcode = op + pp.Word(pp.alphanums).set_results_name("opcode")

    opcode_args = pp.Group(pp.delimited_list(
        pp.ZeroOrMore(id | literal_string | pp.Word(pp.alphanums) | pp.pyparsing_common.number),
        delim=" ",
        allow_trailing_delim=False
    )).set_results_name("opcode_args")


    body_start = id + eq + op + pp.Keyword("Label")
    body_end = op + pp.Keyword("FunctionEnd")
    operation = opcode + pp.Opt(opcode_args) + nl.suppress()
    assignment = id + eq + operation
    
    header = pp.ZeroOrMore(operation)

    spirv_body = pp.ZeroOrMore(
        pp.Group(operation | assignment)
    )

    # spirv_body = pp.Group(header) + pp.ZeroOrMore(
    #     pp.Group(
    #         body_start + \
    #             pp.Group(
    #                 operation | assignment
    #             ) + \
    #         body_end
    #     )
    # )