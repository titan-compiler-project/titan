import type as t

print(f"{t.DataType.INTEGER.name}")
print(f"{t.DataType.INTEGER.value}")

if type(3) == t.DataType.INTEGER.value:
    print("so true")

print(t.DataType(type(3)).name)