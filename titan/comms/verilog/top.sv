// example only
module top (
	input wire FPGA_clock,
	input wire SPI_clock,
	input wire SSEL,
	input wire MOSI,
	output wire MISO
);

	reg PLL_CLK_50M, PLL_SCLK;

	// FPGA specific PLLs
	pll_global_1in pll_global_fpga (FPGA_clock, PLL_CLK_50M);
	pll_regional_1in pll_regional_sclk (SPI_clock, PLL_SCLK);

	logic [7:0] rx_byte;
	logic [7:0] tx_byte;
	logic rx_valid;

	spi_byte_if uut_spi_slave_cvonk (
		PLL_CLK_50M, PLL_SCLK, MOSI, MISO, SSEL, tx_byte, rx_byte, rx_valid
	);

	logic [7:0] instr_bus;
	logic [23:0] addr_bus;
	logic [31:0] val_in_bus, val_out_bus, stream_bus;

	// instruction_handler uut_ih (
		// PLL_CLK_50M, rx_valid, rx_byte, val_out_bus, instr_bus, addr_bus, val_in_bus,
		// tx_byte
	// );

	instruction_handler uut_ih (
		.clk(PLL_CLK_50M), .spi_rx_valid(rx_valid), .spi_rx_byte(rx_byte), .value_from_core(val_out_bus),
		.stream_bus(stream_bus), .instruction_bus(instr_bus), .address_bus(addr_bus),
		.value_bus(val_in_bus), .spi_tx_byte(tx_byte)
	);

	// core + interface
	// core_interface # (
	// 	.TOTAL_INPUTS(2), .TOTAL_OUTPUTS(1), .START_ADDRESS(0), .END_ADDRESS(2)
	// ) uut_ci_add2 (
	// 	PLL_CLK_50M, instr_bus, addr_bus, val_in_bus, val_out_bus, stream_bus
	// );


	core_interface # (
		.TOTAL_INPUTS(2), .TOTAL_OUTPUTS(1), .START_ADDRESS(0), .END_ADDRESS(2)
	) uut_ci_add2 (
		.clock(PLL_CLK_50M), 
		.instruction(instr_bus), 
		.address(addr_bus), 
		.value(val_in_bus), 
		.output_value(val_out_bus), 
		.stream_bus(stream_bus)
	);

endmodule