!!! warning inline end
    Compatibility with GPUs is not guaranteed!

A Python source file is taken as an input to the compiler. It gets parsed and eventually compiled into SPIR-V assembly. The use of SPIR-V allows the frontend and backend of the compiler to be easily swapped out, and for the SPIR-V assembly to also be used on existing parallel hardware, such as GPUs.

The parsing of the Python source file is performed by Python's AST module. This module, when supplied with Python source code will transform it into a tree which can be programmatically traversed. This feature means that when the AST module is parsing, calls will be made to various functions depending on the expression.

!!! example
    If the AST module encounters a function definition, it'll call ``visit_FunctionDef``, or if you have code that is something like ``a = 4``, it'll call ``visit_Assign``. 

    More details available at the Python Docs [here](https://docs.python.org/3/library/ast.html).

Some additional features (once implemented), such as total functional recursion, will be made available via Python decorators.

## Brief overview of functionality

### Functions & Calls
Calls are currently not supported, however functions can be defined. When compiling a function definition into SPIR-V, debug information and types will be created, as well as parsing of the input and output parameters.

Multiple returns are not supported currently, however you can have an abritrary number of inputs. Both the inputs and outputs must have type hints, so that the compiler does not have to guess the type.

Once all the information has been created, the compiler will call ``super().generic_visit(node)`` to procced further.

### Assignments, Arithmetic & Comparison
These operations are handled a recursive function that will attempt to parse anything related to arithmetic or comparison operations and return the final line ID and context about the line. During its recursion, it will create any necessary types and context structures which are available to access via the SPIR-V helper class.

Nested arithmetic expressions are evaluated with the ``_eval_line`` function. On each call, it'll generate an intermediate ID that will store the value of one operation. A combination of these intermediate IDs will create the final result of the calculation.

!!! example
    An expression like ``c = a + (b / 2)`` would first have ``b / 2`` evaluated and the result placed into a temporary ID, and then ``a + temporaryID`` would get evaluated next.

    In SPIR-V context, would look something like so:
    ```SPIR-V
    %1 = OpSDiv %type_int %b %const_2
    %2 = OpIAdd %type_int %a %1
    OpStore %c %2
    ```

Whilst ``_eval_line`` also handles comparison expressions, it does not directly perform any actions. Instead this is handed off to ``visit_Compare`` and ``visit_IfExp``. This is done because you may perform a comparison operation outside of an if-expression, so the distinction is necessary.