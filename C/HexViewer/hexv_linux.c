#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "curses.h"
#define REC_ERR 1
#define REC_OPN 2
#define REC_BEG 4
#define REC_END 8
int main(int argc, char *argv[]) {
    if (!isatty(fileno(stdin)) || !isatty(fileno(stdout))) {
        fprintf(stderr, "Error: unsupported stdin/stdout\n");
        return 1;
    }
    int rec = 0;
    ssize_t beg, end;
    char *filename;
    for (int i = 1; (rec & REC_ERR) == 0 && i < argc; i++) {
        if (argv[i][0] != '-') {
            if ((rec & REC_OPN) == 0) {
                filename = argv[i];
                rec |= REC_OPN;
            } else {
                rec |= REC_ERR;
            }
        } else if (argv[i][1] == 'e' && argv[i][2] == '\0') {
            if ((rec & (REC_BEG | REC_END)) == 0 && i + 1 < argc && (end = atoll(argv[++i])) >= 0) {
                rec |= REC_END;
            } else {
                rec |= REC_ERR;
            }
        } else if (argv[i][1] == 'b' && argv[i][2] == '\0') {
            if ((rec & (REC_BEG | REC_END)) == 0 && i + 1 < argc && (beg = atoll(argv[++i])) >= 0) {
                rec |= REC_BEG;
            } else {
                rec |= REC_ERR;
            }
        } else {
            rec |= REC_ERR;
        }
    }
    FILE *fp;
    if ((rec & REC_ERR) != 0 || (rec & REC_OPN) == 0 || (fp = fopen(filename, "rb")) == NULL) {
        fprintf(stderr, "Description: Terminal-based Hex Viewer\n");
        fprintf(stderr, "Usage: %s [-e N | -b N] FILENAME\n", argv[0]);
        fprintf(stderr, "Options:\n");
        fprintf(stderr, "  -e N  start at the Nth byte from the end of the file\n");
        fprintf(stderr, "  -b N  start at the Nth byte from the beginning of the file\n");
        return 1;
    }
    fseek(fp, 0, SEEK_END);
    ssize_t len = ftell(fp), itr;
    if ((rec & (REC_BEG | REC_END)) == 0) {
        itr = 0;
    } else if ((rec & REC_END) != 0) {
        itr = len - end;
    } else if ((rec & REC_BEG) != 0) {
        itr = beg;
    }
    initscr();
    curs_set(0);
    noecho();
    start_color();
    use_default_colors();
    init_pair(2, COLOR_RED, -1);
    int w, h;
_INIT:
    w = (COLS  - 9) / 4;
    h = (LINES - 1) / 1;
    clear();
_DRAW:
    if (itr > len) {
        itr = len;
    } else if (itr < 0) {
        itr = 0;
    }
    move(0, 0);
    attron(A_BOLD | A_REVERSE);
    printw("         ");
    for (int j = 0; j < w; j++) {
        addch(' ');
        printw("%02X", j & 0xff);
    }
    addch(' ');
    for (int j = 0; j < w; j++) {
        addch(' ');
    }
    attroff(A_BOLD | A_REVERSE);
    fseek(fp, itr, SEEK_SET);
    for (int i = 0; i < h; i++) {
        move(i + 1, 0);
        attron(A_BOLD);
        printw("%08X", itr + i * w & 0xffffffff);
        attroff(A_BOLD);
        for (int j = 0; j < w; j++) {
            addch(' ');
            int c = fgetc(fp);
            switch (c) {
            case EOF:
                printw("  ");
                break;
            case 0:
                printw("00");
                break;
            default:
                attron(COLOR_PAIR(2));
                printw("%02X", c);
                attroff(COLOR_PAIR(2));
            }
        }
    }
    fseek(fp, itr, SEEK_SET);
    for (int i = 0; i < h; i++) {
        move(i + 1, w * 3 + 10);
        for (int j = 0; j < w; j++) {
            int c = fgetc(fp);
            addch(c == EOF ? ' ' : isprint(c) ? c : '.');
        }
    }
_READ:
    switch (getch()) {
    case KEY_RESIZE:
    case 'r':
        goto _INIT;
    case 'w':
        itr -= w;
        goto _DRAW;
    case 's':
        itr += w;
        goto _DRAW;
    case 'a':
        itr--;
        goto _DRAW;
    case 'd':
        itr++;
        goto _DRAW;
    case ',':
        itr -= w * h;
        goto _DRAW;
    case '.':
        itr += w * h;
        goto _DRAW;
    case 'h':
        itr = 0;
        goto _DRAW;
    case 'e':
        itr = len;
        goto _DRAW;
    case 'q':
        goto _QUIT;
    default:
        goto _READ;
    }
_QUIT:
    endwin();
    fclose(fp);
    return 0;
}
