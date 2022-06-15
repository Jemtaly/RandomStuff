#!/usr/bin/python3
freq = [
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015, 0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406,
    0.06749, 0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758, 0.00978, 0.02360, 0.00150, 0.01974, 0.00074,
]
def mini(iterable):
    minv = float('inf')
    for i, v in enumerate(iterable):
        if v < minv: mini, minv = i, v
    return mini
def get_key(clst):
    cycl, chck = 1, False
    while not chck:
        cycl, chck = cycl + 1, True
        for n in range(cycl):
            smin, smax = len(clst[n::cycl]), 0
            for c in range(26):
                stat = clst[n::cycl].count(c)
                if stat < smin: smin = stat
                if stat > smax: smax = stat
            chck &= smin * 20 < smax
    return [mini(sum((clst[n::cycl].count(i) / len(clst) - freq[i - k]) ** 2 for i in range(26)) for k in range(26)) for n in range(cycl)]
def encrypt(klst, plst):
    return [(p + klst[i % len(klst)]) % 26 for i, p in enumerate(plst)]
def decrypt(klst, clst):
    return [(c - klst[i % len(klst)]) % 26 for i, c in enumerate(clst)]
def main():
    ctxt = input()
    clst = []
    for c in ctxt:
        if c.isupper():
            clst.append(ord(c) - 65)
        if c.islower():
            clst.append(ord(c) - 97)
    klst = get_key(clst)
    plst = decrypt(klst, clst)
    ptxt, i = '', iter(plst)
    for c in ctxt:
        ptxt += chr(next(i) + 65) if c.isupper() else chr(next(i) + 97) if c.islower() else c
    print(ptxt)
if __name__ == '__main__':
    main()
