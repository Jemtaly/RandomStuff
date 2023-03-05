#!/usr/bin/python3
def padding_oracle_attack(iv, cc, oracle):
    size = len(iv)
    assert len(cc) == size
    aa = bytearray(size)
    for i in range(size)[::-1]:
        for j in range(i + 1, size):
            aa[j] ^= size - i
        while oracle(aa + cc):
            aa[i] += 1
        for j in range(i, size):
            aa[j] ^= size - i
    return bytearray(i ^ j for i, j in zip(iv, aa))
def main():
    import subprocess
    ivcc = bytearray.fromhex('02c6a098a0c5013c45faa400e422e95b59d50c6c47b19c1aa661a26dcfb2050beff3d2773d0ee08be94b603020e85b3129db055a450378d72a4d10582e14f440')
    pp = bytearray()
    for n in range(16, len(ivcc), 16):
        iv = ivcc[slice(n - 16, n)]
        cc = ivcc[slice(n, n + 16)]
        pp.extend(padding_oracle_attack(iv, cc, lambda a: subprocess.call(['dec_oracle', a.hex()], stdout = subprocess.PIPE) != 200))
    pp = pp[:-pp[-1]]
    print(pp.decode())
if __name__ == '__main__':
    main()
