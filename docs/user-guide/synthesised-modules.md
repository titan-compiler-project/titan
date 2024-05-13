The output of the Titan compiler consists of multiple SystemVerilog source files, which can then be used in conjunction with Quartus/Xilinx/other software to create a bitstream for FPGA programming, or fed through an open-source ASIC flow like OpenLane to generate chip layouts.

The core components have been tested on an Altera Cyclone V 5CEFA2F23I7N FPGA dev board from QMTECH. The documentation for this FPGA can be found [here](https://github.com/ChinaQMTECH/QM_CYCLONE_V/tree/master/5CEFA2F23).

The hierarchy looks something like this:
```
├ top
│ ├ SPI Interface
│ ├ Instruction Handler
│ └ Core Interface
│   └ User Module 
```

## Core Modules
### SPI Interface
The SPI interface is provided by [Coert Vonk](http://coertvonk.com/hw/math-talk/introduction-13067), and is available on [GitHub](https://github.com/cvonk/FPGA_SPI). This module exposes 4 wires to the user (CLK, CS, POCI, PICO) which is the only way of getting data in and out of the system. 
*[CLK]: Clock
*[CS]: Chip Select
*[POCI]: Peripheral Out, Controller In
*[PICO]: Peripheral In, Controller Out

### Instruction Handler

The instruction handler module is responsible for receiving bytes from the SPI interface, and interpreting them. For example, if there is no instruction currently active, then the next byte from the SPI interface must be a valid instruction for the module to perform any action. If a valid instruction byte is received, then the module will wait to receive the remaining bytes before setting any internal buses.

!!! info inline end
    Valid instructions and the SPI protocol can be found [here](../comms/#protocol-reference).

Once all of the required bytes have been received, internal buses will be set to appropriate values. For example, if we are attemping to write the value ``0xDE`` to the address ``0x04`` then the instruction handler will wait until the write opcode has been issued (``0x01``), then wait to receive an additional 7 bytes - 3 for the address, 4 for the value.

The instruction bus will be set to ``0x01``, address bus to ``0x04`` and the value bus to ``0xDE``.


### Core Interface
The core interface is a wrapper around the user module/core that allows it to interface with the rest of the system. It interprets the current instruction on the bus and will act accordingly if it is being indexed, determined by the start and end range of its address. 

The core interface provides a memory array for both the inputs and outputs, which are written to by sending instructions. This memory array is directly connected to the inputs and ouputs of the user module, and therefore act similarly to passing parameters to a function in regular code.

Currently only one core interface can be instanciated, as the bus does not contain a multiplexer.

Each core interface is unique to the user module, as the memory depth must change depending on how many parameters the user wants. Furthermore, the user module is actually instanciated within this module.

## User Modules
The user module is genereated by the Titan compiler, when the user passes through a valid Python-subset source file.