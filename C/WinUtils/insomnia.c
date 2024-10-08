#include <Windows.h>
#include <stdio.h>

#define REC_TIMEOUT 1
#define REC_COMMAND 2
#define REC_DISPLAY 8
#define REC_ERROR 128

int timeout(LONGLONG llPeriod) {
    fprintf(stderr, "Waiting for %lld milliseconds, press Esc to continue, or press Enter to check the remaining time ...", llPeriod);
    HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
    for (ULONGLONG ullEnd = GetTickCount64() + llPeriod;;) {
        if (WaitForSingleObject(hStdin, max(0, llPeriod)) != WAIT_OBJECT_0) {
            fprintf(stderr, "\n");
            return 0;
        }
        llPeriod = ullEnd - GetTickCount64();
        INPUT_RECORD irRead;
        DWORD dwRead;
        ReadConsoleInput(hStdin, &irRead, 1, &dwRead);
        if (irRead.EventType == KEY_EVENT && irRead.Event.KeyEvent.bKeyDown) {
            switch (irRead.Event.KeyEvent.uChar.AsciiChar) {
            case 13:
                fprintf(stderr, "\nWaiting for %lld milliseconds ...", llPeriod);
                break;
            case 27:
                fprintf(stderr, "\n");
                return 0;
            }
        }
    }
}

int pause() {
    fprintf(stderr, "Press Esc to continue ...");
    HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
    for (;;) {
        INPUT_RECORD irRead;
        DWORD dwRead;
        ReadConsoleInput(hStdin, &irRead, 1, &dwRead);
        if (irRead.EventType == KEY_EVENT && irRead.Event.KeyEvent.bKeyDown) {
            switch (irRead.Event.KeyEvent.uChar.AsciiChar) {
            case 27:
                fprintf(stderr, "\n");
                return 0;
            }
        }
    }
}

int main(int argc, char *argv[]) {
    int rec = 0;
    long long t;
    char *c;
    for (int i = 1; i < argc; i++) {
        if (argv[i][0] != '-') {
            rec |= REC_ERROR;
        } else if (argv[i][1] == 'c' && argv[i][2] == '\0') {
            if ((rec & (REC_COMMAND | REC_TIMEOUT)) == 0 && i + 1 < argc) {
                c = argv[++i];
                rec |= REC_COMMAND;
            } else {
                rec |= REC_ERROR;
            }
        } else if (argv[i][1] == 't' && argv[i][2] == '\0') {
            if ((rec & (REC_COMMAND | REC_TIMEOUT)) == 0 && i + 1 < argc) {
                t = atoll(argv[++i]);
                rec |= REC_TIMEOUT;
            } else {
                rec |= REC_ERROR;
            }
        } else if (argv[i][1] == 'd' && argv[i][2] == '\0') {
            if ((rec & REC_DISPLAY) == 0) {
                rec |= REC_DISPLAY;
            } else {
                rec |= REC_ERROR;
            }
        } else {
            rec |= REC_ERROR;
        }
    }
    if ((rec & REC_ERROR) != 0) {
        fprintf(stderr, "Description: Prevent the PC from sleeping.\n");
        fprintf(stderr, "Usage: %s [-d] [-t <ms> | -c <cmd>]\n", argv[0]);
        fprintf(stderr, "Options:\n");
        fprintf(stderr, "  -d        prevent the display from sleeping as well\n");
        fprintf(stderr, "  -t <ms>   wait for <ms> milliseconds\n");
        fprintf(stderr, "  -c <cmd>  execute <cmd> and wait for it to finish\n");
        return 1;
    }
    SetThreadExecutionState(ES_CONTINUOUS | (rec & REC_DISPLAY ? ES_DISPLAY_REQUIRED : ES_SYSTEM_REQUIRED));
    if ((rec & (REC_COMMAND | REC_TIMEOUT)) == 0) {
        return pause();
    } else if ((rec & REC_COMMAND) != 0) {
        return system(c);
    } else if ((rec & REC_TIMEOUT) != 0) {
        return timeout(t);
    }
}
