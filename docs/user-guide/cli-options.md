## Available Options

| Option | Function |
| :- | :- |
| ``-t`` | Specify top function if there are multiple functions in the same source file |
| ``-asm`` | Output SPIR-V assembly code |
| ``-s`` | Only run the SPIR-V generation |
| ``-v`` | Verbose, output debug information to console |
| ``-dd`` | Use a dark theme for the Graphviz diagrams |

To use an option simply pass it as an argument to the program: ``python3 titan/main.py -asm my_file.py``

---

## Source Code
::: titan.main.run_argparse
    options:
        show_root_heading: true
        heading_level: 3