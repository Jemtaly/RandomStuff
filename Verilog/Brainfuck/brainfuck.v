`timescale 1ns / 1ps

module brainfuck(
    input clock,
    input enter,
    input start,
    input stop,
    input left,
    input right,
    input [15:0] in,
    output reg [15:0] out
  );
  parameter M = 8;
  parameter N = 8;
  parameter S = 8;
  reg [8 - 1:0] mem [2 ** M - 1:0];
  reg [4 - 1:0] cde [2 ** N - 1:0];
  reg [N - 1:0] sta [2 ** S - 1:0];
  reg [M - 1:0] ptr;
  reg [N - 1:0] pos;
  reg [S - 1:0] top, count;
  reg [2 - 1:0] block = 2'b11;
  reg [N - 3:0] slide;
  reg l, r, e;
  wire continue;
  assign continue = enter & ~e;
  always @(posedge clock) begin
    if (stop)
      block = 2'b11;
    else if (start) begin
      ptr = 0;
      pos = 0;
      top = 0;
      count = 0;
      block = 0;
    end
    else case (block)
      2'b00: begin
        if (count)
          case (cde[pos])
            4'b0110:
              count = count + 1;
            4'b0111:
              count = count - 1;
          endcase
        else begin
          out = 0;
          case (cde[pos])
            4'b0000:
              ptr = ptr + 1;
            4'b0001:
              ptr = ptr - 1;
            4'b0010:
              mem[ptr] = mem[ptr] + 1;
            4'b0011:
              mem[ptr] = mem[ptr] - 1;
            4'b0100:
              block[0] = 1;
            4'b0101:
              block[1] = 1;
            4'b0110:
              if (mem[ptr]) begin
                sta[top] = pos;
                top = top + 1;
              end
              else
                count = 1;
            4'b0111:
              if (mem[ptr]) begin
                top = top - 1;
                pos = sta[top];
              end
            default:
              block = 2'b11;
          endcase
        end
        pos = pos + 1;
      end
      2'b01: begin
        out = mem[ptr];
        if (continue)
          block = 0;
      end
      2'b10: begin
        mem[ptr] = in;
        if (continue)
          block = 0;
      end
      2'b11: begin
        slide = slide + (right & ~r & (slide != 2 ** N - 4)) - (left & ~l & (slide != 0));
        if (continue)
          {cde[{slide, 2'b00}], cde[{slide, 2'b01}], cde[{slide, 2'b10}], cde[{slide, 2'b11}]} = in;
        out = {cde[{slide, 2'b00}], cde[{slide, 2'b01}], cde[{slide, 2'b10}], cde[{slide, 2'b11}]};
      end
    endcase
    l <= left;
    r <= right;
    e <= enter;
  end
endmodule
