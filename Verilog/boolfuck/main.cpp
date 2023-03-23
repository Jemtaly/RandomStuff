#include <stdio.h>
#include "Vboolfuck.h"
#include "Windows.h"
#include "verilated.h"
#define mv(x, y) printf("\033[%d;%dH", (x) + 1, (y) + 1)
#define mvprintf(x, y, ...) mv(x, y), printf(__VA_ARGS__)
#define INSTRS "/~<>.,[]"
#define VALUES "01??????"
int main(int argc, char **argv, char **env) {
    HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE), hStdout = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwStdinMode, dwStdoutMode;
    if (!GetConsoleMode(hStdin, &dwStdinMode) ||
        !GetConsoleMode(hStdout, &dwStdoutMode) ||
        !SetConsoleMode(hStdin, dwStdinMode | ENABLE_WINDOW_INPUT) ||
        !SetConsoleMode(hStdout, dwStdoutMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING)) {
        fprintf(stderr, "error: unsupported stdin/stdout\n");
        return 1;
    }
    setvbuf(stdout, NULL, _IOFBF, 0x10000);
    printf("\033[?1049h\033[?25l");
    fflush(stdout);
    for (Vboolfuck vbfo; vbfo.eval(), GetKeyState(VK_ESCAPE) >= 0; Sleep(1), vbfo.clk = ~vbfo.clk) {
        static int w = 0, h = 0;
        CONSOLE_SCREEN_BUFFER_INFO csbi;
        GetConsoleScreenBufferInfo(hStdout, &csbi);
        if (w != csbi.dwSize.X || h != csbi.dwSize.Y) {
            w = csbi.dwSize.X;
            h = csbi.dwSize.Y;
            printf("\033[2J");
            printf("\033(0");
            mvprintf( 0,  0, "lqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqwwqqqqqqqqqqqqqk");
            mvprintf( 1,  0, "x                                  xx     x q   q x");
            mvprintf( 2,  0, "x                                  xx     x q   q x");
            mvprintf( 3,  0, "x                                  xx     x q   q x");
            mvprintf( 4,  0, "x                                  xx     x q   q x");
            mvprintf( 5,  0, "x                                  xx     x q   q x");
            mvprintf( 6,  0, "x                                  xx     x q   q x");
            mvprintf( 7,  0, "x                                  xx     x q   q x");
            mvprintf( 8,  0, "x                                  xx     x q   q x");
            mvprintf( 9,  0, "tqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqutqqqqqqqqqqqqqu");
            mvprintf(10,  0, "x                                  xx     x q   q x");
            mvprintf(11,  0, "x                                  xx     x q   q x");
            mvprintf(12,  0, "x                                  xx     x q   q x");
            mvprintf(13,  0, "x                                  xtqqqqqqqqqqqqqu");
            mvprintf(14,  0, "x                                  xx     x q   q x");
            mvprintf(15,  0, "x                                  xtqqqqqqqqqqqqqu");
            mvprintf(16,  0, "x                                  xx     x q   q x");
            mvprintf(17,  0, "x                                  xx     x q   q x");
            mvprintf(18,  0, "tqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqvvqqqqqqqqqqqqqu");
            mvprintf(19,  0, "x                                                 x");
            mvprintf(20,  0, "x                                                 x");
            mvprintf(21,  0, "x                                                 x");
            mvprintf(22,  0, "x                                                 x");
            mvprintf(23,  0, "mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj");
            printf("\033(B");
            mvprintf( 0, 15, " \033[1mCODE\033[22m ");
            mvprintf( 9, 15, " \033[1mDATA\033[22m ");
            mvprintf(18, 22, " \033[1mSTACK\033[22m ");
            mvprintf( 0, 40, " \033[1mSTATE\033[22m ");
            for (int i = 0; i < 8; i++)
                mvprintf(i +  1, 38, "(%c)", INSTRS[i]);
            mvprintf(10, 38, "LFT");
            mvprintf(11, 38, "RGT");
            mvprintf(12, 38, "CTL");
            mvprintf(14, 38, "CLK");
            mvprintf(16, 38, "WRB");
            mvprintf(17, 38, "RDB");
        }
        for (int i = 0; i < 8; i++) {
            mv(i +  1,  2);
            for (int j = 0; j < 32; j++)
                printf("%c", INSTRS[vbfo.prg[i * 32 + j]]);
        }
        for (int i = 0; i < 8; i++) {
            mv(i + 10,  2);
            for (int j = 0; j < 32; j++)
                printf("%c", VALUES[vbfo.mem[i * 32 + j]]);
        }
        for (int i = 0; i < 4; i++) {
            mv(i + 19,  2);
            for (int j = 0; j < 16; j++)
                printf("%02X ", vbfo.stk[i * 16 + j]);
        }
        mvprintf( 1 + vbfo.cur / 32, vbfo.cur % 32 + 2, "\033[4m%c\033[24m", INSTRS[vbfo.prg[vbfo.cur]]);
        mvprintf(10 + vbfo.ptr / 32, vbfo.ptr % 32 + 2, "\033[4m%c\033[24m", VALUES[vbfo.mem[vbfo.ptr]]);
        mvprintf(19 + vbfo.top / 16, vbfo.top % 16 * 3 + 2, "\033[4m%02X\033[24m", vbfo.stk[vbfo.top]);
        switch (vbfo.blk) {
        case 0b11: mvprintf( 1 + vbfo.cur / 32, vbfo.cur % 32 + 2, "\033[7m%c\033[27m", INSTRS[vbfo.prg[vbfo.cur]]); break;
        case 0b01: mvprintf(10 + vbfo.ptr / 32, vbfo.ptr % 32 + 2, "\033[7m%c\033[27m", VALUES[vbfo.mem[vbfo.ptr]]); break;
        case 0b10: mvprintf(10 + vbfo.ptr / 32, vbfo.ptr % 32 + 2, "\033[7m%c\033[27m", VALUES[7]); break; }
        for (int i = 0; i < 8; i++)
            mvprintf(i +  1, 46, "%d", vbfo.key >> i & 1);
        mvprintf(10, 46, "%d", vbfo.lft & 1);
        mvprintf(11, 46, "%d", vbfo.rgt & 1);
        mvprintf(12, 46, "%d", vbfo.ctl & 1);
        mvprintf(14, 46, "%d", vbfo.clk & 1);
        mvprintf(16, 46, "%d", vbfo.blk >> 0 & 1);
        mvprintf(17, 46, "%d", vbfo.blk >> 1 & 1);
        fflush(stdout);
        vbfo.lft = GetAsyncKeyState(VK_LEFT)  < 0;
        vbfo.rgt = GetAsyncKeyState(VK_RIGHT) < 0;
        vbfo.ctl = GetAsyncKeyState(VK_SPACE) < 0;
        auto rei = GetAsyncKeyState(VK_OEM_2) < 0;
        auto wav = GetAsyncKeyState(VK_OEM_3) < 0;
        auto lbr = GetAsyncKeyState(VK_OEM_4) < 0;
        auto rbr = GetAsyncKeyState(VK_OEM_6) < 0;
        auto alt = GetAsyncKeyState(VK_SHIFT) < 0;
        auto cma = GetAsyncKeyState(VK_OEM_COMMA)  < 0;
        auto prd = GetAsyncKeyState(VK_OEM_PERIOD) < 0;
        vbfo.key = rei << 0 | wav << 1 | cma << (alt ? 2 : 5) | prd << (alt ? 3 : 4) | lbr << 6 | rbr << 7;
    }
    printf("\033[?1049l\033[?25h");
    fflush(stdout);
    SetConsoleMode(hStdout, dwStdoutMode);
    SetConsoleMode(hStdin, dwStdinMode);
    FlushConsoleInputBuffer(hStdin);
    return 0;
}
