import os
TWI = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
B64 = '0123456789@ABCDEFGHIJKLMNOPQRSTUVWXYZ`abcdefghijklmnopqrstuvwxyz'
T2B = {t: b for t, b in zip(TWI, B64)}
T2I = {t: i for i, t in enumerate(TWI)}
def twi2int(s):
    return sum(T2I[c] * 64 ** i for i, c in enumerate(reversed(s)))
def int2twi(n):
    return ''.join(TWI[n // 64 ** i % 64] for i in reversed(range(15)))
def t2iname(f):
    path, name = os.path.split(f)
    name, ext = os.path.splitext(name)
    return os.path.join(path, '{:028}{}'.format(twi2int(name), ext))
def i2tname(l):
    path, name = os.path.split(l)
    name, ext = os.path.splitext(name)
    return os.path.join(path, '{}{}'.format(int2twi(int(name)), ext))
def twisort(l):
    d = {twi2int(os.path.splitext(os.path.basename(s))[0]): s for s in l}
    return sorted(l, key = d.get)
