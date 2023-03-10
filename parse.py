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
        bracket_positions = []

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

        # added preprocessed file to list
        machine_object.processed_text.append(lines)