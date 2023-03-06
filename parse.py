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