#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <immintrin.h>
#include <zmmintrin.h>
void show(char const *name, __m256i mmc) {
    uint8_t *u8c = (uint8_t *)&mmc;
    printf("%s:\n", name);
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 8; j++) {
            printf("0x%02x ", u8c[i * 8 + j]);
        }
        printf("\n");
    }
}
static const __m256i rev = _mm256_set_epi8(
    0x1c, 0x1d, 0x1e, 0x1f,
    0x18, 0x19, 0x1a, 0x1b,
    0x14, 0x15, 0x16, 0x17,
    0x10, 0x11, 0x12, 0x13,
    0x0c, 0x0d, 0x0e, 0x0f,
    0x08, 0x09, 0x0a, 0x0b,
    0x04, 0x05, 0x06, 0x07,
    0x00, 0x01, 0x02, 0x03); // Reverse Byte Order
void test(uint32_t const *src, uint32_t *dst) {
    __m256i ss0 = _mm256_loadu_si256((__m256i *)src + 0); // 0x00 0x01 0x02 0x03 0x04 0x05 0x06 0x07
    __m256i ss1 = _mm256_loadu_si256((__m256i *)src + 1); // 0x08 0x09 0x0a 0x0b 0x0c 0x0d 0x0e 0x0f
    __m256i ss2 = _mm256_loadu_si256((__m256i *)src + 2); // 0x10 0x11 0x12 0x13 0x14 0x15 0x16 0x17
    __m256i ss3 = _mm256_loadu_si256((__m256i *)src + 3); // 0x18 0x19 0x1a 0x1b 0x1c 0x1d 0x1e 0x1f
    __m256i tt0 = _mm256_unpacklo_epi32(ss0, ss1);        // 0x00 0x08 0x01 0x09 0x04 0x0c 0x05 0x0d
    __m256i tt1 = _mm256_unpackhi_epi32(ss0, ss1);        // 0x02 0x0a 0x03 0x0b 0x06 0x0e 0x07 0x0f
    __m256i tt2 = _mm256_unpacklo_epi32(ss2, ss3);        // 0x10 0x18 0x11 0x19 0x14 0x1c 0x15 0x1d
    __m256i tt3 = _mm256_unpackhi_epi32(ss2, ss3);        // 0x12 0x1a 0x13 0x1b 0x16 0x1e 0x17 0x1f
    __m256i mm0 = _mm256_unpacklo_epi64(tt0, tt2);        // 0x00 0x08 0x10 0x18 0x04 0x0c 0x14 0x1c
    __m256i mm1 = _mm256_unpackhi_epi64(tt0, tt2);        // 0x01 0x09 0x11 0x19 0x05 0x0d 0x15 0x1d
    __m256i mm2 = _mm256_unpacklo_epi64(tt1, tt3);        // 0x02 0x0a 0x12 0x1a 0x06 0x0e 0x16 0x1e
    __m256i mm3 = _mm256_unpackhi_epi64(tt1, tt3);        // 0x03 0x0b 0x13 0x1b 0x07 0x0f 0x17 0x1f
    // ...
    __m256i cc0 = _mm256_unpacklo_epi32(mm0, mm1);        // 0x00 0x01 0x08 0x09 0x04 0x05 0x0c 0x0d
    __m256i cc1 = _mm256_unpackhi_epi32(mm0, mm1);        // 0x10 0x11 0x18 0x19 0x14 0x15 0x1c 0x1d
    __m256i cc2 = _mm256_unpacklo_epi32(mm2, mm3);        // 0x02 0x03 0x0a 0x0b 0x06 0x07 0x0e 0x0f
    __m256i cc3 = _mm256_unpackhi_epi32(mm2, mm3);        // 0x12 0x13 0x1a 0x1b 0x16 0x17 0x1e 0x1f
    __m256i dd0 = _mm256_unpacklo_epi64(cc0, cc2);        // 0x00 0x01 0x02 0x03 0x04 0x05 0x06 0x07
    __m256i dd1 = _mm256_unpackhi_epi64(cc0, cc2);        // 0x08 0x09 0x0a 0x0b 0x0c 0x0d 0x0e 0x0f
    __m256i dd2 = _mm256_unpacklo_epi64(cc1, cc3);        // 0x10 0x11 0x12 0x13 0x14 0x15 0x16 0x17
    __m256i dd3 = _mm256_unpackhi_epi64(cc1, cc3);        // 0x18 0x19 0x1a 0x1b 0x1c 0x1d 0x1e 0x1f
    _mm256_storeu_si256((__m256i *)dst + 0, dd0);
    _mm256_storeu_si256((__m256i *)dst + 1, dd1);
    _mm256_storeu_si256((__m256i *)dst + 2, dd2);
    _mm256_storeu_si256((__m256i *)dst + 3, dd3);
}
int main() {
    uint8_t u8a[32] = {
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
    };
    uint8_t u8b[32] = {
        0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27,
        0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
        0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
        0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f,
    };
    __m256i mma = _mm256_loadu_si256((__m256i *)u8a);
    __m256i mmb = _mm256_loadu_si256((__m256i *)u8b);
    show("_mm256_packs_epi32", _mm256_packs_epi32(mma, mmb));
    show("_mm256_packs_epi16", _mm256_packs_epi16(mma, mmb));
    show("_mm256_packus_epi32", _mm256_packus_epi32(mma, mmb));
    show("_mm256_packus_epi16", _mm256_packus_epi16(mma, mmb));
    show("_mm256_unpacklo_epi8", _mm256_unpacklo_epi8(mma, mmb));
    show("_mm256_unpackhi_epi8", _mm256_unpackhi_epi8(mma, mmb));
    show("_mm256_unpacklo_epi16", _mm256_unpacklo_epi16(mma, mmb));
    show("_mm256_unpackhi_epi16", _mm256_unpackhi_epi16(mma, mmb));
    show("_mm256_unpacklo_epi32", _mm256_unpacklo_epi32(mma, mmb));
    show("_mm256_unpackhi_epi32", _mm256_unpackhi_epi32(mma, mmb));
    show("_mm256_unpacklo_epi64", _mm256_unpacklo_epi64(mma, mmb));
    show("_mm256_unpackhi_epi64", _mm256_unpackhi_epi64(mma, mmb));
}
