import sys
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv[1:]) != 1:
        print(f"missing arg, expected file name")
    else:
        print(f"got arg: {sys.argv[1]}")
        print(f"file exist? {Path(sys.argv[1]).is_file()}")
    