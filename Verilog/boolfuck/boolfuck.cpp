#include "Vboolfuck.h"
#include "verilated.h"
#include "curses.h"
#include <iostream>
#define INSTRS "/~<>.,[]"
#define VALUES "01?"
int main(int argc, char** argv, char** env) {
	if (!isatty(fileno(stdin)) || !isatty(fileno(stdout))) {
		std::cerr << "error: unsupported stdin/stdout" << std::endl;
		return 1;
	}
    Verilated::commandArgs(argc, argv);
    Vboolfuck* top = new Vboolfuck;
	auto win = initscr();
    nodelay(win, true);
    noecho();
    curs_set(0);
    while (true) {
        mvprintw( 0, 0, "----------- PROGRAM ------------");
        for (int i = 0; i < 8; i++) {
            move(i +  1, 0);
            for (int j = 0; j < 32; j++)
                printw("%c", INSTRS[top->prg[i * 32 + j]]);
        }
        mvprintw( 9, 0, "--------- DATA MEMORY ----------");
        for (int i = 0; i < 8; i++) {
            move(i + 10, 0);
            for (int j = 0; j < 32; j++)
                printw("%c", VALUES[top->mem[i * 32 + j]]);
        }
        mvprintw(18, 0, "----------- STACK --------------");
        for (int i = 0; i < 3; i++) {
            move(i + 19, 0);
            for (int j = 0; j < 11; j++)
                printw("%02X ",    (top->stk[i * 11 + j]));
        }
        attron (A_UNDERLINE);
        mvprintw( 1 + top->cur / 32, top->cur % 32, "%c", INSTRS[top->prg[top->cur]]);
        mvprintw(10 + top->ptr / 32, top->ptr % 32, "%c", VALUES[top->mem[top->ptr]]);
        mvprintw(19 + top->top / 11, top->top % 11 * 3, "%02X", (top->stk[top->top]));
        attroff(A_UNDERLINE);
        attron (A_REVERSE);
        switch (top->blk) {
        case 0b11: mvprintw( 1 + top->cur / 32, top->cur % 32, "%c", INSTRS[top->prg[top->cur]]); break;
        case 0b01: mvprintw(10 + top->ptr / 32, top->ptr % 32, "%c", VALUES[top->mem[top->ptr]]); break;
        case 0b10: mvprintw(10 + top->ptr / 32, top->ptr % 32, "%c", VALUES[0x0000000000000002]); break;
        }
        attroff(A_REVERSE);
        auto c = getch();
        top->key = c == INSTRS[0] ? 0b00000001 :
                   c == INSTRS[1] ? 0b00000010 :
                   c == INSTRS[2] ? 0b00000100 :
                   c == INSTRS[3] ? 0b00001000 :
                   c == INSTRS[4] ? 0b00010000 :
                   c == INSTRS[5] ? 0b00100000 :
                   c == INSTRS[6] ? 0b01000000 :
                   c == INSTRS[7] ? 0b10000000 : 0;
        top->lft = c == 'a';
        top->rgt = c == 'd';
        top->swi = c == ' ';
        if (c == 'q') break;
        top->clk = 0; top->eval();
        top->clk = 1; top->eval();
    }
    endwin();
    delete top;
    return 0;
}
