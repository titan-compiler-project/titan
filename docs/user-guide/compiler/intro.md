The compiler is split into two sections: the "frontend" which takes the Python source file and converts it into SPIR-V, and the "backend" which takes the SPIR-V and converts it into SystemVerilog.

The "frontend" makes use of Python's AST class, in order to parse the syntax into something meaningful. Using AST and its calls to relevant functions, we are able to construct the SPIR-V assembly. These functions can be seen in ``titan/spirv.py``.

The "backend" uses Pyparsing to parse the SPIR-V assembly file, as no existing module exists for this function. The grammar is rough, but suitable for this usecase.

Rough intro to the project structure:
- ``titan/common/``  holds files relevant for common tasks, and which are not directly related to compilation
- ``titan/compiler/`` holds files relating to the Python → SPIR-V compiler, and the SPIR-V → SystemVerilog compiler
- ``titan/comms/`` holds files relating to the communication, such as SystemVerilog RTL and the Arduino communications library