`timescale 1ns/1ps
`default_nettype none

module tb_uart_harness(
    input wire rx
);

initial 
    begin
        $dumpfile("sim.vcd");
        $dumpvars(0,tb_uart_harness);
        #1;
    end
endmodule