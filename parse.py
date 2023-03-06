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
        #
        #   https://stackoverflow.com/questions/24954340/change-string-during-pyparsing