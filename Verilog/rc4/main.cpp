#include <iostream>
#include "Vrc4.h"
#include "verilated.h"
using namespace std;
void hexdump(uint8_t const *data, size_t len, size_t width = 16) {
	for (size_t i = 0; i < len; ++i)
		printf("%02X%c", data[i], (i + 1) % width == 0 || i + 1 == len ? '\n' : ' ');
}
void test(Vrc4 &vrc4, size_t keylen, uint8_t *key, size_t msglen, uint8_t *msg, uint8_t *buf) {
	vrc4.rst = 1;  // 将 rst 置 1，开始输入密钥
	for (int i = 0; i < keylen; i++) {
		vrc4.in = key[i];
		vrc4.clk = 0;
		vrc4.eval();
		vrc4.clk = 1;
		vrc4.eval();
	}
	vrc4.rst = 0;  // 将 rst 置 0，开始密钥混淆
	for (int i = 0; i < 256; i++) {
		vrc4.clk = 0;
		vrc4.eval();
		vrc4.clk = 1;
		vrc4.eval();
	}
	for (int i = 0; i < msglen; i++) {
		vrc4.in = msg[i];   // 输入明文
		vrc4.clk = 0;
		vrc4.eval();
		vrc4.clk = 1;
		vrc4.eval();
		buf[i] = vrc4.out;  // 输出密文
	}
}
void show(ostream &o, size_t keylen, uint8_t *key, size_t msglen, uint8_t *msg, uint8_t *buf) {
	o << "Key: " << endl;
	hexdump(key, keylen);
	o << "Msg: " << endl;
	hexdump(msg, msglen);
	o << "Buf: " << endl;
	hexdump(buf, msglen);
}
int main(int argc, char **argv, char **env) {
	// RC4 examples from http://en.wikipedia.org/wiki/RC4
	uint8_t keyA[] = {'K', 'e', 'y'};
	uint8_t msgA[] = {'P', 'l', 'a', 'i', 'n', 't', 'e', 'x', 't'};
	uint8_t bufA[sizeof(msgA)];
	uint8_t keyB[] = {'W', 'i', 'k', 'i'};
	uint8_t msgB[] = {'p', 'e', 'd', 'i', 'a'};
	uint8_t bufB[sizeof(msgB)];
	uint8_t keyC[] = {'S', 'e', 'c', 'r', 'e', 't'};
	uint8_t msgC[] = {'A', 't', 't', 'a', 'c', 'k', ' ', 'a', 't', ' ', 'd', 'a', 'w', 'n'};
	uint8_t bufC[sizeof(msgC)];
	Vrc4 vrc4;
	cout << "-------------- RC4 test A ---------------" << endl;
	test(vrc4, sizeof(keyA), keyA, sizeof(msgA), msgA, bufA);
	show(cout, sizeof(keyA), keyA, sizeof(msgA), msgA, bufA);
	cout << "-------------- RC4 test B ---------------" << endl;
	test(vrc4, sizeof(keyB), keyB, sizeof(msgB), msgB, bufB);
	show(cout, sizeof(keyB), keyB, sizeof(msgB), msgB, bufB);
	cout << "-------------- RC4 test C ---------------" << endl;
	test(vrc4, sizeof(keyC), keyC, sizeof(msgC), msgC, bufC);
	show(cout, sizeof(keyC), keyC, sizeof(msgC), msgC, bufC);
	return 0;
}
