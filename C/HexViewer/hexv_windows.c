#include <Windows.h>
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
        !SetConsoleMode(hStdin, dwStdinMode | ENABLE_WINDOW_INPUT) ||
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
    setvbuf(stdout, NULL, _IOFBF, 0x10000);
    printf("\033[?1049h\033[?25l");
    fflush(stdout);
    SHORT w, h;
    goto _READ;
_DRAW:
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
        printf("\033[%dH\033[1m%08X: \033[22m", i + 2, beg + i * w & 0xffffffff);
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
                printf("\033[31;47m%02X\033[39;49m ", c);
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
_READ:
    INPUT_RECORD irRead;
    DWORD dwRead;
    ReadConsoleInput(hStdin, &irRead, 1, &dwRead);
    switch (irRead.EventType == WINDOW_BUFFER_SIZE_EVENT ? VK_F5 :
            irRead.EventType == KEY_EVENT && irRead.Event.KeyEvent.bKeyDown ? irRead.Event.KeyEvent.wVirtualKeyCode : 0) {
    case VK_F5:
        w = (irRead.Event.WindowBufferSizeEvent.dwSize.X - 10) / 4;
        h = (irRead.Event.WindowBufferSizeEvent.dwSize.Y + -1) / 1;
        printf("\033[2J");
        goto _DRAW;
    case VK_UP:
        beg -= w;
        goto _DRAW;
    case VK_DOWN:
        beg += w;
        goto _DRAW;
    case VK_LEFT:
        beg--;
        goto _DRAW;
    case VK_RIGHT:
        beg++;
        goto _DRAW;
    case VK_PRIOR:
        beg -= w * h;
        goto _DRAW;
    case VK_NEXT:
        beg += w * h;
        goto _DRAW;
    case VK_HOME:
        beg = 0;
        goto _DRAW;
    case VK_END:
        beg = len;
        goto _DRAW;
    case VK_ESCAPE:
        goto _QUIT;
    default:
        goto _READ;
    }
_QUIT:
    printf("\033[?1049l\033[?25h");
    fflush(stdout);
    fclose(fp);
    SetConsoleMode(hStdin, dwStdinMode);
    SetConsoleMode(hStdout, dwStdoutMode);
    return 0;
}
