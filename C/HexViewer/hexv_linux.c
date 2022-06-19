#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "curses.h"
#define REC_OPN 1
#define REC_ERR 2
#define REC_BEG 4
#define REC_END 8
int main(int argc, char *argv[]) {
	if (!isatty(fileno(stdin)) || !isatty(fileno(stdout))) {
		fprintf(stderr, "error: unsupported stdin/stdout\n");
		return 1;
	}
	int rec = 0;
	ssize_t beg = 0;
	char *filename = NULL;
	for (int i = 1; (rec & REC_ERR) == 0 && i < argc; i++) {
		if (argv[i][0] == '-') {
			if (argv[i][1] == 'e' && argv[i][2] == '\0') {
				if ((rec & (REC_END | REC_BEG)) == 0) {
					rec |= REC_END;
				} else {
					rec |= REC_ERR;
				}
			} else if (argv[i][1] == 'b' && argv[i][2] == '\0') {
				if ((rec & (REC_END | REC_BEG)) == 0 && i + 1 < argc) {
					beg = atoll(argv[++i]);
					rec |= REC_BEG;
				} else {
					rec |= REC_ERR;
				}
			} else {
				rec |= REC_ERR;
			}
		} else if ((rec & REC_OPN) == 0) {
			filename = argv[i];
			rec |= REC_OPN;
		} else {
			rec |= REC_ERR;
		}
	}
	FILE *fp;
	if ((rec & REC_ERR) != 0 || (rec & REC_OPN) == 0 || (fp = fopen(filename, "rb")) == NULL) {
		fprintf(stderr, "usage: %s [-e] [-b N] FILENAME\n", argv[0]);
		return 1;
	}
	fseek(fp, 0, SEEK_END);
	ssize_t len = ftell(fp);
	if ((rec & REC_END) != 0) {
		beg = len;
	}
	initscr();
	noecho();
	curs_set(0);
	start_color();
	use_default_colors();
	init_pair(2, COLOR_RED, COLOR_WHITE);
	int w = (COLS - 10) / 4, h = LINES - 1;
DRAW:
	if (beg > len) {
		beg = len;
	} else if (beg < 0) {
		beg = 0;
	}
	attron(A_BOLD | A_REVERSE);
	mvprintw(0, 0, "          ");
	for (int j = 0; j < w; j++) {
		printw("%02X ", j & 0xff);
	}
	for (int j = 0; j < w; j++) {
		addch(' ');
	}
	attroff(A_BOLD | A_REVERSE);
	fseek(fp, beg, SEEK_SET);
	for (int i = 0; i < h; i++) {
		attron(A_BOLD);
		mvprintw(i + 1, 0, "%08X:", beg + i * w & 0xffffffff);
		attroff(A_BOLD);
		addch(' ');
		for (int j = 0; j < w; j++) {
			int c = fgetc(fp);
			switch (c) {
			case EOF:
				printw("   ");
				break;
			case 0:
				printw("00 ");
				break;
			default:
				attron(COLOR_PAIR(2));
				printw("%02X", c);
				attroff(COLOR_PAIR(2));
				addch(' ');
			}
		}
	}
	fseek(fp, beg, SEEK_SET);
	for (int i = 0; i < h; i++) {
		move(i + 1, w * 3 + 10);
		for (int j = 0; j < w; j++) {
			int c = fgetc(fp);
			addch(c == EOF ? ' ' : c < 32 || c >= 127 ? '.' : c);
		}
	}
READ:
	switch (getch()) {
	case KEY_RESIZE:
		w = (COLS - 10) / 4;
		h = LINES - 1;
		clear();
		goto DRAW;
	case 'w':
		beg -= w;
		goto DRAW;
	case 's':
		beg += w;
		goto DRAW;
	case 'a':
		beg--;
		goto DRAW;
	case 'd':
		beg++;
		goto DRAW;
	case ',':
		beg -= w * h;
		goto DRAW;
	case '.':
		beg += w * h;
		goto DRAW;
	case 'h':
		beg = 0;
		goto DRAW;
	case 'e':
		beg = len;
		goto DRAW;
	case 'q':
		goto QUIT;
	default:
		goto READ;
	}
QUIT:
	endwin();
	fclose(fp);
	return 0;
}
