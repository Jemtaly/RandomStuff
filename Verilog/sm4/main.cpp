#include <iostream>
#include "Vsm4.h"
#include "verilated.h"
void setk(Vsm4 &vsm4, uint8_t *key, bool mode) {
    vsm4.mode = mode;          // 模式
    for (int i = 0; i < 16; i++)
        vsm4.key[i] = key[i];  // 密钥
}
void test(Vsm4 &vsm4, uint8_t *buf) {
    for (int i = 0; i < 16; i++)
        vsm4.src[i] = buf[i];  // 输入
    vsm4.eval();               // 仿真
    for (int i = 0; i < 16; i++)
        buf[i] = vsm4.dst[i];  // 输出
}
void dump(const char *name, uint8_t *data) {
    printf("%s:", name);
    for (size_t i = 0; i < 16; i++)
        printf(" %02x", data[i]);
    printf("\n");
}
int main(int argc, char **argv, char **env) {
    // Example:
    // k: 01 23 45 67 89 ab cd ef fe dc ba 98 76 54 32 10
    // p: 01 23 45 67 89 ab cd ef fe dc ba 98 76 54 32 10
    // c: 68 1e df 34 d2 06 96 5e 86 b3 e9 4f 53 6e 42 46
    uint8_t key[] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef, 0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10};
    uint8_t buf[] = {0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef, 0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10};
    Vsm4 vsm4;
    dump("Key", key);
    dump("Msg", buf);
    setk(vsm4, key, 1);
    test(vsm4, buf);
    dump("Enc", buf);
    setk(vsm4, key, 0);
    test(vsm4, buf);
    dump("Dec", buf);
    return 0;
}
