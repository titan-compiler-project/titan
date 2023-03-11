import tokenize
import machine
from typing import NamedTuple
import pyparsing as pp

def preprocess(machine_object):

    # tokenize IDs, got from experimentation
    # https://docs.python.org/3/library/tokenize.html
    INDENT_ID = 5
    DEDENT_ID = 6

    class BracketPos(NamedTuple):
        type: int
        pos: int

    for file in machine_object.files:

        lines = []
        bracket_positions = []
        joined_lines = ""

        # read file into list
        with open(file) as f:
            lines = f.read().splitlines()

        # tokenize file -- reads file again! does not use lines list defined earlier
        with tokenize.open(file) as f:
            tokens = tokenize.generate_tokens(f.readline)

            for token in tokens:
                # append result (indent/dedent) to list to keep track of position and type
                if token.type == INDENT_ID:
                    # token.start gives tuple (row, col), we only want the row
                    bracket_positions.append(BracketPos(INDENT_ID, token.start[0]))
                elif token.type == DEDENT_ID:
                    bracket_positions.append(BracketPos(DEDENT_ID, token.start[0]))


        # we need to keep track of how many brackets we've inserted
        # so that we insert the next bracket in the correct position
        bracket_offset = 0

        # for every bracket position we've recorded...
        for entry in bracket_positions:
            if entry.type == INDENT_ID:
                # insert {
                lines.insert((entry.pos-1)+bracket_offset, "{")
                bracket_offset += 1
            elif entry.type == DEDENT_ID:
                # or insert }
                lines.insert((entry.pos-1)+bracket_offset, "}")
                bracket_offset += 1

        # converting list into string because it makes it easier when it comes to parsing stage
        joined_lines = "".join(lines)
        # added preprocessed file to list
        # machine_object.processed_text.append(lines)
        machine_object.processed_text.append(joined_lines)

# https://docs.python.org/3/library/typing.html
def parse_processed_python(machine_object: machine.Machine):

    keyword_def = pp.Keyword("def").suppress()
    keyword_return = pp.Keyword("return").suppress()
    keyword_None = pp.Keyword("None")
    function_name = pp.pyparsing_common.identifier
    variable_name = pp.pyparsing_common.identifier
    l_br, r_br = map(pp.Literal, "()")
    l_cbr, r_cbr = map(pp.Literal, "{}")
    colon = pp.Literal(":").suppress()
    number = pp.Word(pp.nums) + pp.Optional("." + pp.Word(pp.nums))

    function_parameter_list = pp.delimitedList(variable_name) | pp.empty
    function_return_list = pp.Group(pp.delimitedList(variable_name | number | keyword_None))
    function_call = function_name + l_br + function_parameter_list + r_br
    arithmetic_expression = pp.infix_notation(variable_name | number, [
        ('-', 1, pp.OpAssoc.RIGHT),
        (pp.one_of("* /"), 2, pp.OpAssoc.LEFT),
        (pp.one_of("+ -"), 2, pp.OpAssoc.LEFT)
    ])
    statement = pp.Group(variable_name + "=" + arithmetic_expression | function_call)

    #checks for: "def function_name(param1, param2):"
    function_definition = keyword_def + function_name.set_results_name("function_name") + l_br.suppress() + function_parameter_list.set_results_name("function_param_list") + r_br.suppress() + colon

    function_body = pp.Group(pp.ZeroOrMore(statement)).set_results_name("function_statements") + pp.Optional(keyword_return  + function_return_list.set_results_name("function_returns"))

    module = function_definition + l_cbr.suppress() + function_body + r_cbr.suppress()

    for entry in machine_object.processed_text:
        # print(entry)
        parse_result = module.parse_string(entry)
        machine_object.parsed_modules.append(parse_result)
        parse_result.pprint()

        print()
        print()

        print(f"func name= {parse_result.function_name}")
        print(f"func params= {parse_result.function_param_list}")
        print(f"func statements= {parse_result.function_statements}")
        print(f"func returns= {parse_result.function_returns}")


    return None