import random
import sys
sys.setrecursionlimit(0x10000)
def exgcd(a, b):
    if b == 0:
        return abs(a), ((a > 0) - (a < 0), 0)
    d, (x, y) = exgcd(b, a % b)
    return d, (y, x - a // b * y)
def inv(a, n):
    d, (x, _) = exgcd(a, n)
    assert d == 1
    return x % n
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
        r = random.getrandbits(l)
        if chkPrime(r):
            return r
def legendre(a, p):
    assert chkPrime(p) and p != 2
    return (pow(a, (p - 1) >> 1, p) + 1) % p - 1
