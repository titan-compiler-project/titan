// example only
// this will work for a function that has 2 inputs and 1 output, which are 32 bits wide
// this must be generated by titan for each function
import TitanComms::*;

module core_interface # (
    parameter INSTRUCTION_WIDTH = 8,
    parameter ADDRESS_WIDTH = 24,
    parameter VALUE_WIDTH = 32,
    parameter TOTAL_INPUTS,
    parameter TOTAL_OUTPUTS,
    parameter START_ADDRESS,
    parameter END_ADDRESS
) (
    input wire clock,
    input wire [INSTRUCTION_WIDTH-1:0] instruction,
    input wire [ADDRESS_WIDTH-1:0] address,
    input wire [VALUE_WIDTH-1:0] value,
    output wire [VALUE_WIDTH-1:0] output_value,
    output wire core_interrupt
);

    localparam LAST_INPUT_ADDRESS = END_ADDRESS - TOTAL_OUTPUTS;
    TitanComms::instructions instr_enum;

    // need address in normal range to index memory, not global range
    wire [ADDRESS_WIDTH-1:0] normalised_input_address = address - START_ADDRESS;
    wire [ADDRESS_WIDTH-1:0] normalised_ouput_address = address - LAST_INPUT_ADDRESS;

    
    wire interface_enable = (address >= START_ADDRESS) & (address <= END_ADDRESS);
    wire addressing_inputs = (address >= START_ADDRESS) & (address <= LAST_INPUT_ADDRESS);
    wire addressing_outputs = (address > LAST_INPUT_ADDRESS) & (address <= END_ADDRESS);
    
    
    logic [VALUE_WIDTH-1:0] input_memory [0:1];  // use params to calculate required depth
    logic [VALUE_WIDTH-1:0] output_memory; // if only one output, we can't make instance using [0]

    (*keep = 1*) logic interrupt_enabled = 0;
    logic core_done_signal;

    assign core_interrupt = interrupt_enabled;
	 
    reg [VALUE_WIDTH-1:0] output_val_internal;

    add_2 uut_add2 (
        .clock(clock), .a(input_memory[0]), .b(input_memory[1]), .c(output_memory), .done(core_done_signal)
    );    

	 always @ (posedge clock) begin

        // if we're not being talked to, but there is another BIND_INTERRUPT instruction
        // means that we have to release the bus
        // if (!interface_enable & instruction == BIND_INTERRUPT) begin
        //     interrupt_enabled = 0;
        // end

        if (interface_enable) begin
            unique case (instruction)

                READ: begin
                    if (addressing_inputs) begin
                        output_val_internal <= input_memory[normalised_input_address];
                    end else if (addressing_outputs) begin
                        // only usable with multiple outputs
                        // output_val_internal <= output_memory[normalised_ouput_address];
                        output_val_internal <= output_memory;
                    end
                end

                WRITE: begin
                    // writing to output_memory is illegal because it would lead to multiple drivers
                    if (addressing_inputs) begin
                        input_memory[normalised_input_address] <= value;
                    end
                end

                BIND_INTERRUPT: begin
                    interrupt_enabled <= 1;    
                    input_memory[0] <= input_memory[0] + 1;
                end

            endcase
        end else if (!interface_enable & (instruction == BIND_INTERRUPT)) begin
            interrupt_enabled <= 0;
        end
    end


    assign output_value = output_val_internal;

endmodule