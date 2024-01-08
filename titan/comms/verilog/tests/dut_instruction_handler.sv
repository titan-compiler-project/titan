module dut_instruction_handler (
    input wire clk_i,
    input wire spi_rx_valid_i,
    input wire [7:0] spi_rx_byte_i,
    input wire [31:0] result_i,
    input wire [31:0] stream_i,
    output wire [7:0] instruction_o,
    output wire [23:0] address_o,
    output wire [31:0] value_o,
    output wire [7:0] spi_tx_byte_o
);

    `ifdef COCOTB_SIM
        initial begin
            $dumpfile ("waves_dut_instruction_handler.vcd");
            // https://stackoverflow.com/questions/37368155/what-does-unable-to-bind-wire-error-mean
            $dumpvars (0, uut_ih);
            #1;
        end
    `endif

    instruction_handler uut_ih (
        .clk_i(clk_i), .spi_rx_valid_i(spi_rx_valid_i), .spi_rx_byte_i(spi_rx_byte_i),
        .result_i(result_i),.stream_i(stream_i), .instruction_o(instruction_o), 
        .address_o(address_o), .value_o(value_o), .spi_tx_byte_o(spi_tx_byte_o)
    );

endmodule