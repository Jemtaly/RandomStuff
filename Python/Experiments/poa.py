#!/usr/bin/python3
import Crypto.Cipher.AES as AES
import Crypto.Util.Padding as Padding
import Crypto.Random as Random
def padding_oracle_attack_one(iv, ct, oracle):
    bs = len(iv)
    assert len(ct) == bs
    xv = bytearray(bs)
    for i in reversed(range(bs)):
        for j in range(i, bs):
            xv[j] = xv[j] ^ bs - i
        while True:
            try:
                oracle.decrypt(xv, ct)
            except ValueError:
                xv[i] = xv[i] + 1 & 0xff
            else:
                break
        for j in range(i, bs):
            xv[j] = xv[j] ^ bs - i
    return bytearray(i ^ x for i, x in zip(iv, xv))
def padding_oracle_attack_any(iv, ct, oracle):
    bs = len(iv)
    assert len(ct) % bs == 0
    pt = bytearray()
    while ct:
        pt.extend(padding_oracle_attack_one(iv, ct[:bs], oracle))
        iv, ct = ct[:bs], ct[bs:]
    return Padding.unpad(pt, bs)
class Oracle:
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
def main():
    oracle = Oracle()
    pt = Random.get_random_bytes(256)
    iv, ct = oracle.encrypt(pt)
    re = padding_oracle_attack_any(iv, ct, oracle)
    if re == pt:
        print('Success')
    else:
        print('Failure')
if __name__ == '__main__':
    main()
