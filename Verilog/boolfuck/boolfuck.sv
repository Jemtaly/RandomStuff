`timescale 1ns / 1ps
/* verilator lint_off BLKSEQ */
/* verilator lint_off CASEINCOMPLETE */
/* verilator lint_off WIDTH */
module boolfuck
  #(
    parameter C = 8,  M = 8, S = 6
  )(
    input wire clk, lft, rgt, ctl,
    input wire [8 - 1 : 0] key,
    output reg [3 - 1 : 0] prg [2 ** C - 1 : 0],
    output reg [1 - 1 : 0] mem [2 ** M - 1 : 0],
    output reg [C - 1 : 0] stk [2 ** S - 1 : 0], cur, nxt,
    output reg [M - 1 : 0] ptr,
    output reg [S - 1 : 0] top, ctr,
    output reg [2 - 1 : 0] blk = 2'b11
  );
  reg  lftd, rgtd, ctld;
  wire lftp, rgtp, ctlp;
  reg  [8 - 1 : 0] keyd;
  wire [8 - 1 : 0] keyp;
  assign lftp = lft & ~lftd;
  assign rgtp = rgt & ~rgtd;
  assign ctlp = ctl & ~ctld;
  assign keyp = key & ~keyd;
  always @(posedge clk)
  begin
    if (ctlp)
      if (blk == 2'b11)
      begin
        nxt = 0;
        ptr = 0;
        top = 0;
        ctr = 0;
        blk = 2'b00;
      end
      else
        blk = 2'b11;
    else
      case (blk)
      2'b00:
      begin
        nxt = cur + 1;
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
        if (keyp)
          blk = 2'b00;
      2'b10:
        if (keyp)
        begin
          mem[ptr] = ~keyp[0];
          blk = 2'b00;
        end
      2'b11:
        case (keyp)
        8'b00000001: begin prg[cur] = 3'b000; cur = cur + 1; end
        8'b00000010: begin prg[cur] = 3'b001; cur = cur + 1; end
        8'b00000100: begin prg[cur] = 3'b010; cur = cur + 1; end
        8'b00001000: begin prg[cur] = 3'b011; cur = cur + 1; end
        8'b00010000: begin prg[cur] = 3'b100; cur = cur + 1; end
        8'b00100000: begin prg[cur] = 3'b101; cur = cur + 1; end
        8'b01000000: begin prg[cur] = 3'b110; cur = cur + 1; end
        8'b10000000: begin prg[cur] = 3'b111; cur = cur + 1; end
        default:     cur = cur + (rgtp ? 1 : 0) - (lftp ? 1 : 0);
        endcase
      endcase
    if (blk == 2'b00)
      cur = nxt;
    lftd <= lft;
    rgtd <= rgt;
    ctld <= ctl;
    keyd <= key;
  end
endmodule
