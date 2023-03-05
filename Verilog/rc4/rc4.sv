`timescale 1ns / 1ps
/* verilator lint_off WIDTH */
module RC4(
    input wire clk,
    input wire rst,
    input wire [7:0] in,
    output reg [7:0] out
  );
  reg  prompt, rec = 1;
  reg  [7:0] m [0:255];
  reg  [7:0] k [0:255];
  reg  [7:0] x, y, i, j, n;
  wire [7:0] X, Y, a, b, t;
  integer _;
  assign t = j + m[i] + k[i % n];
  assign X = x + 1;
  assign a = m[X];
  assign Y = y + a;
  assign b = m[Y];
  always @(posedge clk) begin
    if (rst) begin
      if (rec) begin
        for (_ = 0; _ < 256; _ = _ + 1) begin
          m[_] = _;
        end
        x <= 0;
        y <= 0;
        i <= 0;
        j <= 0;
        prompt <= 0;
        out <= 0;
        k[0] <= in;
        n <= 0 + 1;
      end else begin
        k[n] <= in;
        n <= n + 1;
      end
      rec <= 0;
    end else begin
      if (prompt) begin
        m[X] <= b;
        m[Y] <= a;
        out <= m[a + b] ^ in;
        x <= X;
        y <= Y;
      end else begin
        m[i] <= m[t];
        m[t] <= m[i];
        i <= i + 1;
        j <= t;
        if (i == 255) begin
          prompt <= 1;
        end
      end
      rec <= 1;
    end
  end
endmodule
