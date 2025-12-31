#include <Windows.h>

#ifdef DEBUG
#include <stdio.h>
#define PDEBUG(...) fprintf(stderr, __VA_ARGS__)
#else
#define PDEBUG(...)
#endif

int main() {
    BOOL b1_rec = FALSE;
    BOOL b2_rec = FALSE;
    BOOL b3_rec = FALSE;
    RegisterHotKey(NULL, 1, MOD_ALT, VK_F1);
    RegisterHotKey(NULL, 2, MOD_ALT, VK_F2);
    RegisterHotKey(NULL, 3, MOD_ALT, VK_F3);
    MSG msg = {0};
    for (;;) {
        if (b1_rec || b2_rec || b3_rec) {
            // using GetAsyncKeyState when at least one button is pressed to avoid missing release events
            BOOL menu = GetAsyncKeyState(VK_MENU) < 0;
            BOOL b1_cur = menu && GetAsyncKeyState(VK_F1) < 0;
            BOOL b2_cur = menu && GetAsyncKeyState(VK_F2) < 0;
            BOOL b3_cur = menu && GetAsyncKeyState(VK_F3) < 0;
            if (!b1_rec) {
                if (b1_cur) {
                    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
                    b1_rec = TRUE;
                    PDEBUG("Pressed %s (GetAsyncKeyState)\n", "L");
                }
            } else {
                if (!b1_cur) {
                    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
                    b1_rec = FALSE;
                    PDEBUG("Released %s (GetAsyncKeyState)\n", "L");
                }
            }
            if (!b2_rec) {
                if (b2_cur) {
                    mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0);
                    b2_rec = TRUE;
                    PDEBUG("Pressed %s (GetAsyncKeyState)\n", "M");
                }
            } else {
                if (!b2_cur) {
                    mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0);
                    b2_rec = FALSE;
                    PDEBUG("Released %s (GetAsyncKeyState)\n", "M");
                }
            }
            if (!b3_rec) {
                if (b3_cur) {
                    mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0);
                    b3_rec = TRUE;
                    PDEBUG("Pressed %s (GetAsyncKeyState)\n", "R");
                }
            } else {
                if (!b3_cur) {
                    mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0);
                    b3_rec = FALSE;
                    PDEBUG("Released %s (GetAsyncKeyState)\n", "R");
                }
            }
        } else {
            // empty the message queue accumulated while the buttons were pressed
            while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE) != 0) {
                TranslateMessage(&msg);
                DispatchMessage(&msg);
            }
            // using GetMessage when no button is pressed to avoid busy waiting
            if (GetMessage(&msg, NULL, 0, 0) != 0 && msg.message == WM_HOTKEY) {
                if (msg.wParam == 1) {
                    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
                    b1_rec = TRUE;
                    PDEBUG("Pressed %s (GetMessage)\n", "L");
                }
                if (msg.wParam == 2) {
                    mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0);
                    b2_rec = TRUE;
                    PDEBUG("Pressed %s (GetMessage)\n", "M");
                }
                if (msg.wParam == 3) {
                    mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0);
                    b3_rec = TRUE;
                    PDEBUG("Pressed %s (GetMessage)\n", "R");
                }
            }
        }
    }
    return 0;
}
