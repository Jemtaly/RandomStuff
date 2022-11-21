`timescale 1ns / 1ps
/* verilator lint_off BLKSEQ */
/* verilator lint_off CASEINCOMPLETE */
/* verilator lint_off WIDTH */
/* verilator lint_off CASEX */
parameter C = 8;
parameter M = 8;
parameter S = 5;
module boolfuck(
    input clk,
    input lft,
    input rgt,
    input swi,
    input [8 - 1 : 0] key,
    output reg [3 - 1 : 0] prg [2 ** C - 1 : 0],
    output reg [1 - 1 : 0] mem [2 ** M - 1 : 0],
    output reg [C - 1 : 0] stk [2 ** S - 0 : 0],
    output reg [C - 1 : 0] cur,
    output reg [C - 1 : 0] nxt,
    output reg [M - 1 : 0] ptr,
    output reg [S - 1 : 0] top,
    output reg [S - 1 : 0] ctr,
    output reg [2 - 1 : 0] blk = 2'b11
  );
  reg  dlft, drgt, dswi;
  wire plft, prgt, nswi;
  reg  [8 - 1 : 0] dkey;
  wire [8 - 1 : 0] pkey;
  assign plft = lft & ~dlft;
  assign prgt = rgt & ~drgt;
  assign nswi = ~swi | dswi;
  assign pkey = key & ~dkey;
  always @(posedge clk)
  begin
    if (nswi)
      case (blk)
      2'b00:
      begin
        cur = nxt;
        nxt = nxt + 1;
        if (ctr)
          case (prg[cur])
          3'b110: ctr = ctr + 1;
          3'b111: ctr = ctr - 1;
          endcase
        else
          case (prg[cur])
          3'b000: blk = 2'b11;
          3'b001: mem[ptr] = ~mem[ptr];
          3'b010: ptr = ptr - 1;
          3'b011: ptr = ptr + 1;
          3'b100: blk = 2'b01;
          3'b101: blk = 2'b10;
          3'b110:
            if (mem[ptr])
            begin
              stk[top] = cur;
              top = top + 1;
            end
            else
              ctr = 1;
          3'b111:
            begin
              top = top - 1;
              nxt = stk[top];
            end
          endcase
      end
      2'b01:
        if (pkey)
          blk = 2'b00;
      2'b10:
      begin
        mem[ptr] = key != 8'b00000001;
        if (pkey)
          blk = 2'b00;
      end
      2'b11:
      begin
        case (key)
        8'b00000001: prg[cur] = 3'b000;
        8'b00000010: prg[cur] = 3'b001;
        8'b00000100: prg[cur] = 3'b010;
        8'b00001000: prg[cur] = 3'b011;
        8'b00010000: prg[cur] = 3'b100;
        8'b00100000: prg[cur] = 3'b101;
        8'b01000000: prg[cur] = 3'b110;
        8'b10000000: prg[cur] = 3'b111;
        endcase
        cur = cur + prgt - plft + |pkey;
      end
      endcase
    else if (blk == 2'b11)
    begin
      nxt = 0;
      ptr = 0;
      top = 0;
      ctr = 0;
      blk = 2'b00;
    end
    else
      blk = 2'b11;
    dlft <= lft;
    drgt <= rgt;
    dswi <= swi;
    dkey <= key;
  end
endmodule
