#!/usr/bin/python3
def exgcd(a, b):
    if b == 0:
        return a, (1, 0)
    else:
        d, (x, y) = exgcd(b, a % b)
        return d, (y, x - a // b * y)
def gcd(l):
    return 0 if len(l) == 0 else l[0] if len(l) == 1 else exgcd(gcd(l[::2]), gcd(l[1::2]))[0]
def lcm(l):
    return 1 if len(l) == 0 else l[0] if len(l) == 1 else (lambda x, y: x * y // exgcd(x, y)[0])(lcm(l[::2]), lcm(l[1::2]))
def crt(d):
    A, M = 0, 1
    for a, m in d:
        d, (r, _) = exgcd(M, m)
        if (a - A) % d:
            return None
        A += M * r * (a - A) // d
        M *= m // d
    return A, M
def moddiv(a, b, m):
    d, (r, _) = exgcd(b, m)
    if a % d:
        return None
    return r * (a // d), m // d
def reduce(l):
    q = gcd(l)
    return type(l)((i // q for i in l) if q else (0 for _ in l))
def ref(m):
    s = []
    j = 0
    while m and j < len(m[0]):
        for i in range(len(m)):
            if m[i][j] != 0:
                s.append(reduce(m[i]))
                m.pop(i)
                for i in range(len(m)):
                    m[i] = [m[i][y] * s[-1][j] - s[-1][y] * m[i][j] for y in range(len(m[0]))]
                break
        j += 1
    return s + m
def rref(m):
    m = ref(m)
    for i in range(len(m))[::-1]:
        for j in range(len(m[0])):
            if m[i][j] != 0:
                m[i] = reduce(m[i])
                for x in range(i):
                    m[x] = [m[x][y] * m[i][j] - m[i][y] * m[x][j] for y in range(len(m[0]))]
                break
    return m
