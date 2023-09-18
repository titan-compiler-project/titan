import TitanComms::*;

module instruction_handler # (
    parameter INSTRUCTION_WIDTH = 8,
    parameter ADDRESS_WIDTH = 24,
    parameter VALUE_WIDTH = 32
) (
    input wire clk_i,
    input wire spi_rx_valid_i,
    input wire [7:0] spi_rx_byte_i,
    input wire [VALUE_WIDTH-1:0] result_i,
    inout reg [VALUE_WIDTH-1:0] stream_i,
    output logic [INSTRUCTION_WIDTH-1:0] instruction_o,
    output logic [ADDRESS_WIDTH-1:0] address_o,
    output logic [VALUE_WIDTH-1:0] value_o,
    output logic [7:0] spi_tx_byte_o
);

    logic instruction_received = 0;
    logic [7:0] current_instruction;
    logic [63:0] rebuilt_instruction;
    logic [ADDRESS_WIDTH-1:0] interrupt_address, stream_address;


    // TODO: clean this up
    //             63                               31                             0
    //              | byte7 | byte6 | byte5 | byte4 | byte3 | byte2 | byte1 | byte0 |
    // write        | instr |       address         |            value              | - 8 bytes
    // read                                         | instr |      address          | - 4 bytes
    // stream                               | instr |            value              | - 5 bytes
    // bind_intr
    // bind read                                    | instr |      address          | - 4 bytes
    // bind write                                   | instr |      address          | - 4 bytes
    // transfer                                                            | instr  | - 1 byte
    // repeat                                                              | instr  | - 1 byte


    logic [7:0] byte0, byte1, byte2, byte3, byte4, byte5, byte6, byte7;
    assign byte7 = rebuilt_instruction[63:56];
    assign byte6 = rebuilt_instruction[55:48];
    assign byte5 = rebuilt_instruction[47:40];
    assign byte4 = rebuilt_instruction[39:32];
    assign byte3 = rebuilt_instruction[31:24];
    assign byte2 = rebuilt_instruction[23:16];
    assign byte1 = rebuilt_instruction[15:8];
    assign byte0 = rebuilt_instruction[7:0];


    logic [7:0] expected_byte_count = 0;
    logic [7:0] received_byte_count = 0;
 
    (*keep = 1*) wire logic got_all_data;
    assign got_all_data = expected_byte_count == received_byte_count ? 1'b1 : 1'b0;
	 
    logic [1:0] data_pointer = 2'b01;

    always_ff @ (posedge clk_i) begin
        $monitor("(%g) data pointer %h", $time, data_pointer);

        // might cause issues with adding new instructions because they might be out of range?
        // if the instruction is WRITE, READ or STREAM (long instruction)

        if (spi_rx_valid_i) begin
            // range needs to include instructions which require multiple bytes
            // and must be consecutive in the TitanComms enum
            if (!instruction_received & (spi_rx_byte_i >= WRITE & spi_rx_byte_i <= BIND_WRITE_ADDRESS)) begin
                // data_pointer <= 1;

                // TODO: fix this weird offset issue, lets try and get data_pointer = 0
                // set datapointer to appropriate value
                // STREAM sets data_pointer to 2 because we're immediately indexing
                if (spi_rx_byte_i == STREAM) begin
                    data_pointer <= 2'd0;
                end else begin
                    data_pointer <= 2'd1;
                end

                instruction_received <= 1'b1;
                current_instruction <= spi_rx_byte_i;
                received_byte_count <= 8'd1;

                case (spi_rx_byte_i)
                    WRITE: begin
                        expected_byte_count <= 8'd8;
                    end

                    READ: begin
                        expected_byte_count <= 8'd4;
                    end

                    BIND_INTERRUPT: begin
                        expected_byte_count <= 8'd4;
                    end

                    BIND_READ_ADDRESS: begin
                        expected_byte_count <= 8'd4;
                    end

                    BIND_WRITE_ADDRESS: begin
                        expected_byte_count <= 8'd4;
                    end

                    STREAM: begin
                        expected_byte_count <= 8'd5;
                        spi_tx_byte_o <= stream_i[31:24]; // upper most byte
                        // spi_tx_byte_o <= stream_i[31 - (8*data_pointer) -: 8];
                    end

                    default: begin
                        expected_byte_count = 8'hx;
                    end
                endcase

                
            // otherwise if the instruction is TRANSFER or REPEAT
            end else if (!instruction_received & (spi_rx_byte_i >= TRANSFER & spi_rx_byte_i <= REPEAT)) begin
                current_instruction <= spi_rx_byte_i;

                // reset datapointer if we need to send entire thing again
                if (spi_rx_byte_i == REPEAT) begin
                    data_pointer <= 2'd1;
                    
                end else if (spi_rx_byte_i == TRANSFER) begin
                    // https://stackoverflow.com/questions/18067571/indexing-vectors-and-arrays-with
                    // spi_tx_byte_o <= result_i[8 * data_pointer +: 8]; // sends LSB first
                    spi_tx_byte_o <= result_i[31 - (8 * data_pointer) -: 8]; // sends MSB first
                    data_pointer <= data_pointer + 2'd1;
                end

            end else if (instruction_received) begin
                received_byte_count <= received_byte_count + 8'd1;

                if (current_instruction == STREAM) begin
                    spi_tx_byte_o <= stream_i[23 - (8*data_pointer) -: 8];
                    data_pointer <= data_pointer + 2'd1;
                end
            end

                // shift any and all data into the register
                rebuilt_instruction <= {rebuilt_instruction[56:0], spi_rx_byte_i};

        // on the negative edge of spi_rx_valid_i
        end else if (~spi_rx_valid_i) begin
            // if instruction got and all bytes got then reset counters
            if (instruction_received & (received_byte_count == expected_byte_count)) begin
                instruction_received <= 0;
                received_byte_count <= 0;
            end else if (current_instruction == TRANSFER) begin
                // spi_tx_valid <= 0;
            end
        end
    end


    always @ (posedge got_all_data) begin

        if (current_instruction == WRITE) begin
            // instruction_o <= rebuilt_instruction[63:56];
            // address_o <= rebuilt_instruction[55:32];
            // value_o <= rebuilt_instruction[31:0];
            instruction_o <= byte7;
            address_o <= {byte6, byte5, byte4};
            value_o <= {byte3, byte2, byte1, byte0};

        end else if ((current_instruction >= READ) & (current_instruction <= BIND_WRITE_ADDRESS)) begin
            
            if (current_instruction == STREAM) begin
                // instruction_o <= rebuilt_instruction[39:32];
                // address_o <= 'h0;
                // value_o <= rebuilt_instruction[31:0];

                instruction_o <= byte4;
                value_o <= {byte3, byte2, byte1, byte0};

                address_o <= 'h0;

            end else begin
                // instruction_o <= rebuilt_instruction[32:24];
                // address_o <= rebuilt_instruction[23:0];
                // value_o <= 'h0;

                instruction_o <= byte3;
                address_o <= {byte2, byte1, byte0};

                value_o <= 0;
            end
        end else begin
            instruction_o <= 'h0;
            address_o <= 'h0;
            value_o <= 'h0;
        end

    end

endmodule