#include <Windows.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#define REC_ERR 1
#define REC_OPN 2
#define REC_BEG 4
#define REC_END 8
int main(int argc, char *argv[]) {
	HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE), hStdout = GetStdHandle(STD_OUTPUT_HANDLE);
	DWORD dwStdinMode, dwStdoutMode;
	if (!GetConsoleMode(hStdin, &dwStdinMode) ||
		!GetConsoleMode(hStdout, &dwStdoutMode) ||
		!SetConsoleMode(hStdout, dwStdoutMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING)) {
		fprintf(stderr, "error: unsupported stdin/stdout\n");
		return 1;
	}
	DWORD rec = 0;
	SSIZE_T beg = 0;
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
	if ((rec & REC_ERR) != 0 || (rec & REC_OPN) == 0 || fopen_s(&fp, filename, "rb")) {
		fprintf(stderr, "usage: %s [-e] [-b N] FILENAME\n", argv[0]);
		return 1;
	}
	fseek(fp, 0, SEEK_END);
	SSIZE_T len = ftell(fp);
	if ((rec & REC_END) != 0) {
		beg = len;
	}
	setvbuf(stdout, NULL, _IOFBF, 0x10000);	 // stream will be fully buffered.
	printf("\033[?1049h\033[?25l");
	fflush(stdout);
	SHORT w, h;
	goto LREAD;
LDRAW:
	if (beg > len) {
		beg = len;
	} else if (beg < 0) {
		beg = 0;
	}
	printf("\033[H\033[1;7m          ");
	for (SHORT j = 0; j < w; j++) {
		printf("%02X ", j & 0xff);
	}
	for (SHORT j = 0; j < w; j++) {
		putchar(' ');
	}
	printf("\033[22;27m");
	fseek(fp, beg, SEEK_SET);
	for (SHORT i = 0; i < h; i++) {
		printf("\033[%dH\033[1m%08X:\033[22m ", i + 2, beg + i * w & 0xffffffff);
		for (SHORT j = 0; j < w; j++) {
			int c = fgetc(fp);
			switch (c) {
			case EOF:
				printf("   ");
				break;
			case 0:
				printf("00 ");
				break;
			default:
				printf("\033[47;31m%02X\033[0m ", c);
			}
		}
	}
	fseek(fp, beg, SEEK_SET);
	for (SHORT i = 0; i < h; i++) {
		printf("\033[%d;%dH", i + 2, w * 3 + 11);
		for (SHORT j = 0; j < w; j++) {
			int c = fgetc(fp);
			putchar(c == EOF ? ' ' : isprint(c) ? c : '.');
		}
	}
	fflush(stdout);
LREAD:
	INPUT_RECORD irRead;
	DWORD dwRead;
	ReadConsoleInput(hStdin, &irRead, 1, &dwRead);
	switch (irRead.EventType == WINDOW_BUFFER_SIZE_EVENT ? 0xffff :
			irRead.EventType == KEY_EVENT && irRead.Event.KeyEvent.bKeyDown ? irRead.Event.KeyEvent.wVirtualScanCode : 0x0000) {
	case 0xffff:
		w = (irRead.Event.WindowBufferSizeEvent.dwSize.X - 10) / 4;
		h = (irRead.Event.WindowBufferSizeEvent.dwSize.Y + -1) / 1;
		printf("\033[2J");
		goto LDRAW;
	case 0x0048:
		beg -= w;
		goto LDRAW;
	case 0x0050:
		beg += w;
		goto LDRAW;
	case 0x004b:
		beg--;
		goto LDRAW;
	case 0x004d:
		beg++;
		goto LDRAW;
	case 0x0049:
		beg -= w * h;
		goto LDRAW;
	case 0x0051:
		beg += w * h;
		goto LDRAW;
	case 0x0047:
		beg = 0;
		goto LDRAW;
	case 0x004f:
		beg = len;
		goto LDRAW;
	case 0x0001:
		goto LQUIT;
	default:
		goto LREAD;
	}
LQUIT:
	printf("\033[?1049l\033[?25h");
	fflush(stdout);
	fclose(fp);
	SetConsoleMode(hStdout, dwStdoutMode);
	return 0;
}
