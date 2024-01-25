`include "calculator.v"

module testbench;
  reg [7:0] a = 0;
  reg [7:0] b = 0;
  reg [7:0] cin = 0;
  wire [7:0] prod;
  wire [7:0] cout;
  wire [7:0] quo;
  wire [7:0] rem;
  multiplier_8 m8(a, b, cin, cout, prod);
  divider_8 d8(a, b, quo, rem);
  always begin
    #1;
    a = $random;
    b = $random;
    cin = $random;
  end
  initial begin
    $dumpfile("wave.vcd");
    $dumpvars;
    #1024 $finish;
  end
endmodule
