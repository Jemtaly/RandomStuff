ABC = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
SEQ = [9, 8, 1, 6, 2, 4]
ADD = 0x00000002084007c0
XOR = 0x000000000a93b324
MSK = 0xffffffffffffffff
def enc(av):
    av = (av ^ XOR) + ADD & MSK
    bv = [None] * 10
    for i in SEQ:
        av, d = divmod(av, 58)
        bv[i] = ABC[d]
    bv[0] = ABC[13]
    bv[3] = ABC[31]
    bv[5] = ABC[13]
    bv[7] = ABC[40]
    bv = 'BV' + ''.join(bv)
    return bv
def dec(bv):
    bv = bv[2:]
    av = 0
    for i in reversed(SEQ):
        av = av * 58 + ABC.index(bv[i])
    av = (av - ADD & MSK) ^ XOR
    return av
