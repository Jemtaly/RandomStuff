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
    input clk, rst,
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
    end else if (&count[7:0]) begin
      count <= 0;
      cur <= next;
    end else
      count <= count + 1;
endmodule
