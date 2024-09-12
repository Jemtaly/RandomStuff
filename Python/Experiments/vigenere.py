#!/usr/bin/env python3


import argparse
import sys


freq = [
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015, 0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406,
    0.06749, 0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758, 0.00978, 0.02360, 0.00150, 0.01974, 0.00074,
]


def analysis_with_len(carr, l):
    kcur = []
    scur = 0
    for n in range(l):
        row = carr[n::l]
        nums = [0] * 26
        for i in row:
            nums[i] += 1
        i, v = min(enumerate(sum((nums[i] / len(row) - freq[i - j]) ** 2 for i in range(26)) / 26 for j in range(26)), key=lambda x: x[1])
        kcur.append(i)
        scur = scur + v
    vcur = scur / l
    return kcur, vcur


def analysis(carr):
    d = 1
    l = 0
    vrec = float("inf")
    while True:
        l = l + d
        kcur, vcur = analysis_with_len(carr, l)
        if vcur > vrec * 2:
            return krec, vrec
        if vcur < vrec:
            vrec = vcur
            krec = kcur
            d = l


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
    txt, i = "", iter(arr)
    for c in fmt:
        if c.isupper():
            c = chr(next(i) + 65)
        if c.islower():
            c = chr(next(i) + 97)
        txt += c
    return txt


def main():
    parser = argparse.ArgumentParser(description="Vigenere Cipher Auto-Decrypter")
    parser.add_argument("-i", dest="input", help="input file", type=argparse.FileType("r"), default="-")
    parser.add_argument("-o", dest="output", help="output file", type=argparse.FileType("w"), default="-")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-e", dest="encrypt", help="encrypt key", type=str)
    mode.add_argument("-d", dest="decrypt", help="decrypt key", nargs="?", type=str)
    args = parser.parse_args()
    etxt = args.encrypt
    dtxt = args.decrypt
    ctxt = args.input.read()
    carr = decode(ctxt)
    if dtxt is None and etxt is None:
        karr = analysis(carr)[0]
        print("Key:", "".join(chr(k + 65) for k in karr), file=sys.stderr)
        parr = decrypt(karr, carr)
    elif etxt is not None:
        karr = decode(etxt)
        parr = encrypt(karr, carr)
    elif dtxt is not None:
        karr = decode(dtxt)
        parr = decrypt(karr, carr)
    ptxt = encode(ctxt, parr)
    args.output.write(ptxt)


if __name__ == "__main__":
    main()
