import pyparsing as pp
from typing import NamedTuple
import operators as o

# slow performance when evaluating comparison statements
# https://pyparsing-docs.readthedocs.io/en/latest/pyparsing.html?highlight=infix_notation#pyparsing.ParserElement.enable_packrat
pp.ParserElement.enable_packrat()

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
    return_arrow = pp.Literal("->")

    number = pp.pyparsing_common.number

    type = pp.one_of(["int", "float", "bool"])

    parameter_with_type_hint = pp.Group(variable_name.set_results_name("parameter") + colon.suppress() + type.set_results_name("type"))
    function_parameter_list_with_type_hint = pp.delimited_list(parameter_with_type_hint) | pp.empty

    function_parameter_list = pp.delimited_list(variable_name) | pp.empty
    function_return_list = pp.Group(pp.delimited_list(variable_name | number | keyword_None))
    function_call = function_name + l_br + function_parameter_list + r_br
    # function_definition = keyword_def.suppress() + function_name.set_results_name("function_name") + l_br.suppress() + function_parameter_list.set_results_name("function_param_list") + r_br.suppress() + colon.suppress()
    function_definition = keyword_def.suppress() + function_name.set_results_name("function_name") + l_br.suppress() + function_parameter_list_with_type_hint.set_results_name("function_param_list") + r_br.suppress() + return_arrow.suppress() + (type | keyword_None).set_results_name("function_return_type") + colon.suppress()

    # TODO: this doesn't like parsing "a + b - 3" or anything that isn't nicely seperated by brackets
    #       - tried the github ver down below but it also has the same issue, the operators.py file needs to be looked at
    # precendece reference for the comparison operators https://en.cppreference.com/w/c/language/operator_precedence
    arithmetic_expression = pp.infix_notation(variable_name | number, [
        ("-", 1, pp.OpAssoc.RIGHT, o.UnaryOp),
        ("~", 1, pp.OpAssoc.RIGHT, o.UnaryOp),
        (pp.one_of("* /"), 2, pp.OpAssoc.LEFT, o.BinaryOp),
        (pp.one_of("+ -"), 2, pp.OpAssoc.LEFT, o.BinaryOp),
        (pp.one_of("& | ^"), 2, pp.OpAssoc.LEFT, o.BinaryOp),
        (pp.one_of("< <= >= > == !="), 2, pp.OpAssoc.LEFT, o.BinaryOp)
    ])

    # TODO: should these be separate or merged with the arithmetic_expression object
    bitwise_expression = pp.infix_notation(variable_name | number, [
        ("~", 1, pp.OpAssoc.RIGHT, o.UnaryOp),
        (pp.one_of("& | ^"), 2, pp.OpAssoc.LEFT, o.BinaryOp)
    ])


    comparison_expression = pp.infix_notation(variable_name | number | arithmetic_expression, [
        (pp.one_of("< <= >= > == !="), 2, pp.OpAssoc.LEFT, o.BinaryOp)
    ])

    
    # combo_expression = arithmetic_expression ^ bitwise_expression ^ comparison_expression

    combo_expression = number ^ variable_name ^ arithmetic_expression

    conditional_ternary_expr = (combo_expression + pp.Literal("if").suppress() + comparison_expression + pp.Literal("else").suppress() + combo_expression).set_parse_action(o.TernaryCondOp)


    # https://github.com/pyparsing/pyparsing/blob/master/examples/simpleArith.py
    # arithmetic_expression = pp.infix_notation(variable_name | number, [
    #     (pp.one_of("+ -"), 1, pp.OpAssoc.RIGHT, o.UnaryOp),
    #     (pp.one_of("* /"), 2, pp.OpAssoc.LEFT, o.BinaryOp),
    #     (pp.one_of("+ -"), 2, pp.OpAssoc.LEFT, o.BinaryOp)
    # ])

    assignment = (variable_name + "=" + (combo_expression ^ conditional_ternary_expr ^ function_call)).set_results_name("assignment")
    # assignment = (variable_name + "=" + (combo_expression | function_call)).set_results_name("assignment")
    
    # an optional ";" was added to the end of the statement and function return grammars, this is so that it can still match
    # when doing the preprocessing step, and when it comes to parsing the file itself
    # TODO: this might cause issues, maybe split into two seperate variables?
    statement = (pp.Group(assignment) | pp.Group(function_call)) + pp.Opt(semicolon.suppress())

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

    id = pp.Combine(pp.Literal("%") + pp.pyparsing_common.identifier).set_results_name("id")
    literal_string = pp.quoted_string # https://pyparsing-docs.readthedocs.io/en/latest/HowToUsePyparsing.html?highlight=string#common-string-and-token-constants

    opcode = op + pp.Word(pp.alphanums).set_results_name("opcode")

    opcode_args = pp.Group(pp.delimited_list(
        pp.ZeroOrMore(id | literal_string | pp.Word(pp.alphanums) | pp.pyparsing_common.number),
        delim=" ",
        allow_trailing_delim=False
    )).set_results_name("opcode_args")


    operation = opcode + pp.Opt(opcode_args) + nl.suppress()
    assignment = id + eq + operation
    
    line = pp.Group(operation | assignment)

    spirv_body = pp.ZeroOrMore(
        line
    )

    # TODO: is there a way to isolate function blocks using what we currently have?
    #       or does the grammar need to be a lot more specific?
    #       - tried using pp.nested_expr and using the Label and FunctionEnd keywords but
    #           i think that something else is just greedily eating tokens

    # https://pyparsing-docs.readthedocs.io/en/latest/pyparsing.html?highlight=locatedExpr#pyparsing.Located

    # body_start = id + eq + op + pp.Keyword("Label")
    # body_end = op + pp.Keyword("FunctionEnd")
    
    # not_label_or_func_end = (~pp.Keyword("Label") | ~pp.Keyword("FunctionEnd") | pp.Word(pp.alphanums))

    # header = pp.Group(pp.ZeroOrMore(
    #     pp.Group(pp.Opt(id + eq) + op + not_label_or_func_end + pp.Opt(opcode_args) + nl.suppress())
    # ))

    # spirv_body = header + pp.ZeroOrMore(pp.Group(pp.nested_expr(
    #     opener = body_start,
    #     content = pp.ZeroOrMore(line),
    #     closer = body_end
    # )).set_results_name("func_body"))