#include <Windows.h>
int main() {
    BOOL pressed_z = FALSE;
    BOOL pressed_x = FALSE;
    for (;;) {
        BOOL CTRL = GetAsyncKeyState(VK_CONTROL) < 0;
        BOOL MENU = GetAsyncKeyState(VK_MENU) < 0;
        BOOL KEYZ = GetAsyncKeyState('Z') < 0;
        BOOL KEYX = GetAsyncKeyState('X') < 0;
        BOOL pressing_z = CTRL && MENU && KEYZ;
        BOOL pressing_x = CTRL && MENU && KEYX;
        if (!pressed_z && pressing_z) {
            mouse_event(MOUSEEVENTF_MIDDLEDOWN, 0, 0, 0, 0);
            pressed_z = TRUE;
        } else if (pressed_z && !pressing_z) {
            mouse_event(MOUSEEVENTF_MIDDLEUP, 0, 0, 0, 0);
            pressed_z = FALSE;
        }
        if (!pressed_x && pressing_x) {
            mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0);
            pressed_x = TRUE;
        } else if (pressed_x && !pressing_x) {
            mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0);
            pressed_x = FALSE;
        }
    }
    return 0;
}
