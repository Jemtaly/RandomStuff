`timescale 1ns / 1ps

module adder(
    input a,
    input b,
    input cin,
    output cout,
    output s
  );
  assign s = a ^ b ^ cin;
  assign cout = a & cin | b & cin | a & b;
endmodule

module adder_8(
    input [7:0] a,
    input [7:0] b,
    input cin,
    output cout,
    output [7:0] sum
  );
  wire [7:0] c;
  adder a0(a[0],  b[0],  cin, c[0], sum[0]);
  adder a1(a[1],  b[1], c[0], c[1], sum[1]);
  adder a2(a[2],  b[2], c[1], c[2], sum[2]);
  adder a3(a[3],  b[3], c[2], c[3], sum[3]);
  adder a4(a[4],  b[4], c[3], c[4], sum[4]);
  adder a5(a[5],  b[5], c[4], c[5], sum[5]);
  adder a6(a[6],  b[6], c[5], c[6], sum[6]);
  adder a7(a[7],  b[7], c[6], c[7], sum[7]);
  assign cout =  c[7];
endmodule

module subtractor_8(
    input [7:0] a,
    input [7:0] b,
    input cin,
    output cout,
    output [7:0] dif
  );
  wire [7:0] c;
  adder a0(a[0], ~b[0], ~cin, c[0], dif[0]);
  adder a1(a[1], ~b[1], c[0], c[1], dif[1]);
  adder a2(a[2], ~b[2], c[1], c[2], dif[2]);
  adder a3(a[3], ~b[3], c[2], c[3], dif[3]);
  adder a4(a[4], ~b[4], c[3], c[4], dif[4]);
  adder a5(a[5], ~b[5], c[4], c[5], dif[5]);
  adder a6(a[6], ~b[6], c[5], c[6], dif[6]);
  adder a7(a[7], ~b[7], c[6], c[7], dif[7]);
  assign cout = ~c[7];
endmodule

module multiplier_8(
    input [7:0] a,
    input [7:0] b,
    input [7:0] cin,
    output [7:0] cout,
    output [7:0] prod
  );
  wire [7:0] s [0:7];
  adder_8 add_o0(     8'b0, b & {8{a[0]}}, cin[0], s[0][7], {s[0][6:0], prod[0]});
  adder_8 add_o1(s[0][7:0], b & {8{a[1]}}, cin[1], s[1][7], {s[1][6:0], prod[1]});
  adder_8 add_o2(s[1][7:0], b & {8{a[2]}}, cin[2], s[2][7], {s[2][6:0], prod[2]});
  adder_8 add_o3(s[2][7:0], b & {8{a[3]}}, cin[3], s[3][7], {s[3][6:0], prod[3]});
  adder_8 add_o4(s[3][7:0], b & {8{a[4]}}, cin[4], s[4][7], {s[4][6:0], prod[4]});
  adder_8 add_o5(s[4][7:0], b & {8{a[5]}}, cin[5], s[5][7], {s[5][6:0], prod[5]});
  adder_8 add_o6(s[5][7:0], b & {8{a[6]}}, cin[6], s[6][7], {s[6][6:0], prod[6]});
  adder_8 add_o7(s[6][7:0], b & {8{a[7]}}, cin[7], s[7][7], {s[7][6:0], prod[7]});
  assign cout = +s[7][7:0];
endmodule

module divider_8(
    input [7:0] num,
    input [7:0] den,
    output [7:0] quo,
    output [7:0] rem
  );
  wire [7:0] res [0:7];
  wire [7:0] raw [0:7];
  assign raw[7] = {                          num[7]};
  assign raw[6] = {quo[7] ? res[7] : raw[7], num[6]};
  assign raw[5] = {quo[6] ? res[6] : raw[6], num[5]};
  assign raw[4] = {quo[5] ? res[5] : raw[5], num[4]};
  assign raw[3] = {quo[4] ? res[4] : raw[4], num[3]};
  assign raw[2] = {quo[3] ? res[3] : raw[3], num[2]};
  assign raw[1] = {quo[2] ? res[2] : raw[2], num[1]};
  assign raw[0] = {quo[1] ? res[1] : raw[1], num[0]};
  adder_8 add_o7(raw[7], ~den, 1'b1, quo[7], res[7]);
  adder_8 add_o6(raw[6], ~den, 1'b1, quo[6], res[6]);
  adder_8 add_o5(raw[5], ~den, 1'b1, quo[5], res[5]);
  adder_8 add_o4(raw[4], ~den, 1'b1, quo[4], res[4]);
  adder_8 add_o3(raw[3], ~den, 1'b1, quo[3], res[3]);
  adder_8 add_o2(raw[2], ~den, 1'b1, quo[2], res[2]);
  adder_8 add_o1(raw[1], ~den, 1'b1, quo[1], res[1]);
  adder_8 add_o0(raw[0], ~den, 1'b1, quo[0], res[0]);
  assign rem = quo[0] ? res[0] : raw[0];
endmodule
