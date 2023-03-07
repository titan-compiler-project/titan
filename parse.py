import pyparsing as p

# take in python file, replace whitespace with matching braces
# replace colons too
# i.e function def x(): should become def x(){}

def preprocess(machine_object):

    for file in machine_object.files:
        print(f"FILE: {file}")

        # setting up the grammar
        # : --> {
        # how to detect a change in indentation level?
        #   after :, indentation++, so update some var?
        # TODO: https://github.com/pyparsing/pyparsing/blob/master/examples/indentedGrammarExample.py

        # 1. parse functions + statements -- assign result names
        # 2. search through parse results for : and skip over body
        # 3. idea is that the function declaration, :, and function body will be seperate
        #       allowing me to just copy the contents into another array or something
        #   ----> NO! won't work for in-body if statements etc etc.

        #   https://stackoverflow.com/questions/24954340/change-string-during-pyparsing


        ############################################################################
        # identifier = p.Word(p.alphas + "_", p.alphanums+ "_")
        # colon = p.Literal(":")

        # function_declaration = "def" + identifier + p.Group("(" + p.Optional(p.delimited_list(identifier)) + ")") + colon

        # rhs_value = p.Forward() # values that can only be on the right hand side of an expression --- nums/floats, identifiers, function calls
        # statement = p.Forward() # assignment, function def, identifier

        # function_call = identifier + "(" + p.Optional(p.delimited_list(identifier))
        # function_body = p.IndentedBlock(statement)
        # assignment = p.Group(identifier + "=" + rhs_value)

        # function_definition = p.Group(function_declaration + function_body)

        # rhs_value << (function_call | identifier | p.Word(p.nums))
        # statement << (function_declaration | assignment | identifier | p.Group("return" + rhs_value))

        # file_body = p.OneOrMore(statement)

        # results = file_body.parse_file(file)

        # results.pprint()

        ############################################################################

    # p.ParserElement.set_default_whitespace_chars(" \t")

    id = p.pyparsing_common.identifier
    l_br = "("
    r_br = ")"
    colon = ":"
    keyword_def = p.Keyword("def")
    content = p.restOfLine + p.lineEnd
    indented_content = p.IndentedBlock(content, recursive=False)

    func_def = keyword_def + id + l_br + p.Optional(p.Group(p.delimitedList(id))) + r_br + colon

    line = p.Forward()
    
    # line can contain lines of content or indented blocks consisting of lines of content
    # line = (content | indented_content)
    line = content

    
    file_structure = func_def + p.ZeroOrMore(p.Group(line), stop_on=p.LineStart())



    file_result = file_structure.parse_file(file)
    file_result.pprint()
