import TitanComms::*;

module instruction_handler # (
    parameter INSTRUCTION_WIDTH = 8,
    parameter ADDRESS_WIDTH = 24,
    parameter VALUE_WIDTH = 32
) (
    input wire clk,
    input wire spi_rx_valid,
    input wire [7:0] spi_rx_byte,
    input wire [VALUE_WIDTH-1:0] value_from_core,
    output logic [INSTRUCTION_WIDTH-1:0] instruction_bus,
    output logic [ADDRESS_WIDTH-1:0] address_bus,
    output logic [VALUE_WIDTH-1:0] value_bus,
    output logic spi_tx_valid,
    output logic [7:0] spi_tx_byte
);

    logic instruction_received = 0;
    logic [7:0] current_instruction;
    logic [63:0] rebuilt_instruction;

    logic [7:0] expected_byte_count = 0;
    logic [7:0] received_byte_count = 0;
 
    wire logic got_all_data;
    assign got_all_data = expected_byte_count == received_byte_count ? 1 : 0;

    wire logic data_valid;
    logic [1:0] data_pointer = 0;

    // on new byte get
    always_ff @ (posedge spi_rx_valid) begin
        $monitor("(%g) data pointer %h", $time, data_pointer);

        // might cause issues with adding new instructions because they might be out of range?
        // if the instruction is WRITE, READ or STREAM (long instruction)

            if (!instruction_received & (spi_rx_byte >= 1 & spi_rx_byte <= 3)) begin
                data_pointer <= 0;
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

                // reset datapointer if we need to send entire thing again
                if (spi_rx_byte == REPEAT) begin
                    data_pointer <= 0;
                    
                end else if (spi_rx_byte == TRANSFER) begin
                    // https://stackoverflow.com/questions/18067571/indexing-vectors-and-arrays-with
                    // spi_tx_byte <= value_from_core[8 * data_pointer +: 8]; // sends LSB first
                    spi_tx_byte <= value_from_core[31 - (8 * data_pointer) -: 8]; // sends MSB first
                    data_pointer <= data_pointer + 1;
                    spi_tx_valid <= 1;
                end

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
        end else if (current_instruction == TRANSFER) begin
            spi_tx_valid = 0;
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