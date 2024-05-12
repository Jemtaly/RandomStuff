#!/usr/bin/python3
import sys
import argparse
freq = [
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015, 0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406,
    0.06749, 0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758, 0.00978, 0.02360, 0.00150, 0.01974, 0.00074,
]
def minidx(arr):
    x = float('inf')
    for i, v in enumerate(arr):
        if v < x:
            j, x = i, v
    return j
def analysis(carr):
    cycl, chck = 0, False
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
            chck = chck and smin * 20 < smax
    return [minidx(sum((carr[n::cycl].count(i) / len(carr) - freq[i - k]) ** 2 for i in range(26)) for k in range(26)) for n in range(cycl)]
def encrypt(karr, parr):
    return [(p + karr[i % len(karr)]) % 26 for i, p in enumerate(parr)]
def decrypt(karr, carr):
    return [(c - karr[i % len(karr)]) % 26 for i, c in enumerate(carr)]
def decode(txt):
    arr = []
    for c in txt:
        if c.isupper():
            arr.append(ord(c) - 65)
        if c.islower():
            arr.append(ord(c) - 97)
    return arr
def encode(fmt, arr):
    txt, i = '', iter(arr)
    for c in fmt:
        if c.isupper():
            c = chr(next(i) + 65)
        if c.islower():
            c = chr(next(i) + 97)
        txt += c
    return txt
def main():
    parser = argparse.ArgumentParser(description = 'Vigenere Cipher Auto-Decrypter')
    parser.add_argument('-i', dest = 'input', help = 'input file', type = argparse.FileType('r'), default = '-')
    parser.add_argument('-o', dest = 'output', help = 'output file', type = argparse.FileType('w'), default = '-')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('-e', dest = 'encrypt', help = 'encrypt key', type = str)
    mode.add_argument('-d', dest = 'decrypt', help = 'decrypt key', nargs = '?', type = str)
    args = parser.parse_args()
    etxt = args.encrypt
    dtxt = args.decrypt
    ctxt = args.input.read()
    carr = decode(ctxt)
    if dtxt is None and etxt is None:
        karr = analysis(carr)
        print('Key:', ''.join(chr(k + 65) for k in karr), file = sys.stderr)
        parr = decrypt(karr, carr)
    elif etxt is not None:
        karr = decode(etxt)
        parr = encrypt(karr, carr)
    elif dtxt is not None:
        karr = decode(dtxt)
        parr = decrypt(karr, carr)
    ptxt = encode(ctxt, parr)
    args.output.write(ptxt)
if __name__ == '__main__':
    main()
