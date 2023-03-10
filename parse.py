# import pyparsing as p

# # take in python file, replace whitespace with matching braces
# # replace colons too
# # i.e function def x(): should become def x(){}

# def preprocess(machine_object):

#     for file in machine_object.files:
#         print(f"FILE: {file}")

#         # setting up the grammar
#         # : --> {
#         # how to detect a change in indentation level?
#         #   after :, indentation++, so update some var?
#         # TODO: https://github.com/pyparsing/pyparsing/blob/master/examples/indentedGrammarExample.py

#         # 1. parse functions + statements -- assign result names
#         # 2. search through parse results for : and skip over body
#         # 3. idea is that the function declaration, :, and function body will be seperate
#         #       allowing me to just copy the contents into another array or something
#         #   ----> NO! won't work for in-body if statements etc etc.

#         #   https://stackoverflow.com/questions/24954340/change-string-during-pyparsing


#         ############################################################################
#         # identifier = p.Word(p.alphas + "_", p.alphanums+ "_")
#         # colon = p.Literal(":")

#         # function_declaration = "def" + identifier + p.Group("(" + p.Optional(p.delimited_list(identifier)) + ")") + colon

#         # rhs_value = p.Forward() # values that can only be on the right hand side of an expression --- nums/floats, identifiers, function calls
#         # statement = p.Forward() # assignment, function def, identifier

#         # function_call = identifier + "(" + p.Optional(p.delimited_list(identifier))
#         # function_body = p.IndentedBlock(statement)
#         # assignment = p.Group(identifier + "=" + rhs_value)

#         # function_definition = p.Group(function_declaration + function_body)

#         # rhs_value << (function_call | identifier | p.Word(p.nums))
#         # statement << (function_declaration | assignment | identifier | p.Group("return" + rhs_value))

#         # file_body = p.OneOrMore(statement)

#         # results = file_body.parse_file(file)

#         # results.pprint()

#         ############################################################################

#     # p.ParserElement.set_default_whitespace_chars(" \t")

#     id = p.pyparsing_common.identifier
#     l_br = p.Literal("(").suppress()
#     r_br = p.Literal(")").suppress()
#     colon = p.Literal(":").suppress()
#     keyword_def = p.Keyword("def").suppress()
#     content = p.restOfLine + p.lineEnd
#     indented_content = p.IndentedBlock(content, recursive=False)

#     # p.Suppress(keyword_def)
#     # l_br.suppress()
#     # r_br.suppress()
#     # colon.suppress()

#     func_def = keyword_def + id + l_br + p.Optional(p.Group(p.delimitedList(id))) + r_br + colon

#     # line = p.Forward()
#     # line can contain lines of content or indented blocks consisting of lines of content
#     # line = (content | indented_content)
#     # line = content

    
#     file_structure = (func_def + p.Group(p.ZeroOrMore(p.Group(content), stop_on=p.LineStart())))

#     # file_structure = p.OneOrMore(
#     #     p.Group(
#     #         func_def + p.ZeroOrMore(content, stop_on=p.LineStart())
#     #     ),
#     # stop_on=(p.LineStart() + keyword_def))


#     file_result = file_structure.parse_file(file)
#     file_result.pprint()

import tokenize
import machine
from typing import NamedTuple
def preprocess(machine_object):

    INDENT_ID = 5
    DEDENT_ID = 6

    for file in machine_object.files:

        indents = []
        dedents = []
        processed_file_content = []
        lines = []

        i_d_pos = []

        class indents_dedents(NamedTuple):
            type: int
            pos: int

        # tokens = []

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
                # if token.type == 4:
                    # print(token)
                    # print(token.line)

                if token.type == INDENT_ID:
                    print(f"indent: '{token.line[:-1]}' {token.start} {token.end}")
                    indents.append(token.start)
                    i_d_pos.append(indents_dedents(INDENT_ID, token.start[0]))
                elif token.type == DEDENT_ID:
                    print(f"dedent: '{token.line[:-1]}' {token.start} {token.end}")
                    dedents.append(token.start)
                    i_d_pos.append(indents_dedents(DEDENT_ID, token.start[0]))

        print()
        for x in range(0, len(lines)):
            print(lines[x])
        print()

        print(indents)
        print(dedents)

        offset = 0

        print(i_d_pos)

        for entry in i_d_pos:
            if entry.type == INDENT_ID:
                lines.insert((entry.pos-1)+offset, "{")
                offset += 1
            elif entry.type == DEDENT_ID:
                lines.insert((entry.pos-1)+offset, "}")
                offset += 1
                # print("dedent")



        # for pos in indents:
            # print(pos[0])
            # lines.insert((pos[0]-1)+offset, "{")
            # offset += 1

        # for pos in dedents:
            # print(pos[0])
            # lines.insert((pos[0]-1)+offset, "}")
            # offset += 1


        print()
        for x in range(0, len(lines)):
            print(lines[x])
        print()