import tokenize, machine, io
from typing import NamedTuple
from grammar import *
import pyparsing as pp


def preprocess(machine_object):

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

      
        for x in range(0, len(lines)):
            line = lines[x]

            try:
                # we dont really care about the tokens, we just want the line that matches
                # TODO: search_string() maybe be better in this situation, but it is not matching correctly
                _ = (TitanPythonGrammar.statement | TitanPythonGrammar.keyword_return + pp.rest_of_line).parse_string(line)
            except pp.exceptions.ParseException:
                # if we get a line that doesn't match the statement grammar we just continue anyway
                # TODO: is this really the best way to handle this?
                continue
            else:
                lines[x] = line + ";" # overwrite with line + semicolon

        # converting list into string because it makes it easier when it comes to parsing stage
        joined_lines = " ".join(lines)

        # added preprocessed file to list
        machine_object.processed_text.append(joined_lines)

# https://docs.python.org/3/library/typing.html
def parse_processed_python(machine_object: machine.Machine):

    for entry in machine_object.processed_text:
        parse_result = TitanPythonGrammar.module.parse_string(entry)
        machine_object.parsed_modules.append(parse_result)
        # parse_result.pprint()

        for result in parse_result:
            machine_object.functions.append(
                machine.Function(
                  name= result.function_name,
                  params= result.function_param_list,
                  body= result.function_statements,
                  returns= result.function_returns,
                  return_type= result.function_return_type
                )
            )


def parse_spriv(m: machine.Machine):

    # creates file in memory using what has already been generated
    with io.StringIO(m.SPIRV_asm_obj.create_file_as_string()) as x:
        # applies grammar
        parse_result = TitanSPIRVGrammar.spirv_body.parse_file(x)

    return parse_result