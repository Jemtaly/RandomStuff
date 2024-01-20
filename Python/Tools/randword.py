#!/usr/bin/python3
import math, random
consonant = [
    ['`', 'p', 'b', 't', 'd', 'k', 'g', 'm', 'n', 'l', 'f', 's', 'z', 'c', 'r', 'h', 'x'],
    ['fp', 'ft', 'fk', 'fm', 'fn', 'fl', 'sp', 'st', 'sk', 'sm', 'sn', 'sl', 'cp', 'ct', 'ck', 'cm', 'cn', 'cl', 'xp', 'xt', 'xk', 'xm', 'xn', 'xl'],
    ['pf', 'tf', 'kf', 'ps', 'ts', 'ks', 'pc', 'tc', 'kc', 'ph', 'th', 'kh'],
    ['pl', 'bl', 'tl', 'dl', 'kl', 'gl'],
]
vowel = [
    ['i', 'e', 'a', 'o', 'u', 'w', 'y'],
    ['ej', 'aj', 'oj', 'eo', 'au', 'ou'],
]
def randsyl():
    r = math.tan(random.random() * math.pi / 2)
    c = random.choice(consonant[int(random.random() ** (12 * r) * 4)])
    v = random.choice(vowel[int(random.random() ** (8 / r) * 2)])
    if c == '`' or v in vowel[0]:
        if random.random() < 0.2:
            t = random.choice(['j', 'v'])
            if not (t == 'v' and v in ['u', 'w', 'y'] or t == 'j' and (v in ['i', 'w', 'y'] or v[-1] == 'j')):
                c += t
    if random.random() ** 4 > 0.5:
        v += 'n'
    return c + v
def randword():
    word, i = '', 0
    while i < 0.9:
        syllable = randsyl()
        if word and word[-1] == 'n':
            if syllable[0] in ['p', 'b', 'f', 'm']:
                word = word[:-1] + 'm'
        word += syllable
        i += random.random()
    return word
def main():
    import argparse
    parser = argparse.ArgumentParser(description = 'Random Word Generator')
    parser.add_argument('-n', dest = 'number', help = 'number of words', type = int, default = 1)
    args = parser.parse_args()
    for _ in range(args.number):
        print(randword())
if __name__ == '__main__':
    main()
