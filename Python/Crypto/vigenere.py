#!/usr/bin/python3
freq = [
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015, 0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406,
    0.06749, 0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758, 0.00978, 0.02360, 0.00150, 0.01974, 0.00074,
]
def mink(iterable):
    minv = float('inf')
    for k, v in enumerate(iterable):
        if v < minv:
            mink, minv = k, v
    return mink
def get_key(carr):
    cycl, chck = 1, False
    while not chck:
        cycl, chck = cycl + 1, True
        for n in range(cycl):
            smin, smax = len(carr[n::cycl]), 0
            for c in range(26):
                stat = carr[n::cycl].count(c)
                if stat < smin:
                    smin = stat
                if stat > smax:
                    smax = stat
            chck &= smin * 20 < smax
    return [mink(sum((carr[n::cycl].count(i) / len(carr) - freq[i - k]) ** 2 for i in range(26)) for k in range(26)) for n in range(cycl)]
def encrypt(karr, parr):
    return [(p + karr[i % len(karr)]) % 26 for i, p in enumerate(parr)]
def decrypt(karr, carr):
    return [(c - karr[i % len(karr)]) % 26 for i, c in enumerate(carr)]
def main():
    ctxt = input()
    carr = []
    for c in ctxt:
        if c.isupper():
            carr.append(ord(c) - 65)
        if c.islower():
            carr.append(ord(c) - 97)
    karr = get_key(carr)
    parr = decrypt(karr, carr)
    ptxt, i = '', iter(parr)
    for c in ctxt:
        if c.isupper():
            c = chr(next(i) + 65)
        if c.islower():
            c = chr(next(i) + 97)
        ptxt += c
    print(ptxt)
if __name__ == '__main__':
    main()
