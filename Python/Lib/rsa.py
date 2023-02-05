import sys, random
sys.setrecursionlimit(0x10000)
def exgcd(a, b):
    if b == 0:
        return abs(a), ((a > 0) - (a < 0), 0)
    d, (x, y) = exgcd(b, a % b)
    return d, (y, x - a // b * y)
def power(b, p, m):
    if p == 0:
        return 1
    t = power(b, p >> 1, m)
    return (t * t * b if p & 1 else t * t) % m
def sqrt(n):
    amin, amax = 0, n + 1
    while amax - amin > 1:
        a = (amax + amin) // 2
        if a * a > n:
            amax = a
        else:
            amin = a
    return amin
def isprime(n):
    if n == 2:
        return True
    if n < 2 or n & 1 == 0:
        return False
    s, k = n - 1, 0
    while s & 1 == 0:
        s, k = s >> 1, k + 1
    for _ in range(16):
        a = random.randrange(1, n)
        t = power(a, s, n)
        if t == 1:
            continue
        for _ in range(k):
            if t == n - 1:
                break
            t = t * t % n
        else:
            return False
    return True
def randprime(l):
    while True:
        r = random.getrandbits(l)
        if isprime(r):
            return r
def RSAGenKey(l):
    p, q = randprime(l), randprime(l)
    phi = (p - 1) * (q - 1)
    while True:
        e = random.randrange(0, phi)
        gcd, (r, _) = exgcd(e, phi)
        if gcd == 1:
            d = r % phi
            return p, q, e, d
def RSACrypt(n, k, x):
    return power(x, k, n)
def CRTCrypt(p, q, k, x):
    xp = x % p
    xq = x % q
    kp = k % (p - 1)
    kq = k % (q - 1)
    mp = power(xp, kp, p)
    mq = power(xq, kq, q)
    _, (r, s) = exgcd(p, q)
    return (mp * s * q + mq * r * p) % (p * q)
def main():
    p, q, e, d = RSAGenKey(1024)
    n = p * q
    M = 0xfedcba9876543210
    S = CRTCrypt(p, q, e, M) # signature
    V = RSACrypt(n, d, S)    # verification
    assert M == V
    C = RSACrypt(n, e, M)    # encryption
    P = CRTCrypt(p, q, d, C) # decryption
    assert M == P
