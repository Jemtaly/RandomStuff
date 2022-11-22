#include <stdio.h>
#include "Vboolfuck.h"
#include "Windows.h"
#include "verilated.h"
#define INSTRS "/~<>.,[]"
#define VALUES "01??????"
#define mv(x, y) printf("\033[%d;%dH", (x) + 1, (y) + 1)
#define mvprintf(x, y, ...) mv(x, y), printf(__VA_ARGS__)
#define UNDERLN "\004\030"
#define REVERSE "\007\033"
#define attron(x) printf("\033[%dm", x[0])
#define attrno(x) printf("\033[%dm", x[1])
int main(int argc, char **argv, char **env) {
	HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
    HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);
	DWORD dwStdinMode, dwStdoutMode;
	if (!GetConsoleMode(hStdin, &dwStdinMode) ||
		!GetConsoleMode(hStdout, &dwStdoutMode) ||
        !SetConsoleMode(hStdin, dwStdinMode & ~(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT)) ||
        !SetConsoleMode(hStdout, dwStdoutMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING)) {
		fprintf(stderr, "error: unsupported stdin/stdout\n");
		return 1;
	}
	printf("\033[?1049h\033[?25l\033(0");
	for (Vboolfuck vbfo; GetKeyState(VK_ESCAPE) >= 0; Sleep(1), vbfo.clk = !vbfo.clk, vbfo.eval()) {
        CONSOLE_SCREEN_BUFFER_INFO csbi;
        GetConsoleScreenBufferInfo(GetStdHandle(STD_OUTPUT_HANDLE), &csbi);
        if (static int w = 0, h = 0; w != csbi.dwSize.X || h != csbi.dwSize.Y) {
            w = csbi.dwSize.X;
            h = csbi.dwSize.Y;
            printf("\033[2J");
        }
		mvprintf( 0,  0, "lqqqqqqqqqqqq PROGRAM qqqqqqqqqqqqqwwqqq INPUT qqqk");
		for (int i = 0; i < 8; i++) {
			mvprintf(i +  1,  0, "x ");
			for (int j = 0; j < 32; j++)
				printf("%c", INSTRS[vbfo.prg[i * 32 + j]]);
            printf(" xx             x");
		}
		mvprintf( 9,  0, "tqqqqqqqqqq DATA MEMORY qqqqqqqqqqqux             x");
		for (int i = 0; i < 8; i++) {
			mvprintf(i + 10,  0, "x ");
			for (int j = 0; j < 32; j++)
				printf("%c", VALUES[vbfo.mem[i * 32 + j]]);
            printf(" xx             x");
		}
		mvprintf(18,  0, "tqqqqqqqqqqqqqqqqqqqqqq STACK qqqqqvvqqqqqqqqqqqqqu");
		for (int i = 0; i < 4; i++) {
            mvprintf(i + 19,  0, "x ");
			for (int j = 0; j < 16; j++)
				printf("%02X ", vbfo.stk[i * 11 + j]);
            printf("x");
		}
        mvprintf(23,  0, "mqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqj");
		for (int i = 0; i < 8; i++)
			mvprintf(i +  1, 36, "x (%c) x q %d q x", INSTRS[i], vbfo.key >> i & 1);
        mvprintf( 9, 36, "tqqqqqqqqqqqqqu");
		mvprintf(10, 36, "x LFT x q %d q x", vbfo.lft & 1);
		mvprintf(11, 36, "x RGT x q %d q x", vbfo.rgt & 1);
		mvprintf(12, 36, "x CTR x q %d q x", vbfo.ctl & 1);
        mvprintf(13, 36, "tqqqqqqqqqqqqqu");
		mvprintf(14, 36, "x CLK x q %d q x", vbfo.clk & 1);
        mvprintf(15, 36, "tqqqqqqqqqqqqqu");
        mvprintf(17, 36, "x WRB x q %d q x", vbfo.blk % 2);
        mvprintf(16, 36, "x RDB x q %d q x", vbfo.blk / 2);
		attron(UNDERLN);
		mvprintf( 1 + vbfo.cur / 32, vbfo.cur % 32 + 2, "%c", INSTRS[vbfo.prg[vbfo.cur]]);
		mvprintf(10 + vbfo.ptr / 32, vbfo.ptr % 32 + 2, "%c", VALUES[vbfo.mem[vbfo.ptr]]);
		mvprintf(19 + vbfo.top / 11, vbfo.top % 11 * 3 + 2, "%02X", vbfo.stk[vbfo.top]);
		attrno(UNDERLN);
		attron(REVERSE);
		switch (vbfo.blk) {
		case 0b11: mvprintf( 1 + vbfo.cur / 32, vbfo.cur % 32 + 2, "%c", INSTRS[vbfo.prg[vbfo.cur]]); break;
		case 0b01: mvprintf(10 + vbfo.ptr / 32, vbfo.ptr % 32 + 2, "%c", VALUES[vbfo.mem[vbfo.ptr]]); break;
		case 0b10: mvprintf(10 + vbfo.ptr / 32, vbfo.ptr % 32 + 2, "%c", VALUES[7]); break;
        }
		attrno(REVERSE);
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
	printf("\033[?1049l\033[?25h\033(B");
	fflush(stdout);
	SetConsoleMode(hStdout, dwStdoutMode);
	SetConsoleMode(hStdin, dwStdinMode);
	return 0;
}
