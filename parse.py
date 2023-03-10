import tokenize
import machine
from typing import NamedTuple

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
        # i_d_pos = []
        bracket_positions = []

        # class indents_dedents(NamedTuple):
        #     type: int
        #     pos: int

        with open(file) as f:
            lines = f.read().splitlines()

        with tokenize.open(file) as f:
            tokens = tokenize.generate_tokens(f.readline)

            # for token in tokens:
            #    print(token)

            # indent -- 5
            # dedent -- 6
            # tuple is: type string start end line
            for token in tokens:

                if token.type == INDENT_ID:
                    # print(f"indent: '{token.line[:-1]}' {token.start} {token.end}")
                    # i_d_pos.append(indents_dedents(INDENT_ID, token.start[0]))
                    bracket_positions.append(BracketPos(INDENT_ID, token.start[0]))
                elif token.type == DEDENT_ID:
                    # print(f"dedent: '{token.line[:-1]}' {token.start} {token.end}")
                    bracket_positions.append(BracketPos(DEDENT_ID, token.start[0]))
                    # i_d_pos.append(indents_dedents(DEDENT_ID, token.start[0]))

        # DEBUG
        # print()
        # for x in range(0, len(lines)):
        #     print(lines[x])
        # print()



        # DEBUG
        # print(bracket_positions)

        bracket_offset = 0

        for entry in bracket_positions:
            if entry.type == INDENT_ID:
                lines.insert((entry.pos-1)+bracket_offset, "{")
                bracket_offset += 1
            elif entry.type == DEDENT_ID:
                lines.insert((entry.pos-1)+bracket_offset, "}")
                bracket_offset += 1

        # DEBUG
        print()
        for x in range(0, len(lines)):
            print(lines[x])
        print()