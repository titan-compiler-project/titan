import TitanComms::*;
module tb_core_interface;

    localparam CLOCK = 5;
    reg clk = 0;
    always #CLOCK clk = ~clk;

    TitanComms::instructions instr_enum;

    reg [7:0] instruction = NOP;
    reg [23:0] address = 0;
    reg [31:0] value, returned_value;

    core_interface # (
        .START_ADDRESS(0), .END_ADDRESS(2), .TOTAL_INPUTS(2), .TOTAL_OUTPUTS(1)

    ) uut_cf (
        .clock(clk), .instruction(instruction),
        .address(address), .value(value), .output_value(returned_value)
    );


    initial begin
        #CLOCK;

        address = 'h0;
        value = 'h7;
        instruction = WRITE; // write 1 to first parameter
        #CLOCK; #CLOCK;

        address = 'h1; // write 1 to second parameter
        value = 'h3;
        #CLOCK; #CLOCK;

        #CLOCK; #CLOCK;

        address = 'h2; // read output
        instruction = READ;
        #CLOCK; #CLOCK;

        address = 'h3; // testing if enable goes low when outside of addr range
        #CLOCK; #CLOCK;
    end
endmodule