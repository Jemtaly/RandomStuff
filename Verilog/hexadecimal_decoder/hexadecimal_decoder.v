`timescale 1ns / 1ps

/* verilator lint_off WIDTH */

module hexadecimal_decoder(
    input clk,
    input [7:0] blank,
    input [31:0] in,
    output [7:0] id,
    output [7:0] out
  );
  reg [2:0] i = 0;
  wire [3:0] cur;
  wire [7:0] hex [0:15];
  assign hex[4'h0] = 8'b0000_0011;
  assign hex[4'h1] = 8'b1001_1111;
  assign hex[4'h2] = 8'b0010_0101;
  assign hex[4'h3] = 8'b0000_1101;
  assign hex[4'h4] = 8'b1001_1001;
  assign hex[4'h5] = 8'b0100_1001;
  assign hex[4'h6] = 8'b0100_0001;
  assign hex[4'h7] = 8'b0001_1111;
  assign hex[4'h8] = 8'b0000_0001;
  assign hex[4'h9] = 8'b0000_1001;
  assign hex[4'ha] = 8'b0001_0001;
  assign hex[4'hb] = 8'b1100_0001;
  assign hex[4'hc] = 8'b0110_0011;
  assign hex[4'hd] = 8'b1000_0101;
  assign hex[4'he] = 8'b0110_0001;
  assign hex[4'hf] = 8'b0111_0001;
  assign id = ~(1 << i) | blank;
  assign cur = in >> {i, 2'b00};
  assign out = hex[cur];
  always @(posedge clk) i <= i + 1;
endmodule
