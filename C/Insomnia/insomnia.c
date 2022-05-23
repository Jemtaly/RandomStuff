#include <Windows.h>
#include <stdio.h>
#define REC_SYSTEM 1
#define REC_DISPLAY 2
#define REC_TIMEOUT 4
#define REC_ERROR 128
BOOL timeout(DWORD dwTime) {
	fprintf(stderr, "Waiting for %lu milliseconds, press Esc to continue, or press Enter to check the remaining time ...", dwTime);
	HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
	for (DWORD dwEnd = GetTickCount() + dwTime;;) {
		if (WaitForSingleObject(hStdin, dwEnd - GetTickCount()) != WAIT_OBJECT_0) {
			fprintf(stderr, "\n");
			return TRUE;
		}
		INPUT_RECORD irRead;
		DWORD dwRead;
		ReadConsoleInput(hStdin, &irRead, 1, &dwRead);
		if (irRead.EventType == KEY_EVENT && irRead.Event.KeyEvent.bKeyDown)
			switch (irRead.Event.KeyEvent.uChar.AsciiChar) {
			case 27:
				fprintf(stderr, "\n");
				return FALSE;
			case 13:
				fprintf(stderr, "\nWaiting for %lu milliseconds ...", dwEnd - GetTickCount());
			}
	}
}
void pause() {
	fprintf(stderr, "Press Esc to continue ...");
	HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
	for (;;) {
		INPUT_RECORD irRead;
		DWORD dwRead;
		ReadConsoleInput(hStdin, &irRead, 1, &dwRead);
		if (irRead.EventType == KEY_EVENT && irRead.Event.KeyEvent.bKeyDown)
			switch (irRead.Event.KeyEvent.uChar.AsciiChar) {
			case 27:
				fprintf(stderr, "\n");
				return;
			}
	}
}
int main(int argc, char *argv[]) {
	int rec = 0;
	long long t;
	for (int i = 1; i < argc; i++)
		if (argv[i][0] == '-')
			if (argv[i][1] == 't' && argv[i][2] == '\0')
				if ((rec & REC_TIMEOUT) == 0 && i + 1 < argc) {
					t = atoll(argv[++i]);
					rec |= REC_TIMEOUT;
				} else
					rec |= REC_ERROR;
			else if (argv[i][1] == 'd' && argv[i][2] == '\0')
				if ((rec & (REC_DISPLAY | REC_SYSTEM)) == 0)
					rec |= REC_DISPLAY;
				else
					rec |= REC_ERROR;
			else if (argv[i][1] == 's' && argv[i][2] == '\0')
				if ((rec & (REC_DISPLAY | REC_SYSTEM)) == 0)
					rec |= REC_SYSTEM;
				else
					rec |= REC_ERROR;
			else
				rec |= REC_ERROR;
		else
			rec |= REC_ERROR;
	if ((rec & REC_ERROR) != 0 || (rec & (REC_DISPLAY | REC_SYSTEM)) == 0) {
		fprintf(stderr, "usage: %s (-s | -d) [-t TIME]\n", argv[0]);
		return 1;
	}
	SetThreadExecutionState(ES_CONTINUOUS | (rec & REC_DISPLAY ? ES_DISPLAY_REQUIRED : 0) | (rec & REC_SYSTEM ? ES_SYSTEM_REQUIRED : 0));
	if ((rec & REC_TIMEOUT) == 0)
		pause();
	else
		timeout(t);
	SetThreadExecutionState(ES_CONTINUOUS);
}
