#!/usr/bin/python3
import random
import sys
sys.setrecursionlimit(0x10000)
def exgcd(a, b):
    if b == 0:
        return abs(a), ((a > 0) - (a < 0), 0)
    d, (x, y) = exgcd(b, a % b)
    return d, (y, x - a // b * y)
def modinv(a, m):
    d, (r, _) = exgcd(a, m)
    assert d == 1
    return r % m
def moddiv(a, b, m):
    d, (r, _) = exgcd(b, m)
    assert a % d == 0
    n = m // d
    return a // d * r % n, n
def choice(a, b, n):
    res = set()
    while len(res) < n:
        res.add(random.randrange(a, b))
    return res
def crt(D):
    R, M = 0, 1
    for r, m in D:
        d, (N, n) = exgcd(M, m)
        assert (r - R) % d == 0
        R += (r - R) // d * N * M
        M *= m // d
    return R % M, M
def generate(coeffs, x, q):
    return sum(c * x ** i for i, c in enumerate(coeffs)) % q
def lagrange(points, q):
    n = len(points)
    coeffs = [0 for _ in range(n)]
    prod = [1]
    for x, _ in points:
        prod = [(v - x * u) % q for u, v in zip(prod + [0], [0] + prod)]
    for j, (xj, yj) in enumerate(points):
        dj = 1
        for m, (xm, ym) in enumerate(points):
            if m != j:
                dj = dj * (xj - xm) % q
        qj = modinv(dj, q)
        rj = modinv(xj, q)
        temp = 0
        for i in range(n):
            temp = (temp - prod[i]) * rj % q
            coeffs[i] = (coeffs[i] + yj * qj * temp) % q
    return coeffs
def polyadd(a, b, m):
    res = [0] * max(len(a), len(b))
    for i in range(len(a)):
        res[i] += a[i]
    for i in range(len(b)):
        res[i] += b[i]
    return [x % m for x in res]
def polysub(a, b, m):
    res = [0] * max(len(a), len(b))
    for i in range(len(a)):
        res[i] += a[i]
    for i in range(len(b)):
        res[i] -= b[i]
    return [x % m for x in res]
def polymul(a, b, m):
    res = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            res[i + j] += a[i] * b[j]
    return [x % m for x in res]
def polydm(a, b, m):
    q = []
    r = a[::-1]
    d = b[::-1]
    for _ in range(len(a) - len(d) + 1):
        t = r[0] * modinv(d[0], m) % m
        for i in range(len(d)):
            r[i] = (r[i] - t * d[i]) % m
        q.append(t)
        r.pop(0)
    return q[::-1], r[::-1]
def nsqrt(n):
    amin, amax = 0, n + 1
    while amax - amin > 1:
        a = (amax + amin) // 2
        if a * a > n:
            amax = a
        else:
            amin = a
    return amin
def chkPrime(n):
    if n == 2:
        return True
    if n < 2 or n & 1 == 0:
        return False
    s, k = n - 1, 0
    while s & 1 == 0:
        s, k = s >> 1, k + 1
    for _ in range(16):
        a = random.randrange(1, n)
        t = pow(a, s, n)
        if t == 1:
            continue
        for _ in range(k):
            if t == n - 1:
                break
            t = t * t % n
        else:
            return False
    return True
def genPrime(l):
    while True:
        r = random.randrange(1 << l - 1, 1 << l)
        if chkPrime(r):
            return r
def legendre(a, p):
    assert chkPrime(p) and p != 2
    return (pow(a, (p - 1) // 2, p) + 1) % p - 1
