In order to interface with the generated core, we need some method to get data on and off the FPGA itself. It was decided that SPI would be a good fit - it's fairly common, especially on micrcontrollers, and relatively easy to use.

SPI connects with a hardware module on the FPGA that is waiting for an instruction & the relevant data to arrive, so that it can set the appropriate buses and coordinate data.

An Arduino library (provided by this project) can be used to abstract the communication away into a few simple function calls, helping to improve accessibility. Currently it has been tested on a Teensy 3.2 and the Raspberry Pi Pico.

## Short introduction into SPI
Serial Protocol Interface (SPI) is a protocol that allows devices to communicate in a synchronous, full-duplex manner. It has 4 pins: clock (CLK), chip select (CS), controller-out-peripheral-in (COPI) and peripheral-out-controller-in (POCI).

Three wires are handled by the controller (CLK, CS, COPI) and one by the peripheral (POCI). CLK and CS coordinate the communication, whilst COPI and POCI contain the data which is being transferred across the devices.

## Custom Protocol

Since SPI does not directly define a communications protocol, instead only how it works electrically, it is necessary to outline a protocol that will allow us to communicate with the FPGA.

Packets of information can only be 8 bytes long at maximum, being segmented into 1 byte increments.

The first byte must be a valid instruction (``READ``, ``WRITE``, ``STREAM``, ``BIND_WRITE_ADDRESS``, ``BIND_READ_ADDRESS``, ``TRANSFER``, ``REPEAT``), followed up by additional information if required. For example, if you are executing a ``WRITE`` instruction, you need to provide a 3-byte address and a 4-byte value which gets written to the address; whilst a ``READ`` instruction only requires the 3-byte address as additional data.

In theory any device which implements this protocol will be able to communicate with the FPGA, so it isn't limited to only microcontrollers. This could be done on a PC which bit-bangs the wires, though its unlikely to be useful in that context.

### Protocol Reference

| Mnemonic | Instruction | Fields | Format | Action |
|:-:|:-|:-|:-| :- |
| ``NOP`` | ``0x00`` | No fields | ``NOP`` | No operation |
| ``WRITE`` | ``0x01`` | ``ADDRESS`` (3 bytes), <br> ``VALUE`` (4 bytes) | ``WRITE ADDRESS VALUE``| Write ``VALUE`` to ``ADDRESS`` |
| ``READ`` | ``0x02`` | ``ADDRESS`` (3 bytes) | ``READ ADDRESS`` | Read a value from ``ADDRESS`` <br> (This only places the value in an internal register.) |
| ``STREAM`` | ``0x03`` | ``VALUE`` (4 bytes) | ``STREAM VALUE`` | Stream a ``VALUE`` to a pre-determined address, and recieve a value simultaneously | 
| ``RESERVED`` | ``0x04`` | - | - | Reserved |
| ``BIND_READ_ADDRESS`` | ``0x05`` | ``ADDRESS`` (3 bytes) | ``BIND_READ_ADDRESS ADDRESS`` | Bind to an address to read from when running a ``STREAM`` instruction |
| ``BIND_WRITE_ADDRESS`` | ``0x06`` | ``ADDRESS`` (3 bytes) | ``BIND_WRITE_ADDRESS ADDRESS`` | Bind to an address to write a value to when running a ``STREAM`` instruction |
| ``TRANSFER`` | ``0x07`` | No fields | ``TRANSFER`` | Transfer 1 byte across SPI, advancing the internal data pointer by 1 |
| ``REPEAT`` | ``0x08`` | No fields | ``REPEAT`` | Reset the internal data pointer |
| ``N/A`` | ``0x09 - 0xFE`` | No fields | No format | Unused range |
| ``RESERVED`` | ``0xFF`` | - | - | Reserved |





## Arduino Library
!!! info inline end
    The library is currently on the ``dev`` branch, under ``titan/titan/comms/TitanComms``

A very simple Arduino library is provided for use on the Pico or Teensy 3.2 microcontrollers. It provides functionality for reading, writing and streaming to the core.

However, it is not necessary to use this library. Any device with an SPI connection that implements the protocol is able to communicate to the core.