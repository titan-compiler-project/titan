import TitanComms::*;

module instruction_handler # (
    parameter INSTRUCTION_WIDTH = 8,
    parameter ADDRESS_WIDTH = 24,
    parameter VALUE_WIDTH = 32
) (
    input wire spi_rx_valid,
    input wire [7:0] spi_rx_byte,
    input wire [VALUE_WIDTH-1:0] value_from_core,
    output logic [INSTRUCTION_WIDTH-1:0] instruction_bus,
    output logic [ADDRESS_WIDTH-1:0] address_bus,
    output logic [VALUE_WIDTH-1:0] value_bus
);

    logic instruction_received = 0;
    logic [7:0] current_instruction;
    logic [63:0] rebuilt_instruction;

    logic [7:0] expected_byte_count = 0;
    logic [7:0] received_byte_count = 0;
 
    wire logic got_all_data;
    assign got_all_data = expected_byte_count == received_byte_count ? 1 : 0;

    logic [2:0] data_pointer = 0;

    // on new byte get
    always_ff @ (posedge spi_rx_valid) begin
        // might cause issues with adding new instructions because they might be out of range?
        // if the instruction is WRITE, READ or STREAM (long instruction)
        if (!instruction_received & (spi_rx_byte >= 1 & spi_rx_byte <= 3)) begin
            instruction_received <= 1;
            current_instruction <= spi_rx_byte;
            received_byte_count <= 1;

            unique case (spi_rx_byte)
                WRITE: begin
                    expected_byte_count = 8;
                end

                READ: begin
                    expected_byte_count = 4;
                end

                default: begin
                    expected_byte_count = 'hx;
                end
            endcase

            
        // otherwise if the instruction is TRANSFER or REPEAT
        end else if (!instruction_received & (spi_rx_byte >= 4 & spi_rx_byte <= 5)) begin
            current_instruction <= spi_rx_byte;
            $display("%h TRANSFER or REPEAT", spi_rx_byte);
            // TODO: add stuff to control the transfer back

        end else if (instruction_received) begin
            received_byte_count <= received_byte_count + 1;
        end

            // shift any and all data into the register
            rebuilt_instruction <= {rebuilt_instruction[56:0], spi_rx_byte};
    end


    always_ff @ (negedge spi_rx_valid) begin
    // always_ff @ (posedge got_all_data) begin
        if (instruction_received & (received_byte_count == expected_byte_count)) begin
            instruction_received <= 0;
            received_byte_count <= 0;
        end
    end


    // if all data was received, write to busses
    always_comb begin
        if (got_all_data) begin
            unique case (current_instruction)

                WRITE: begin
                    instruction_bus = rebuilt_instruction[63:56];
                    address_bus = rebuilt_instruction[55:32];
                    value_bus = rebuilt_instruction[31:0];
                end

                READ: begin
                    instruction_bus = rebuilt_instruction[32:24];
                    address_bus = rebuilt_instruction[23:0];
                    value_bus = 'hz;
                end

                default: begin
                    instruction_bus = 'hz;
                    address_bus = 'hz;
                    value_bus = 'hz;
                end
            endcase
        end
    end

endmodule