#!/usr/bin/python3
import sys, random
sys.setrecursionlimit(0x10000)
def sqrt(n):
    min, max = 0, n + 1
    while max - min > 1:
        a = (max + min) // 2
        b = a ** 2
        if b > n:
            max = a
        else:
            min = a
    return min
def power(b, p, m):
    if p == 0:
        return 1
    t = power(b, p >> 1, m)
    return (t * t * b if p & 1 else t * t) % m
def exgcd(a, b):
    if b == 0:
        return a, (1, 0)
    else:
        gcd, (x, y) = exgcd(b, a % b)
        return gcd, (y, x - a // b * y)
def isprime(n):
    if n == 2:
        return True
    if n < 2 or n & 1 == 0:
        return False
    for _ in range(16):
        a = random.randrange(1, n)
        d = n - 1
        while d & 1 == 0:
            t = power(a, d, n)
            if t == n - 1:
                break
            elif t != 1:
                return False
            d >>= 1
    return True
def randprime(l):
    while True:
        r = random.getrandbits(l)
        if isprime(r):
            return r
def encode(s):
    n, t = 0, 0
    for c in s:
        n |= c << t
        t += 8
    return n
def decode(n):
    s = []
    while n:
        s.append(n & 255)
        n >>= 8
    return bytes(s)
class RSA:
    def __init__(self, l):
        p, q = randprime(l), randprime(l)
        self.n = p * q
        phi = (p - 1) * (q - 1)
        while True:
            self.e = random.randrange(0, phi)
            gcd, (r, _) = exgcd(self.e, phi)
            if gcd == 1:
                self.d = r % phi
                break
    def encrypt(self, m):
        return power(m, self.e, self.n)
    def decrypt(self, c):
        return power(c, self.d, self.n)
