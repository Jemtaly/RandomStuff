`include "cellular_automata.v"

module test;
  reg clk = 1, rst = 1;
  reg [7:0] rule = 30;
  reg [15:0] in = 1;
  wire [15:0] out;
  cellular_automata ca(clk, rst, rule, in, out);
  initial begin
    $dumpfile("wave.vcd");
    $dumpvars;
  end
  always
    #1 clk = ~clk;
  initial
    #1 rst = 1'b0;
  initial
    #65535 $finish;
endmodule
