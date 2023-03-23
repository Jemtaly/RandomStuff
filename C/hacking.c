#include <Windows.h>
#include <stdio.h>
typedef union PTRUN {
    UCHAR *pb;
    void **pp;
    DWORD (*f)(DWORD);
} PTRUN;
int main(void) {
    DWORD rec = 0;
    PTRUN buff = {
        .pb = VirtualAlloc(0, 0x100, MEM_COMMIT, PAGE_EXECUTE_READWRITE),
    };
    if (buff.pb == NULL) {
        fputs("Could not aquire memory.\n", stderr);
        return 1;
    }
    PTRUN iter = buff;
#ifndef _WIN64
    *iter.pb++ = 0x8b;
    *iter.pb++ = 0x4c;
    *iter.pb++ = 0x24;
    *iter.pb++ = 0x04; // mov ecx, dword [esp + 4]
#endif
    *iter.pb++ = 0x89;
    *iter.pb++ = 0xc8; // mov eax, ecx
#ifndef _WIN64
    printf("Architecture: x86\n");
    *iter.pb++ = 0x2b;
    *iter.pb++ = 0x05;
    *iter.pp++ = &rec; // sub eax, dword [rec]
    *iter.pb++ = 0x89;
    *iter.pb++ = 0x0d;
    *iter.pp++ = &rec; // mov dword [rec], ecx
#else
    printf("Architecture: x64\n");
    *iter.pb++ = 0x48;
    *iter.pb++ = 0xba;
    *iter.pp++ = &rec; // movabs rdx, rec (64)
    *iter.pb++ = 0x2b;
    *iter.pb++ = 0x02; // sub eax, dword [rdx]
    *iter.pb++ = 0x89;
    *iter.pb++ = 0x0a; // mov dword [rdx], ecx
#endif
    *iter.pb++ = 0xc3; // ret
    for (int tmp; printf("-----------------\nArg: "), scanf("%d", &tmp), printf("Ret: %d\n", buff.f(tmp)), tmp;) {}
    VirtualFree(buff.pb, 0x100, MEM_RELEASE);
    return 0;
}
