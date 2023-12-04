!!! warning
    This is currently a work-in-progress compiler. Please be aware that there will be some bugs stil rumaging around in the code. 

## Installing and Running

To get started, clone the compiler [repository](https://github.com/titan-compiler-project/titan). The ``master`` branch usually has builds which are slightly out of date, but should be functioning. The ``dev`` branch is more up-to-date, but could be broken. You will need to install ``pyparsing``. 

Once cloned, execute ``titan/main.py`` with the appropriate command line arguments to run the compiler. For example, to compile a file called ``my_epic_module.sv``, we would run ``python3 titan/main.py my_epic_module.py``. 

There are optional arguments available to modify the behaviour of the compiler. A reference is available <a  href="/user_guide/cli_options">here</a>, and also provided below.

If the compilation is successful, you will have some SystemVerilog (.sv) files within the directory. You should then be able to import these files into an FPGA project (Altera or Xilinx) and program your device.

!!! info
    The compiler currently does not automatically generate the necessary interface HDL files, these are available in ``titan/comms/verilog`` and can be modified to suit your module. Apologies for the inconvencience. 

!!! note
    If you notice any bugs, feel free to make an issue on GitHub :)

## Subset

Please ensure that your code fits within the defined subset so that it can be compiled.

### Valid Features

- 32-bit integers & floats
- Booleans
- Type hints
- Arithmetic operations
- Comparison operations

#### To-do
- [ ] Maps
- [ ] Delayed inputs
- [ ] Limited recursion
- [ ] Automatic interface generation from template
- [ ] Arrays

### Example of a valid program

```py
def my_cool_adder(a:int, b:int) -> int:
    return a + b
```

!!! note
    Type hints are now required.