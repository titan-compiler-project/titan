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
The SPI interface is provided by [Coert Vonk](http://coertvonk.com/hw/math-talk/introduction-13067), and is available on [GitHub](https://github.com/cvonk/FPGA_SPI). This module exposes 4 wires to the user (CLK, CS, COPI, PICO) which is the only way of getting data in and out of the system. 


### Instruction Handler
<!-- The instruction handler module is responsible for recieving bytes from the SPI interface, and interpreting them. If there is no instruction currently active, and the received byte fits  -->

The instruction handler module is responsible for receiving bytes from the SPI interface, and interpreting them. For example, if there is no instruction currently active, then the next byte from the SPI interface must be a valid instruction for the module to perform any action. If a valid instruction byte is received, then the module will wait to receive the remaining bytes before setting any internal buses.

Once all of the bytes have been received, internal buses will be set to appropriate values. For example, if we are attemping to write the value ``0xDE`` to the address ``0x04`` then the instruction handler will wait until the write opcode has been issued (``0x01``), then wait to receive an additional 7 bytes - 3 for the address, 4 for the value.

The instruction bus will be set to ``0x01``, address bus to ``0x04`` and the value bus to ``0xDE``. 

| Instruction | Opcode | Total bytes to send | Operation |
| :-: | :-: | :-: | :-: |
| ``WRITE`` | ``0x01`` | 8 | Write a value to a given address. |
| ``READ`` | ``0x02`` | 4 | Read a value from the core, onto an internal bus. This is not the same as transferring it across the SPI bus. |
| ``STREAM`` | ``0x03`` | 5 | Send a value to a predetermined address, and receive one from another. ``BIND_READ`` and ``BIND_WRITE`` must be issued first, otherwise the data is not valid. |
| ``BIND_INTERRUPT`` | ``0x04`` | N/A | Not implemented. |
| ``BIND_READ`` | ``0x05`` | 4 | Set an address which to read from whilst streaming. |
| ``BIND_WRITE`` | ``0x06`` | 4 | Set an address which to write to whilst streaming. |
| ``TRANSFER`` | ``0x07`` | 1 | Issue as many times as needed to read a value. Internally increments a pointer that selects a portion of the value to send, due to the 1-byte window of SPI. For a 32-bit value, issue this instruction 4 times. |
| ``REPEAT`` | ``0x08`` | 1 | Reset the internal data pointer to restart the transfer of data. |

### Core Interface
The core interface is a wrapper around the user module/core that allows it to interface with the rest of the system. It interprets the current instruction on the bus and will act accordingly if it is being indexed, determined by the start and end range of its address. 

The core interface provides a memory array for both the inputs and outputs, which are written to by sending instructions. This memory array is directly connected to the inputs and ouputs of the user module, and therefore act similarly to passing parameters to a function in regular code.

Currently only one core interface can be instanciated, as the bus does not contain a multiplexer.

Each core interface is unique to the user module, as the memory depth must change depending on how many parameters the user wants. Furthermore, the user module is actually instanciated within this module.

## User Modules
The user module is genereated by the Titan compiler, when the user passes through a valid Python-subset source file.