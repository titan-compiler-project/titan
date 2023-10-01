import cocotb
import random
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock

@cocotb.test()
async def set_and_check(dut):
    """
    set input signals to known value, and check if they arrive at the output when selected
    """

    input_list = [dut.in1, dut.in2, dut.in3, dut.in4]
    rand_inputs = []

    # setting input values
    for i in range(len(input_list)):
        rand_inputs.append(random.randint(0, 2**32))
        input_port = input_list[i]

        input_port.value = rand_inputs[i]

    await Timer(1, "ns")

    for i in range(len(input_list)):
        dut.sel_i.value = i
        await Timer(1, "ns")

        assert dut.mux_o.value == rand_inputs[i]