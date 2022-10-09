#include <Windows.h>
#include <stdio.h>
#define REC_TIMEOUT 1
#define REC_COMMAND 2
#define REC_DISPLAY 8
#define REC_ERROR 128
BOOL timeout(ULONGLONG ullPeriod) {
	fprintf(stderr, "Waiting for %llu milliseconds, press Esc to continue, or press Enter to check the remaining time ...", ullPeriod);
	HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
	for (ULONGLONG ullBegin = GetTickCount64(), ullEnd = ullBegin + ullPeriod;;) {
		if (WaitForSingleObject(hStdin, ullEnd - GetTickCount64()) != WAIT_OBJECT_0) {
			fprintf(stderr, "\n");
			return TRUE;
		}
		INPUT_RECORD irRead;
		DWORD dwRead;
		ReadConsoleInput(hStdin, &irRead, 1, &dwRead);
		if (irRead.EventType == KEY_EVENT && irRead.Event.KeyEvent.bKeyDown) {
			switch (irRead.Event.KeyEvent.uChar.AsciiChar) {
			case 13:
				fprintf(stderr, "\nWaiting for %llu milliseconds ...", ullEnd - GetTickCount64());
				break;
			case 27:
				fprintf(stderr, "\n");
				return FALSE;
			}
		}
	}
}
BOOL pause() {
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
				return FALSE;
			}
		}
	}
}
int main(int argc, char *argv[]) {
	int rec = 0, ret = 0;
	unsigned long long t;
	char *cmd = NULL;
	for (int i = 1; i < argc; i++) {
		if (argv[i][0] == '-') {
			if (argv[i][1] == 'd' && argv[i][2] == '\0') {
				if ((rec & REC_DISPLAY) == 0) {
					rec |= REC_DISPLAY;
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
			} else {
				rec |= REC_ERROR;
			}
		} else if ((rec & (REC_COMMAND | REC_TIMEOUT)) == 0) {
			cmd = malloc(strlen(argv[i]) + 1);
			strcpy(cmd, argv[i]);
			while (++i < argc) {
				cmd = realloc(cmd, strlen(cmd) + strlen(argv[i]) + 2);
				strcat(cmd, " ");
				strcat(cmd, argv[i]);
			}
			rec |= REC_COMMAND;
		} else {
			rec |= REC_ERROR;
		}
	}
	if ((rec & REC_ERROR) != 0) {
		fprintf(stderr, "usage: %s [-d] [-t <milliseconds> | <command>]\n", argv[0]);
		return 1;
	}
	SetThreadExecutionState(ES_CONTINUOUS | (rec & REC_DISPLAY ? ES_DISPLAY_REQUIRED : ES_SYSTEM_REQUIRED));
	if ((rec & REC_COMMAND) != 0) {
		ret = system(cmd);
		free(cmd);
	} else if ((rec & REC_TIMEOUT) != 0) {
		timeout(t);
	} else {
		pause();
	}
	// SetThreadExecutionState(ES_CONTINUOUS);
	return ret;
}
