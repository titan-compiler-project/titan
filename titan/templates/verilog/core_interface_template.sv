import TitanComms::*;

// @titan-core-def
    parameter INSTRUCTION_WIDTH = 8,
    parameter ADDRESS_WIDTH = 24,
    parameter VALUE_WIDTH = 32,
    parameter TOTAL_INPUTS,
    parameter TOTAL_OUTPUTS,
    parameter START_ADDRESS,
    parameter END_ADDRESS
) (
    input wire clk_i,
    input wire [INSTRUCTION_WIDTH-1:0] instruction_i,
    input wire [ADDRESS_WIDTH-1:0] address_i,
    input wire [VALUE_WIDTH-1:0] value_i,
    output wire [VALUE_WIDTH-1:0] result_o,
    output reg [VALUE_WIDTH-1:0] stream_o
);

    localparam LAST_INPUT_ADDRESS = END_ADDRESS - TOTAL_OUTPUTS;

    // need address in normal range to index memory, not global range
    wire [ADDRESS_WIDTH-1:0] normalised_input_address = address_i - START_ADDRESS;
    wire [ADDRESS_WIDTH-1:0] normalised_ouput_address = address_i - LAST_INPUT_ADDRESS;

    
    // if we're getting talked to, and which parts specifically
    wire interface_enable = ((address_i >= START_ADDRESS) & (address_i <= END_ADDRESS));
    wire addressing_inputs = (address_i >= START_ADDRESS) & (address_i <= LAST_INPUT_ADDRESS);
    wire addressing_outputs = (address_i > LAST_INPUT_ADDRESS) & (address_i <= END_ADDRESS);
        
    // @titan-inputs
    // @titan-outputs
    
    logic stream_enabled = 0;
    // logic stream_i_or_o = 0; // 0 = inputs, 1 = outputs
    logic [ADDRESS_WIDTH-1:0] normalised_stream_read_address;
    logic [ADDRESS_WIDTH-1:0] normalised_stream_write_address;
	 
    reg [VALUE_WIDTH-1:0] output_val_internal;

    // @titan-user-module   

	 always @ (posedge clk_i) begin
        // if not being addressed but the current instruction is BINDx then we need to disable our stream output 
        if (!interface_enable & ((instruction_i == BIND_READ_ADDRESS) | (instruction_i == BIND_WRITE_ADDRESS))) begin
            stream_enabled <= 0;
        end

        // TODO: if (stream_enabled) here instead?
        if (instruction_i == STREAM) begin
            if (stream_enabled) begin
                // @titan-stream-input
                // @titan-stream-output
            end
        end else if (interface_enable) begin
        // if (interface_enable) begin
           unique case (instruction_i)

                READ: begin
                    if (addressing_inputs) begin
                        // @titan-read-input
                    end else if (addressing_outputs) begin
                        // @titan-read-output
                    end
                end

                WRITE: begin
                    // writing to output_memory is illegal because it would lead to multiple drivers
                    if (addressing_inputs) begin
                        // @titan-write-input
                    end
                end

                BIND_READ_ADDRESS: begin
                    if (addressing_outputs) begin
                        stream_enabled <= 1;
                        normalised_stream_read_address <= address_i - LAST_INPUT_ADDRESS;
                    end
                end

                BIND_WRITE_ADDRESS: begin
                    if (addressing_inputs) begin
                        stream_enabled <= 1;
                        normalised_stream_write_address <= address_i - START_ADDRESS;
                    end
                end
            endcase
        end
    end

    assign result_o = output_val_internal;

endmodule