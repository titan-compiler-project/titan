// example only
// this will work for a function that has 2 inputs and 1 output, which are 32 bits wide
// this must be generated by titan for each function
import TitanComms::*;

module core_interface # (
    parameter INSTRUCTION_WIDTH = 8,
    parameter ADDRESS_WIDTH = 24,
    parameter VALUE_WIDTH = 32,
    parameter TOTAL_PARAMETERS,
    parameter START_ADDRESS,
    parameter END_ADDRESS
) (
    input wire clock,
    input wire [INSTRUCTION_WIDTH-1:0] instruction,
    input wire [ADDRESS_WIDTH-1:0] address,
    input wire [VALUE_WIDTH-1:0] value,
    output wire [VALUE_WIDTH-1:0] output_value
);

    TitanComms::instructions instr_enum;

    // VALUE_WIDTH wide memory, 3 units deep
    reg [VALUE_WIDTH-1:0] value_memory [0:2];
    // reg [VALUE_WIDTH-1:0] output_reg; // need to account for total number of outputs


    wire enable = (address >= START_ADDRESS) & (address <= END_ADDRESS);

    // need address in normal range to index memory, not global range
    wire [ADDRESS_WIDTH-1:0] normalised_address = address - START_ADDRESS;  

    reg [VALUE_WIDTH-1:0] output_val_internal;

    always_comb begin
    // always @ (posedge enable) begin
        // if we're being talked to
        if (enable) begin
            unique case (instruction)

                READ: begin
                    output_val_internal <= value_memory[normalised_address];
                end

                WRITE: begin
                    value_memory[normalised_address] <= value;
                end

            endcase
        end
    end

    // might have to add the core instance here?
    // not sure how else i could interface the memory block

    add_2 uut_add2 (
        .clock(clock), .a(value_memory[0]), .b(value_memory[1]), .c(value_memory[2])
    );


    assign output_value = output_val_internal;

endmodule