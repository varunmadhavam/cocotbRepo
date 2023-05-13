`timescale 1ns/1ps
`default_nettype none

module tb_vga_harness(
    input wire hsync,
    input wire vsync,
    input wire[7:0] r,
    input wire[7:0] g,
    input wire[7:0] b
);

initial 
    begin
        $dumpfile("sim.vcd");
        $dumpvars(0,tb_vga_harness);
        #1;
    end
endmodule