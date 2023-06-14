import TitanComms::*;
module tb_instruction_handler;


    localparam CLOCK = 2;
    reg clk = 0;
    always #CLOCK clk = ~clk;


    reg rx_valid = 0;
    reg [7:0] rx_byte = 0;

    logic [7:0] instr_bus;
    logic [23:0] addr_bus;
    logic [31:0] val_bus, val_out_bus;

    instruction_handler uut_ih (
        .clk(clk),
        .spi_rx_valid(rx_valid), .spi_rx_byte(rx_byte),
        .instruction_bus(instr_bus), .address_bus(addr_bus),
        .value_bus(val_bus), .value_from_core(val_out_bus)
    );

    core_interface # (
        .TOTAL_INPUTS(2), .TOTAL_OUTPUTS(1), .START_ADDRESS(0), .END_ADDRESS(2)
    ) uut_c_add2 (
        .clock(clk), .instruction(instr_bus), .address(addr_bus),
        .value(val_bus), .output_value(val_out_bus)
    );

    initial begin
    /*    // #4;

        // rx_byte = TRANSFER; rx_valid = 1; #4; rx_valid = 0; #4;

        // #4;

        // // read (instruction) at DEDEDE
        // rx_byte = 'h2; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = 'h5; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = 'hDE; rx_valid = 1; #4; rx_valid = 0; #4; 
        // rx_byte = 'hDE; rx_valid = 1; #4; rx_valid = 0; #4; 

        // #CLOCK; #CLOCK;

        // rx_byte = TRANSFER; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = REPEAT; rx_valid = 1; #4; rx_valid = 0; #4;

        // rx_byte = TRANSFER; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_valid = 1; #4; rx_valid = 0; #4;
        // // rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;

        // // read (instruction) at ADDEEF
        // rx_byte = READ; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hAD; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hDE; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK; 
        // rx_byte = 'hEF; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK; 

        // #CLOCK; #CLOCK;

        // // write at AABBCC the value DEADBEEF
        // rx_byte = 'h1; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = 'hAA; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = 'hBB; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = 'hCC; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = 'hDE; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = 'hAD; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = 'hBE; rx_valid = 1; #4; rx_valid = 0; #4;
        // rx_byte = 'hEF; rx_valid = 1; #4; rx_valid = 0; #4;

        // #CLOCK; #CLOCK;

        // // stream value into function FF00FF00
        // rx_byte = STREAM; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hFF; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'h00; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'hFF; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;
        // rx_byte = 'h00; rx_valid = 1; #CLOCK; rx_valid = 0; #CLOCK;

    */

        #4;

        // write at 000 the value 1
        rx_byte = WRITE; rx_valid = 1; #4; rx_valid = 0; #4;
        rx_byte = 0; rx_valid = 1; #4; rx_valid = 0; #4;
        rx_valid = 1; #4; rx_valid = 0; #4;
        rx_valid = 1; #4; rx_valid = 0; #4;
        rx_valid = 1; #4; rx_valid = 0; #4;
        rx_valid = 1; #4; rx_valid = 0; #4;
        rx_valid = 1; #4; rx_valid = 0; #4;
        rx_byte = 1; rx_valid = 1; #4; rx_valid = 0; #4;

        // write at 001 the value 2
        rx_byte = WRITE; rx_valid = 1; #4; rx_valid = 0; #4; // 1
        rx_byte = 0; rx_valid = 1; #4; rx_valid = 0; #4; //  0
        rx_valid = 1; #4; rx_valid = 0; #4;              //  0
        rx_byte = 1; rx_valid = 1; #4; rx_valid = 0; #4; //  1
        rx_byte = 0; rx_valid = 1; #4; rx_valid = 0; #4; //  0
        rx_valid = 1; #4; rx_valid = 0; #4;              //  0
        rx_valid = 1; #4; rx_valid = 0; #4;              //  0
        rx_byte = 2; rx_valid = 1; #4; rx_valid = 0; #4; //  2
        
        // read from 003
        rx_byte = READ; rx_valid = 1; #4; rx_valid = 0; #4;
        rx_byte = 0; rx_valid = 1; #4; rx_valid = 0; #4;
        rx_byte = 0; rx_valid = 1; #4; rx_valid = 0; #4;
        rx_byte = 2; rx_valid = 1; #4; rx_valid = 0; #4;

        rx_byte = TRANSFER; rx_valid = 1; #4; rx_valid = 0; #4;
        rx_valid = 1; #4; rx_valid = 0; #4;
        rx_valid = 1; #4; rx_valid = 0; #4;
        rx_valid = 1; #4; rx_valid = 0; #4;

    end

endmodule