// example only
module top (
	input wire sys_clock_i,
	input wire spi_clock_i,
	input wire spi_cs_i,     // chip select
	input wire spi_pico_i,   // peripheral in, controller out - rx from mcu
	output wire spi_poci_o   // peripheral out, controller in - tx to mcu
);

	// reg PLL_CLK_50M, PLL_SCLK;
	reg pll_sys_clock_r, pll_spi_clock_r;

	// FPGA specific PLLs
	pll_global_1in pll_global_fpga (sys_clock_i, pll_sys_clock_r);
    pll_regional_1in pll_regional_sclk (spi_clock_i, pll_spi_clock_r);

	logic [7:0] rx_byte_i, tx_byte_o;
	wire rx_valid_w;

	// spi_byte_if uut_spi_slave_cvonk (
		// PLL_CLK_50M, PLL_SCLK, MOSI, MISO, SSEL, tx_byte, rx_byte, rx_valid
	// );

	spi_byte_if spi_interface_cvonk (
		.sysClk(pll_sys_clock_r), .SCLK(pll_spi_clock_r),
		.MOSI(spi_pico_i), .MISO(spi_poci_o), .SS(spi_cs_i),
		.tx(tx_byte_o), .rx(rx_byte_i), .rxValid(rx_valid_w)
	);

	// internal buses used to interface with the cores
	logic [7:0] internal_bus_instruction;
	logic [23:0] internal_bus_address;
	logic [31:0] internal_bus_value, internal_bus_result, internal_bus_stream;

	wire [31:0] internal_bus_stream_w;
	
	// instruction_handler uut_ih (
		// .clk(PLL_CLK_50M), .spi_rx_valid(rx_valid), .spi_rx_byte(rx_byte), .value_from_core(val_out_bus),
		// .stream_bus(stream_bus), .instruction_bus(instr_bus), .address_bus(addr_bus),
		// .value_bus(val_in_bus), .spi_tx_byte(tx_byte)
	// );

	instruction_handler internal_ih (
		.clk(pll_sys_clock_r), .spi_rx_valid(rx_valid_w), .spi_rx_byte(rx_byte_i),
		.value_from_core(internal_bus_result), .stream_bus(internal_bus_stream_w),
		.instruction_bus(internal_bus_instruction), .address_bus(internal_bus_address),
		.value_bus(internal_bus_value), .spi_tx_byte(tx_byte_o)
	);

	// core_interface # (
		// .TOTAL_INPUTS(2), .TOTAL_OUTPUTS(1), .START_ADDRESS(0), .END_ADDRESS(2)
	// ) uut_ci_add2 (
		// .clock(PLL_CLK_50M), 
		// .instruction(instr_bus), 
		// .address(addr_bus), 
		// .value(val_in_bus), 
		// .output_value(val_out_bus), 
		// .stream_bus(stream_bus)
	// );

	core_interface # (
		.TOTAL_INPUTS(2), .TOTAL_OUTPUTS(1), .START_ADDRESS(0), .END_ADDRESS(2)
	) ci_adder (
		.clock(pll_sys_clock_r), .instruction(internal_bus_instruction), .address(internal_bus_address),
		.value(internal_bus_value), .output_value(internal_bus_result), .stream_bus(internal_bus_stream_w)
	);

endmodule