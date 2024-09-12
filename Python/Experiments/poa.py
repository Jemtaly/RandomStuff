#!/usr/bin/env python3


import Crypto.Cipher.AES as AES
import Crypto.Random as Random
import Crypto.Util.Padding as Padding
import Crypto.Util.strxor as strxor


def padding_oracle_attack_one(iv, ct, oracle):
    bs = len(iv)
    assert len(ct) == bs
    while True:
        dx = bytearray(bs)
        for i in reversed(range(bs)):
            px = Random.get_random_bytes(i)
            px = Padding.pad(px, bs)
            for dx[i] in range(256):
                ix = strxor.strxor(px, dx)
                if oracle(ix, ct):
                    break
            else:
                break
        else:
            break
    return strxor.strxor(iv, dx)


def padding_oracle_attack_any(iv, ct, oracle):
    bs = len(iv)
    assert len(ct) % bs == 0
    pt = bytearray()
    while ct:
        pt.extend(padding_oracle_attack_one(iv, ct[:bs], oracle))
        iv, ct = ct[:bs], ct[bs:]
    return Padding.unpad(pt, bs)


class Server:
    def __init__(self):
        self.key = Random.get_random_bytes(16)

    def encrypt(self, pt):
        iv = Random.get_random_bytes(16)
        pt = Padding.pad(pt, 16)
        ct = AES.new(self.key, AES.MODE_CBC, iv).encrypt(pt)
        return iv, ct

    def decrypt(self, iv, ct):
        pt = AES.new(self.key, AES.MODE_CBC, iv).decrypt(ct)
        pt = Padding.unpad(pt, 16)
        return pt

    def oracle(self, iv, ct):
        try:
            self.decrypt(iv, ct)
        except ValueError:
            return False
        else:
            return True


def main():
    server = Server()
    pt = Random.get_random_bytes(256)
    iv, ct = server.encrypt(pt)
    re = padding_oracle_attack_any(iv, ct, server.oracle)
    if re == pt:
        print("Success")
    else:
        print("Failure")


if __name__ == "__main__":
    main()
