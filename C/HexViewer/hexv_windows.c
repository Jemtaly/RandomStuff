#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
#define REC_ERR 1
#define REC_OPN 2
#define REC_BEG 4
#define REC_END 8
int main(int argc, char *argv[]) {
    HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE), hStdout = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwStdinModeOld, dwStdoutModeOld, dwStdinModeNew, dwStdoutModeNew;
    if (!GetConsoleMode(hStdin, &dwStdinModeOld) || !GetConsoleMode(hStdout, &dwStdoutModeOld)) {
        fprintf(stderr, "Error: unsupported stdin/stdout\n");
        return 1;
    }
    dwStdinModeNew = dwStdinModeOld | ENABLE_WINDOW_INPUT;
    dwStdoutModeNew = dwStdoutModeOld | ENABLE_VIRTUAL_TERMINAL_PROCESSING;
    if (!SetConsoleMode(hStdin, dwStdinModeNew) || !SetConsoleMode(hStdout, dwStdoutModeNew)) {
        SetConsoleMode(hStdin, dwStdinModeOld);
        SetConsoleMode(hStdout, dwStdoutModeOld);
        fprintf(stderr, "Error: unsupported stdin/stdout\n");
        return 1;
    }
    DWORD rec = 0;
    SSIZE_T beg, end;
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
    if ((rec & REC_ERR) != 0 || (rec & REC_OPN) == 0 || fopen_s(&fp, filename, "rb")) {
        SetConsoleMode(hStdin, dwStdinModeOld);
        SetConsoleMode(hStdout, dwStdoutModeOld);
        fprintf(stderr, "Description: Terminal-based Hex Viewer\n");
        fprintf(stderr, "Usage: %s [-e N | -b N] FILENAME\n", argv[0]);
        fprintf(stderr, "Options:\n");
        fprintf(stderr, "  -e N  start at the Nth byte from the end of the file\n");
        fprintf(stderr, "  -b N  start at the Nth byte from the beginning of the file\n");
        return 1;
    }
    fseek(fp, 0, SEEK_END);
    SSIZE_T len = ftell(fp), itr;
    if ((rec & (REC_BEG | REC_END)) == 0) {
        itr = 0;
    } else if ((rec & REC_END) != 0) {
        itr = len - end;
    } else if ((rec & REC_BEG) != 0) {
        itr = beg;
    }
    setvbuf(stdout, NULL, _IOFBF, 0x10000);
    printf("\033[?1049h\033[?25l");
    fflush(stdout);
    SHORT w, h;
    goto _READ;
_DRAW:
    if (itr > len) {
        itr = len;
    } else if (itr < 0) {
        itr = 0;
    }
    printf("\033[%d;%dH", 1, 1);
    printf("\033[01;07m");
    printf("        ");
    for (SHORT j = 0; j < w; j++) {
        putchar(' ');
        printf("%02X", j & 0xff);
    }
    putchar(' ');
    for (SHORT j = 0; j < w; j++) {
        putchar(' ');
    }
    printf("\033[22;27m");
    fseek(fp, itr, SEEK_SET);
    for (SHORT i = 0; i < h; i++) {
        printf("\033[%d;%dH", i + 2, 1);
        printf("\033[01m");
        printf("%08X", itr + i * w & 0xffffffff);
        printf("\033[22m");
        for (SHORT j = 0; j < w; j++) {
            putchar(' ');
            int c = fgetc(fp);
            switch (c) {
            case EOF:
                printf("  ");
                break;
            case 0:
                printf("00");
                break;
            default:
                printf("\033[31;49m");
                printf("%02X", c);
                printf("\033[39;49m");
            }
        }
    }
    fseek(fp, itr, SEEK_SET);
    for (SHORT i = 0; i < h; i++) {
        printf("\033[%d;%dH", i + 2, w * 3 + 10);
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
        w = (irRead.Event.WindowBufferSizeEvent.dwSize.X - 9) / 4;
        h = (irRead.Event.WindowBufferSizeEvent.dwSize.Y - 1) / 1;
        printf("\033[2J");
        goto _DRAW;
    case VK_UP:
        itr -= w;
        goto _DRAW;
    case VK_DOWN:
        itr += w;
        goto _DRAW;
    case VK_LEFT:
        itr--;
        goto _DRAW;
    case VK_RIGHT:
        itr++;
        goto _DRAW;
    case VK_PRIOR:
        itr -= w * h;
        goto _DRAW;
    case VK_NEXT:
        itr += w * h;
        goto _DRAW;
    case VK_HOME:
        itr = 0;
        goto _DRAW;
    case VK_END:
        itr = len;
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
    SetConsoleMode(hStdin, dwStdinModeOld);
    SetConsoleMode(hStdout, dwStdoutModeOld);
    return 0;
}
