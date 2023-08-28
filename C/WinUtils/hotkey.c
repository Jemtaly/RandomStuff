#include <Windows.h>
#include <stdio.h>
#define PDEBUG(...) // printf(__VA_ARGS__)
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
            BOOL menu = GetAsyncKeyState(VK_MENU) < 0;
            BOOL b1_cur = menu && GetAsyncKeyState(VK_F1) < 0;
            BOOL b2_cur = menu && GetAsyncKeyState(VK_F2) < 0;
            BOOL b3_cur = menu && GetAsyncKeyState(VK_F3) < 0;
            if (!b1_rec) {
                if (b1_cur) {
                    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
                    b1_rec = TRUE;
                    PDEBUG("Pressed L (GetAsyncKeyState)\n");
                }
            } else {
                if (!b1_cur) {
                    mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
                    b1_rec = FALSE;
                    PDEBUG("Released L (GetAsyncKeyState)\n");
                }
            }
            if (!b2_rec) {
                if (b2_cur) {
                    mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0);
                    b2_rec = TRUE;
                    PDEBUG("Pressed M (GetAsyncKeyState)\n");
                }
            } else {
                if (!b2_cur) {
                    mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0);
                    b2_rec = FALSE;
                    PDEBUG("Released M (GetAsyncKeyState)\n");
                }
            }
            if (!b3_rec) {
                if (b3_cur) {
                    mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0);
                    b3_rec = TRUE;
                    PDEBUG("Pressed R (GetAsyncKeyState)\n");
                }
            } else {
                if (!b3_cur) {
                    mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0);
                    b3_rec = FALSE;
                    PDEBUG("Released R (GetAsyncKeyState)\n");
                }
            }
        } else {
            while (PeekMessage(&msg, NULL, 0, 0, PM_REMOVE) != 0) {
                TranslateMessage(&msg);
                DispatchMessage(&msg);
            }
            if (GetMessage(&msg, NULL, 0, 0) != 0 && msg.message == WM_HOTKEY) {
                switch (msg.wParam) {
                case 1:
                    mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
                    b1_rec = TRUE;
                    PDEBUG("Pressed L (WM_HOTKEY)\n");
                    break;
                case 2:
                    mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0);
                    b2_rec = TRUE;
                    PDEBUG("Pressed M (WM_HOTKEY)\n");
                    break;
                case 3:
                    mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0);
                    b3_rec = TRUE;
                    PDEBUG("Pressed R (WM_HOTKEY)\n");
                    break;
                }
            }
        }
    }
    return 0;
}
