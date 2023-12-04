The compiler is split into two sections: the "frontend" which takes the Python source file and converts it into SPIR-V, and the "backend" which takes the SPIR-V and converts it into SystemVerilog.

The "frontend" makes use of Python's AST class, in order to parse the syntax into something meaningful. Using AST and its calls to relevant functions, we are able to construct the SPIR-V assembly. These functions can be seen in ``titan/ast_crawl.py``.

The "backend" uses Pyparsing to parse the SPIR-V assembly file, as no existing module exists for this function. The grammar is rough, but suitable for this usecase.

The project structure is a little bit scattered, but slowly everything is getting moved into respective folders so that it is easier to follow.

- ``titan/common/``  holds files relevant for common tasks, and which are not directly related to compilation
- ``titan/frontend/`` will hold files relating to the Python → SPIR-V compiler
- ``titan/backend/`` will hold files relating to the SPIR-V → SystemVerilog compiler


These are explained more thoroughly in the next chapters.