module param_mux # (
    parameter INPUT_WIDTH = 32,
    parameter SELECTOR_WIDTH,
    parameter SIGNAL_COUNT
) (
    input wire [SELECTOR_WIDTH-1:0] selector,
    input wire [INPUT_WIDTH-1:0] inputs [0:SIGNAL_COUNT-1],
    output logic [INPUT_WIDTH-1:0] out
);

    always @ (*) begin
        out = inputs[selector];
    end

endmodule