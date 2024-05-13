module top (
	input wire sys_clock_i,
	input wire spi_clock_i,
	input wire spi_cs_i,     // chip select
	input wire spi_pico_i,   // peripheral in, controller out - rx from mcu
	output wire spi_poci_o   // peripheral out, controller in - tx to mcu
);

	reg pll_sys_clock_r, pll_spi_clock_r;

	// NOTE: these modules are for the Altera/Intel PLL IP, they probably can be replaced
	//		 with just the signal itself, but there may be unexpected side effects.
	//		 If using a non-Altera/Intel FPGA, please update these to reflect your device.
	pll_global_1in pll_global_fpga (sys_clock_i, pll_sys_clock_r);
    pll_regional_1in pll_regional_sclk (spi_clock_i, pll_spi_clock_r);

	logic [7:0] rx_byte_i, tx_byte_o;
	wire rx_valid_w;

	spi_byte_if spi_interface_cvonk (
		.sysClk(pll_sys_clock_r), .SCLK(pll_spi_clock_r),
		.MOSI(spi_pico_i), .MISO(spi_poci_o), .SS(spi_cs_i),
		.tx(tx_byte_o), .rx(rx_byte_i), .rxValid(rx_valid_w)
	);

	// internal buses used to interface with the cores
	logic [7:0] internal_bus_instruction;
	logic [23:0] internal_bus_address;
	logic [31:0] internal_bus_value, internal_bus_result;
	wire [31:0] internal_bus_stream_w;

	instruction_handler internal_ih (
		.clk_i(pll_sys_clock_r), .spi_rx_valid_i(rx_valid_w), .spi_rx_byte_i(rx_byte_i),
		.result_i(internal_bus_result), .stream_i(internal_bus_stream_w),
		.instruction_o(internal_bus_instruction), .address_o(internal_bus_address),
		.value_o(internal_bus_value), .spi_tx_byte_o(tx_byte_o)
	);

	// Core Interface instances go here

endmodule