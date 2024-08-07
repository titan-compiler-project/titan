!!! warning
    This is currently a work-in-progress compiler. Please be aware that there will be some bugs stil rumaging around in the code. 

## Setting up

### Cloning & Installing
To get started, clone the compiler [repository](https://github.com/titan-compiler-project/titan). The ``master`` branch usually has builds which are slightly out of date, but should be functioning. The ``dev`` branch is more up-to-date, but could be broken.

Clone the master repo:
```bash
git clone -b master https://github.com/titan-compiler-project/titan
```

Move into the cloned directory:
``bash
cd titan
``

Install the required Python packages as specified in ``requirements.txt`` by running:
```bash
pip install -r requirements.txt
```

Once cloned, execute ``titan/main.py`` with the appropriate command line arguments to run the compiler. There are example files available in the repository, under ``titan/sample_code/``.

To execute the ``simple_neuron.py`` program, you can run the following in your terminal:
```bash
python3 titan/main.py titan/sample_code/simple_neuron.py
```

This is the source file being compiled by the command above:
```python title="simple_neuron.py"
def step(x0:int, x1:int, x2:int, x3:int) -> int:
    w0 = 3
    w1 = 4
    w2 = -1
    w3 = -2
    
    a = ((w0*x0) + (w1*x1)) + ((w2*x2) + (w3*x3))
    r = a if a > 0 else 0
    return r
```
It generates the following SystemVerilog code:
```SystemVerilog title="simple_neuron.sv"
module step (
	input logic clock_i,
	input logic [31:0] x0,
	input logic [31:0] x1,
	input logic [31:0] x2,
	input logic [31:0] x3,
	output logic [31:0] r
);
	logic [31:0] titan_id_0;
	logic [31:0] titan_id_1;
	logic [31:0] titan_id_3;
	logic [31:0] titan_id_4;
	logic [31:0] titan_id_2;
	logic [31:0] titan_id_5;
	logic [31:0] titan_id_6;
	logic [31:0] titan_id_8;
	always_ff @ (posedge clock_i) begin
		titan_id_0 <= 3 * x0;
		titan_id_1 <= 4 * x1;
		titan_id_3 <= -1 * x2;
		titan_id_4 <= -2 * x3;
		titan_id_2 <= titan_id_0 + titan_id_1;
		titan_id_5 <= titan_id_3 + titan_id_4;
		titan_id_6 <= titan_id_2 + titan_id_5;
		titan_id_8 <= titan_id_6 > 0 ? titan_id_6 : 0;
	end
	assign r = titan_id_8;
endmodule
```

There are optional arguments available to modify the behaviour of the compiler. A reference is available [here](../cli-options).

You should then be able to import these files into an FPGA project and program your device.

### Flashing & Running

You can use the generated SystemVerilog files and program an FPGA with it, provided that it contains enough logic elements for your design.

!!! info
    The compiler currently does not automatically generate the necessary interface HDL files, these are available in ``titan/templates/verilog`` and can be modified to suit your module. 


#### Altera/Intel
1. Create a new project via the New Project Wizard in Quartus Prime.
2. Import your source files.
3. Assign FPGA pins - the current interface method requires 4 pins for SPI + 1 for the system clock. Make sure these are accessible and set to the correct direction.
4. Run the compilation and flash onto the FPGA, or run a simulation.

#### Xilinx/AMD/Others
The process is likely to be similar for other FPGA vendors, I simply do not have access to other FPGAs to write about it.


## Subset
This compiler translates a *subset* of Python, and therefore some traditional features may not be available. Please ensure that your code fits within the defined subset so that it can be compiled. Additional features will require additional compiler work to make them compatible.

### Types & Type hinting
Type hinting is required in both the function signature and when declaring a new variable with no default value, or no expression where the type can be inherited.

Supported types:

- Integers
- Booleans
- Floats*

Floats can be converted into SPIR-V, but additional work is needed so that correct SystemVerilog can be generated. See issue [#7](https://github.com/titan-compiler-project/titan/issues/7).

Support for arrays is also limited, and requires you to define them via a decorator.


### Functions
Functions can be defined, with type hinted parameters and with a single return but currently they cannot be called from the main function. Recursive functions are also not yet supported. See issues [#10](https://github.com/titan-compiler-project/titan/issues/10) and [#11](https://github.com/titan-compiler-project/titan/issues/11).


### Returns
Only a variable can be returned - no immediate values or expressions (such as ``a + 3``).


### Arithmetic & Comparison operations
Addition ``+``, subtraction ``-``, division ``/``, multiplication ``*``, left & right shift ``<<``/``>>``, equal/not equal ``==``/``!=``, less than/less than or equal to ``<``/``<=``, greater than/greater than or equal to ``>``/``>=`` is supported for both integers and floats when compiling Python -> SPIR-V.

Division & floating point operators may fail when compiling to SystemVerilog -- this has not been fully tested, you've been warned!


### Classes/Objects
Classes/Objects/other instances of OOP are not supported. This includes using dot operators to access attributes of an object.

### Importing
``import`` and ``import x as y`` statements can be processed, but it does not mean that the library itself will be included! It seems counterproductive, but it is used to only allow compatability with certain features of Numpy. These libraries will more than likely make use of unsupported syntax, requiring more work than necessary to get Titan working with it.

``import x from y`` statements will also fail, again because there is no direct importing of code from external libraries.


### Decorators
Not implemented & reserved - these will be used to mark functions which should behave slightly differently. See issue [#8](https://github.com/titan-compiler-project/titan/issues/8). 


### Maps/Loops
No support at the moment. Should be implemented but requires evaluating whether the loop contains dependencies. 


### If-statements
Only the ternary if statement (``a if c > b else d``) is supported, no regular ``if...elif...else`` statements.