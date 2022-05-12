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
  reg [7:0] mem [2 ** M - 1:0];
  reg [3:0] cde [2 ** N - 1:0];
  reg [M - 1:0] ptr;
  reg [N - 1:0] rec, count;
  reg [N - 3:0] pos;
  reg [1:0] process, block = 2'b11;
  reg l, r, e;
  wire continue;
  assign continue = enter & ~e;
  always @(posedge clock) begin
    if (stop)
      block = 2'b11;
    else if (start) begin
      ptr = 0;
      rec = -1;
      process = 0;
      block = 0;
    end
    else case (block)
      2'b00:
        if (process[1]) begin
          if (cde[rec][3:1] == 3'b011)
            count = process[0] ^ cde[rec][0] ? count - 1 : count + 1;
          if (count == 0)
            process = 0;
          else
            rec = process[0] ? rec - 1 : rec + 1;
        end
        else begin
          rec = rec + 1;
          out = 0;
          case (cde[rec])
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
              if (mem[ptr] == 0) begin
                process = 2'b10;
                count = 0;
              end
            4'b0111:
              if (mem[ptr] != 0) begin
                process = 2'b11;
                count = 0;
              end
            default:
              block = 2'b11;
          endcase
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
        pos = pos + (right & ~r & (pos != 2 ** N - 4)) - (left & ~l & (pos != 0));
        if (continue)
          {cde[{pos, 2'b00}], cde[{pos, 2'b01}], cde[{pos, 2'b10}], cde[{pos, 2'b11}]} = in;
        out = {cde[{pos, 2'b00}], cde[{pos, 2'b01}], cde[{pos, 2'b10}], cde[{pos, 2'b11}]};
      end
    endcase
    l <= left;
    r <= right;
    e <= enter;
  end
endmodule
