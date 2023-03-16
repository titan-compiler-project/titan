import tokenize
import machine, generate
from grammar import *
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

        # print(f"LINES FROM PARSE: {lines}")

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
                # _ = (TitanPythonGrammar.statement | TitanPythonGrammar.keyword_return + pp.rest_of_line).parse_string(line)
                _ = (TitanPythonGrammar.statement | TitanPythonGrammar.keyword_return + pp.rest_of_line).parse_string(line)
            except pp.exceptions.ParseException:
                # if we get a line that doesn't match the statement grammar we just continue anyway
                # TODO: is this really the best way to handle this?
                continue
            else:
                # print(f"{line};")
                lines[x] = line + ";" # overwrite with line + semicolon


        # print(lines)
        # converting list into string because it makes it easier when it comes to parsing stage
        joined_lines = " ".join(lines)

        # added preprocessed file to list
        machine_object.processed_text.append(joined_lines)

# https://docs.python.org/3/library/typing.html
def parse_processed_python(machine_object: machine.Machine):

    for entry in machine_object.processed_text:
        # print(entry)
        # parse_result = module.parse_string(entry)
        parse_result = TitanPythonGrammar.module.parse_string(entry)
        machine_object.parsed_modules.append(parse_result)
        # parse_result.pprint()

        for result in parse_result:
            machine_object.functions.append(
                machine.Function(
                  name= result.function_name,
                  params= result.function_param_list,
                  body= result.function_statements,
                  returns = result.function_returns
                )
            )
            # print(f"func name= {result.function_name}")
            # print(f"func params= {result.function_param_list}")
            # print(f"func statements= {result.function_statements}")
            # print(f"func returns= {result.function_returns}")
            # print()