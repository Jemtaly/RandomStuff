#include <stdio.h>
#include "Vhexadecimal_decoder.h"
#include "Windows.h"
#include "verilated.h"
#define mv(x, y) printf("\033[%d;%dH", (x) + 1, (y) + 1)
#define mvprintf(x, y, format, ...) printf("\033[%d;%dH" format, (x) + 1, (y) + 1 __VA_OPT__(,) __VA_ARGS__)
#define MASK_A  2 //  1
#define MASK_D  6 //  3
#define MASK_W 18 //  9
#define MASK_S 54 // 27
constexpr char ctable[81][4] = {
    " ", "╴", "╸", "╶", "─", "╾", "╺", "╼", "━",
    "╵", "┘", "┙", "└", "┴", "┵", "┕", "┶", "┷",
    "╹", "┚", "┛", "┖", "┸", "┹", "┗", "┺", "┻",
    "╷", "┐", "┑", "┌", "┬", "┭", "┍", "┮", "┯",
    "│", "┤", "┥", "├", "┼", "┽", "┝", "┾", "┿",
    "╿", "┦", "┩", "┞", "╀", "╃", "┡", "╄", "╇",
    "╻", "┒", "┓", "┎", "┰", "┱", "┏", "┲", "┳",
    "╽", "┧", "┪", "┟", "╁", "╅", "┢", "╆", "╈",
    "┃", "┨", "┫", "┠", "╂", "╉", "┣", "╊", "╋",
};
int main(int argc, char **argv, char **env) {
    HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE), hStdout = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwStdinModeOld, dwStdoutModeOld, dwStdinModeNew, dwStdoutModeNew;
    if (!GetConsoleMode(hStdin, &dwStdinModeOld) || !GetConsoleMode(hStdout, &dwStdoutModeOld)) {
        fprintf(stderr, "Error: unsupported stdin/stdout\n");
        return 1;
    }
    dwStdinModeNew = dwStdinModeOld | ENABLE_WINDOW_INPUT;
    dwStdoutModeNew = dwStdoutModeOld | ENABLE_VIRTUAL_TERMINAL_PROCESSING;
    if (!SetConsoleMode(hStdin, dwStdinModeNew) || !SetConsoleMode(hStdout, dwStdoutModeNew) || !SetConsoleOutputCP(CP_UTF8)) {
        SetConsoleMode(hStdin, dwStdinModeOld);
        SetConsoleMode(hStdout, dwStdoutModeOld);
        fprintf(stderr, "Error: unsupported stdin/stdout\n");
        return 1;
    }
    setvbuf(stdout, NULL, _IOFBF, 0x10000);
    printf("\033[?1049h\033[?25l");
    fflush(stdout);
    for (Vhexadecimal_decoder vhd; vhd.eval(), GetKeyState(VK_ESCAPE) >= 0; Sleep(1), vhd.clk = ~vhd.clk) {
        static int w = 0, h = 0;
        CONSOLE_SCREEN_BUFFER_INFO csbi;
        GetConsoleScreenBufferInfo(hStdout, &csbi);
        if (w != csbi.dwSize.X || h != csbi.dwSize.Y) {
            w = csbi.dwSize.X;
            h = csbi.dwSize.Y;
            printf("\033[2J");
            printf("\033(0");
            mvprintf( 0,  0, "lqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqk");
            mvprintf( 1,  0, "x                                                 x");
            mvprintf( 2,  0, "x                                                 x");
            mvprintf( 3,  0, "x                                                 x");
            mvprintf( 4,  0, "x                                                 x");
            mvprintf( 5,  0, "x                                                 x");
            mvprintf( 6,  0, "mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj");
            printf("\033(B");
            mvprintf( 0, 21, " \033[1mLED7SEG\033[22m ");
        }
        static int lum[8][8] = {};
        for (int i = 0; i < 8; i++) {
            for (int j = 0; j < 8; j++) {
                if ((vhd.id >> i & 1) == 0 && (vhd.out >> j & 1) == 0) {
                    lum[i][j] = 15;
                } else if (lum[i][j] > 0) {
                    lum[i][j] -= 1;
                }
            }
        }
        for (int i = 0; i < 8; i++) {
            int pos[5][3] = {};
            if (lum[i][7] > 0) { pos[0][0] += MASK_D, pos[0][1] += MASK_A + MASK_D, pos[0][2] += MASK_A; } // A SEGMENT
            if (lum[i][6] > 0) { pos[0][2] += MASK_S, pos[1][2] += MASK_W + MASK_S, pos[2][2] += MASK_W; } // B SEGMENT
            if (lum[i][5] > 0) { pos[2][2] += MASK_S, pos[3][2] += MASK_W + MASK_S, pos[4][2] += MASK_W; } // C SEGMENT
            if (lum[i][4] > 0) { pos[4][0] += MASK_D, pos[4][1] += MASK_A + MASK_D, pos[4][2] += MASK_A; } // D SEGMENT
            if (lum[i][3] > 0) { pos[2][0] += MASK_S, pos[3][0] += MASK_W + MASK_S, pos[4][0] += MASK_W; } // E SEGMENT
            if (lum[i][2] > 0) { pos[0][0] += MASK_S, pos[1][0] += MASK_W + MASK_S, pos[2][0] += MASK_W; } // F SEGMENT
            if (lum[i][1] > 0) { pos[2][0] += MASK_D, pos[2][1] += MASK_A + MASK_D, pos[2][2] += MASK_A; } // G SEGMENT
            for (int j = 0; j < 5; j++) {
                mv(j +  1, 44 - i * 6),
                printf(ctable[pos[j][0]]),
                printf(ctable[pos[j][1]]),
                printf(ctable[pos[j][1]]),
                printf(ctable[pos[j][1]]),
                printf(ctable[pos[j][2]]);
            }
            printf(lum[i][0] ? "·" : " ");
        }
        fflush(stdout);
        vhd.in += 1;
    }
    printf("\033[?1049l\033[?25h");
    fflush(stdout);
    SetConsoleMode(hStdout, dwStdoutModeOld);
    SetConsoleMode(hStdin, dwStdinModeOld);
    return 0;
}
