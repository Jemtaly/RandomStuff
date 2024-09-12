#!/usr/bin/env python3


import time


class Montgomery:
    def __init__(self, N):
        R, B = 1, 0
        while R < N:
            R *= 2
            B += 1
        self.N = N
        self.R = R  # the multiplicative identity in Montgomery domain
        self.B = B
        self.M = R - 1
        self.K = R - pow(N, -1, R)
        self.Q = R * R % N

    def redc(self, T):
        # returns T / R (mod N), where T < R * N
        t = T + ((T & self.M) * self.K & self.M) * self.N >> self.B
        return t - self.N if t >= self.N else t

    def encode(self, x):
        return self.redc(x * self.Q)

    def decode(self, x):
        return self.redc(x)

    def mult(self, x, y):
        return self.redc(x * y)


def test():
    m = 1000000007
    mont = Montgomery(m)
    x = 123456789
    y = 987654321
    X = mont.encode(x)
    Y = mont.encode(y)
    Z = mont.mult(X, Y)
    z = mont.decode(Z)
    assert z == x * y % m
    print("Test passed")
    start = time.time()
    for i in range(1000000):
        Z = mont.mult(X, Y)
    print("Montgomery multiplication:", time.time() - start)
    start = time.time()
    for i in range(1000000):
        z = x * y % m
    print("Modular multiplication:", time.time() - start)


if __name__ == "__main__":
    test()
