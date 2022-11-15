#include <math.h>
#include <stdio.h>
#if defined _WIN32
#include <Windows.h>
#elif defined __linux__
#include <unistd.h>
#endif
#define TAU 6.283185307179586
#define PIE 3.141592653589793
#define RT2 1.414213562373095
#define DISPL_H 0x18
#define DISPL_W 0x50
#define GRAPH_H 0x10
#define GRAPH_W 0x20
#define WAITING 0x08
#define DELTA_T 0.01
#define DELTA_U 0.02
#define DELTA_V 0.06
typedef struct {
	unsigned char r, g, b;
} RGB;
RGB rainbow(double theta, double brightness, double grayscale) {
	double B = log(brightness);
	double K = 0.5 + atan(B) / PIE;
	double R = 0.5 - atan(sqrt(B * B + grayscale)) / PIE;
	double r = 256 * (K + R * cos(theta));
	double g = 256 * (K + R * cos(theta - TAU / 3));
	double b = 256 * (K + R * cos(theta + TAU / 3));
	return (RGB){
		(unsigned char)(r > 255 ? 255 : r),
		(unsigned char)(g > 255 ? 255 : g),
		(unsigned char)(b > 255 ? 255 : b),
	};
}
void setc(RGB *fgc, RGB *bgc) {
	fputs("\x1b[0m", stdout);
	if (fgc) {
		printf("\x1b[38;2;%d;%d;%dm", fgc->r, fgc->g, fgc->b);
	}
	if (bgc) {
		printf("\x1b[48;2;%d;%d;%dm", bgc->r, bgc->g, bgc->b);
	}
}
int main() {
#if defined _WIN32
	HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);
	DWORD dwStdoutMode;
	BOOL bStdout = GetConsoleMode(hStdout, &dwStdoutMode);
	if (bStdout && !SetConsoleMode(hStdout, dwStdoutMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING)) {
		return 1;
	}
	setvbuf(stdout, NULL, _IOFBF, 0x10000);	 // stream will be fully buffered.
#endif
	printf("\033[?1049h\033[?25l");
	for (float T = 0; T < TAU; T += DELTA_T) {
		float W = 3.0 * T, Z = 1.0 * T;
		float z[DISPL_H][DISPL_W] = {};
		RGB fgc[DISPL_H][DISPL_W] = {};
		for (float u = 0; u < TAU; u += DELTA_U) {
			for (float v = 0; v < TAU; v += DELTA_V) {
				float su = sin(u), cu = cos(u);
				float sv = sin(v), cv = cos(v);
				float sW = sin(W), cW = cos(W);
				float sZ = sin(Z), cZ = cos(Z);
				float h = 2 + cv;
				float t = su * h * cW - sv * sW;
				float d = su * h * sW + sv * cW + 5;
				int y = DISPL_H * 0.5 + GRAPH_H * (cu * h * sZ + t * cZ) / d;
				int x = DISPL_W * 0.5 + GRAPH_W * (cu * h * cZ - t * sZ) / d;
				if (DISPL_H > y && y >= 0 && DISPL_W > x && x >= 0 && z[y][x] < 1 / d) {
					double c = (su * sv - cu * cv) - TAU / 6;
					double b = (sv * sW - su * cv * cW) * cZ - su * cv * sW - sv * cW - cu * cv * sZ;
					fgc[y][x] = rainbow(c, b * RT2, 0.2), z[y][x] = 1 / d;
				}
			}
		}
		for (int y = 0; y < DISPL_H; y++) {
			printf("\x1b[%d;0H", y + 1);
			for (int x = 0; x < DISPL_W; x++) {
				setc(&fgc[y][x], NULL);
				putchar(z[y][x] ? '@' : ' ');
			}
		}
		fflush(stdout);
#if defined _WIN32
		Sleep(WAITING);
#elif defined __linux__
		usleep(WAITING * 1000);
#endif
	};
	printf("\033[?1049l\033[?25h");
#if defined _WIN32
	if (bStdout && !SetConsoleMode(hStdout, dwStdoutMode)) {
		return 1;
	}
#endif
	return 0;
}
