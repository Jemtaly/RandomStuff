`timescale 1ns / 1ps

module next_generation(
    input [7:0] rule,
    input [15:0] in,
    output [15:0] out
  );
  genvar i;
  generate
    for (i = 0; i < 16; i = i + 1) begin
      assign out[i] = rule[{in[(i + 1) % 16], in[i], in[(i + 15) % 16]}];
    end
  endgenerate
endmodule

module cellular_automata(
    input clk,
    input rst,
    input [7:0] rule,
    input [15:0] in,
    output reg [15:0] cur
  );
  integer count;
  wire [15:0] next;
  next_generation ng(rule, cur, next);
  always @(posedge clk or posedge rst)
    if (rst) begin
      count <= 0;
      cur <= in;
    end
    else if (&count[7:0]) begin
      count <= 0;
      cur <= next;
    end
    else
      count <= count + 1;
endmodule

module cellular_automata_tb;
  reg clk = 1, rst = 1;
  reg [7:0] rule = 30;
  reg [15:0] in = 1;
  wire [15:0] out;
  cellular_automata ca(clk, rst, rule, in, out);
  initial begin
    $dumpfile("wave.vcd");
    $dumpvars;
  end
  always #1 clk = ~clk;
  initial begin
    #1 rst = 1'b0;
    #65535 $finish;
  end
endmodule
