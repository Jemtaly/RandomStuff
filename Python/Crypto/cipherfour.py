import numpy
S_BOX = numpy.array([
    0x6, 0x4, 0xc, 0x5, 0x0, 0x7, 0x2, 0xe,
    0x1, 0xf, 0x3, 0xd, 0x8, 0xa, 0x9, 0xb
])
R_BOX = numpy.argsort(S_BOX)
S_MAT = numpy.array(
    list(map(list, (map('{:04b}'.format, S_BOX)))), int).reshape(2, 2, 2, 2, 4)
R_MAT = numpy.array(
    list(map(list, (map('{:04b}'.format, R_BOX)))), int).reshape(2, 2, 2, 2, 4)
def encrypt(m, K):
    for k in K[0:4:+1]:
        m = S_MAT[tuple((m ^ k).T)].T
    return m ^ K[4]
def decrypt(c, K):
    for k in K[4:0:-1]:
        c = R_MAT[tuple((c ^ k).T.T)]
    return c ^ K[0]
def encode(n):
    return numpy.array(list('{:016b}'.format(n)), int).reshape(4, 4)
def decode(m):
    return int(''.join(map(str, m.reshape(16))), 2)
def get_frequency(dm, dc, Kn, mn):
    import random
    DDT = numpy.zeros(0x10000)
    Ks = [[encode(random.getrandbits(16)) for _ in range(5)] for _ in range(Kn)]
    ms = [encode(random.getrandbits(16)) for _ in range(mn)]
    for K in Ks:
        for m in ms:
            n = m ^ encode(dm)
            c = encrypt(m, K)
            d = encrypt(n, K)
            DDT[decode(c ^ d)] += 1
    return DDT[dc] / DDT.sum()
def get_possibility(dm, dc):
    # encrypt 2 rounds
    D_enc = {dm: 1}
    for _ in range(2):
        D_tmp = {}
        for d in D_enc:
            for i in range(0x10000):
                j = d ^ i
                D = (S_BOX[i >> 12] << 12 | S_BOX[i >> 8 & 0xf] << 8 | S_BOX[i >> 4 & 0xf] << 4 | S_BOX[i & 0xf]) \
                  ^ (S_BOX[j >> 12] << 12 | S_BOX[j >> 8 & 0xf] << 8 | S_BOX[j >> 4 & 0xf] << 4 | S_BOX[j & 0xf])
                D_tmp[D] = D_enc[d] + D_tmp.get(D, 0)
        D_enc = {decode(encode(k).T): v for k, v in D_tmp.items()}
    # decrypt 2 rounds
    D_dec = {dc: 1}
    for _ in range(2):
        D_tmp = {decode(encode(k).T): v for k, v in D_dec.items()}
        D_dec = {}
        for d in D_tmp:
            for i in range(0x10000):
                j = d ^ i
                D = (R_BOX[i >> 12] << 12 | R_BOX[i >> 8 & 0xf] << 8 | R_BOX[i >> 4 & 0xf] << 4 | R_BOX[i & 0xf]) \
                  ^ (R_BOX[j >> 12] << 12 | R_BOX[j >> 8 & 0xf] << 8 | R_BOX[j >> 4 & 0xf] << 4 | R_BOX[j & 0xf])
                D_dec[D] = D_tmp[d] + D_dec.get(D, 0)
    # meet in the middle
    return sum(D_enc.get(k, 0) * D_dec.get(k, 0) for k in range(0x10000)) / (sum(D_enc.values()) * sum(D_dec.values()))
def main():
    dm = 0x0020
    do = 0x0020
    print('f({:04x}, {:04x}) = {}'.format(dm, do, get_frequency(dm, do, 100, 100)))
    print('p({:04x}, {:04x}) = {}'.format(dm, do, get_possibility(dm, do)))
if __name__ == '__main__':
    main()
