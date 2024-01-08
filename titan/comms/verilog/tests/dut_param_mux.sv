module dut_param_mux (
    input wire [31:0] in1, in2, in3, in4,
    input wire [1:0] sel_i,
    output wire [31:0] mux_o
);

    `ifdef COCOTB_SIM
        initial begin
            $dumpfile ("waves_dut_param_mux.vcd");
            // https://stackoverflow.com/questions/37368155/what-does-unable-to-bind-wire-error-mean
            $dumpvars (0, uut_pmux);
            #1;
        end
    `endif

    param_mux # (
        .INPUT_WIDTH(32), .SELECTOR_WIDTH(2), .SIGNAL_COUNT(4)
    ) uut_pmux (
        .selector(sel_i), .inputs('{in1, in2, in3, in4}), .out(mux_o)
    );

endmodule