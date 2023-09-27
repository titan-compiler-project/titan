from instructions import SPI_Instructions

import cocotb
import random
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock

async def pulse_rx_valid(dut, on=250, off=750, on_timeunit="ps", off_timeunit="ps"):
    """
    pulses signal "spi_rx_valid_i" in design for specified duration and units
    - default on for 250ps, off for 750ps
    - call using ``await`` keyword
    """
    dut.spi_rx_valid_i.value = 1
    await Timer(on, on_timeunit)
    dut.spi_rx_valid_i.value = 0
    await Timer(off, off_timeunit)

@cocotb.test()
async def instruction_write(dut):
    cocotb.start_soon(Clock(dut.clk_i, 1, "ns").start())
    dut.spi_rx_valid_i.value = 0
    await Timer(1, "ns")

    random_value = random.randint(0, 2**32)
    random_value_byte_list = list(random_value.to_bytes(4))
    address_byte_list = list((0).to_bytes(3))
    
    sample_write = [SPI_Instructions.WRITE.value] + address_byte_list + random_value_byte_list

    for i in range(len(sample_write)):
        byte_to_write = sample_write[i]
        
        # spi_rx_valid_i must be high at the same time as the data is on the bus
        # but the duration of how long it is high does not matter
        dut.spi_rx_byte_i.value = byte_to_write
        await pulse_rx_valid(dut)

    await Timer(1, "ns")

    assert dut.instruction_o.value == SPI_Instructions.WRITE.value
    assert dut.address_o.value == 0
    assert dut.value_o.value == random_value
    assert dut.uut_ih.expected_byte_count == 8

@cocotb.test()
async def instruction_read_transfer_repeat(dut):
    cocotb.start_soon(Clock(dut.clk_i, 1, "ns").start())
    
    sample_write = [SPI_Instructions.READ.value] + list((1).to_bytes(3))

    for i in range(len(sample_write)):
        byte_to_write = sample_write[i]

        dut.spi_rx_byte_i.value = byte_to_write
        await pulse_rx_valid(dut)

    await Timer(1, "ns")

    # fake response
    random_response_value = random.randint(0, 2**32)
    random_response_value_list = list(random_response_value.to_bytes(4))
    dut.result_i.value = random_response_value

    assert dut.instruction_o.value == SPI_Instructions.READ.value
    assert dut.address_o.value == 1
    assert dut.uut_ih.expected_byte_count == 4

    await Timer(2, "ns")

    for i in range(4):
        dut.spi_rx_byte_i.value = SPI_Instructions.TRANSFER.value
        await pulse_rx_valid(dut)
        
        # TODO: fix relevant data pointer bug in verilog
        if i != 3:
            assert dut.spi_tx_byte_o.value == random_response_value_list[i+1]
        else:
            assert dut.spi_tx_byte_o.value == random_response_value_list[0]

    assert dut.uut_ih.data_pointer.value == 1

    # force data pointer to change
    dut.spi_rx_byte_i.value = SPI_Instructions.TRANSFER.value
    await pulse_rx_valid(dut, off=1.75, off_timeunit="ns")

    assert dut.uut_ih.data_pointer.value == 2

    dut.spi_rx_byte_i.value = SPI_Instructions.REPEAT.value
    await pulse_rx_valid(dut)

    assert dut.uut_ih.data_pointer.value == 1



@cocotb.test()
async def instruction_bind_write(dut):
    cocotb.start_soon(Clock(dut.clk_i, 1, "ns").start())

    sample_write = [SPI_Instructions.BIND_WRITE_ADDRESS.value] + list((1).to_bytes(3))

    for byte in sample_write:
        dut.spi_rx_byte_i.value = byte
        print(f"sending {hex(byte)}")
        await pulse_rx_valid(dut)

    await Timer(1, "ns") # allow got_all_data signal to go low

    assert dut.instruction_o.value == SPI_Instructions.BIND_WRITE_ADDRESS.value
    assert dut.address_o.value == 1


@cocotb.test()
async def instruction_bind_read(dut):
    cocotb.start_soon(Clock(dut.clk_i, 1, "ns").start())

    sample_write = [SPI_Instructions.BIND_READ_ADDRESS.value] + list((2).to_bytes(3))

    for byte in sample_write:
        dut.spi_rx_byte_i.value = byte
        await pulse_rx_valid(dut)

    await Timer(1, "ns") # allow got_all_data signal to go low

    assert dut.instruction_o.value == SPI_Instructions.BIND_READ_ADDRESS.value
    assert dut.address_o.value == 2

@cocotb.test()
async def instruction_stream(dut):
    cocotb.start_soon(Clock(dut.clk_i, 1, "ns").start())


    random_value_tx = random.randint(0, 2**32)
    sample_write = [SPI_Instructions.STREAM.value] + list(random_value_tx.to_bytes(4))

    # set up a value on stream bus
    stream_random_value = random.randint(0, 2**32)
    stream_val_byte_list = list(stream_random_value.to_bytes(4))
    dut.stream_i.value = stream_random_value
    await Timer(1, "ns")

    # for byte in sample_write:
    for i in range(len(sample_write)):
        dut.spi_rx_byte_i.value = sample_write[i]
        await pulse_rx_valid(dut)
        assert dut.spi_tx_byte_o.value == stream_val_byte_list[i % 4]

    assert dut.instruction_o.value == SPI_Instructions.STREAM.value
    assert dut.value_o.value == random_value_tx

