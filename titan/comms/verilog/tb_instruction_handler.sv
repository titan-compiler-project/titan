import TitanComms::*;
module tb_instruction_handler;


    localparam CLOCK = 5;
    reg clk = 0;
    always #CLOCK clk = ~clk;


    reg rx_valid = 0;
    reg [7:0] rx_byte = 0;

    logic [7:0] instr_bus;
    logic [23:0] addr_bus;
    logic [31:0] val_bus;

    instruction_handler uut_ih (
        .spi_rx_valid(rx_valid), .spi_rx_byte(rx_byte),
        .instruction_bus(instr_bus), .address_bus(addr_bus),
        .value_bus(val_bus)
    );

    initial begin
        #CLOCK;

        rx_byte = TRANSFER; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;

        #CLOCK;

        // read (instruction) at DEDEDE
        rx_byte = 'h2; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        rx_byte = 'h5; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        rx_byte = 'hDE; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK; 
        rx_byte = 'hDE; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK; 

        #CLOCK; #CLOCK;

        rx_byte = TRANSFER; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;

        // read (instruction) at ADDEEF
        // rx_byte = READ; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hAD; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hDE; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK; 
        // rx_byte = 'hEF; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK; 

        // #CLOCK; #CLOCK;

        // // write at AABBCC the value DEADBEEF
        // rx_byte = WRITE; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hAA; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hBB; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hCC; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hDE; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hAD; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hBE; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hEF; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;

        // #CLOCK; #CLOCK;

        // // stream value into function FF00FF00
        // rx_byte = STREAM; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hFF; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'h00; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hFF; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'h00; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;


    end

endmodule