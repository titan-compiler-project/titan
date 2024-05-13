import ast, sys

print(f"{sys.argv}")

if len(sys.argv) != 2:
    raise Exception("expected 1 argument for file path")

# https://stackoverflow.com/questions/58924031/generating-a-text-representation-of-pythons-ast
tree = ast.dump(ast.parse(open(sys.argv[1], "r").read()), indent=4)
print(tree)