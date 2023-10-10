# https://stackoverflow.com/questions/47184677/pyparsing-combining-infixnotation-with-setresultsname
class BaseOp():
    def __repr__(self):
        return f"({self.__class__.__name__}: {self.operator}, {self.operands})"

class UnaryOp(BaseOp):
    def __init__(self, tokens):
        self.operator = tokens[0][0]
        self.operands = tokens[0][1]

class BinaryOp(BaseOp):
    def __init__(self, tokens):
        self.operator = tokens[0][1]
        self.operands = [tokens[0][0], tokens[0][2]]


class TernaryCondOp():
    def __init__(self, tokens):
        self.true_val = tokens[0]
        self.false_val = tokens[2]
        self.condition = tokens[1]

    def __repr__(self):
        return f"({self.__class__.__name__}: true_val: {self.true_val} , false_val: {self.false_val} , cond: {self.condition})"