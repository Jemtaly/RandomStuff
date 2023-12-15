#!/usr/bin/python3
import random
import sys
sys.setrecursionlimit(0x10000)
class ECC:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
    def chk(self, P):
        return P is None or (P[0] * P[0] * P[0] - P[1] * P[1] + self.a * P[0] + self.b) % self.p == 0
    def inv(self, P):
        if P is None:
            return None
        return P[0], P[1] and self.p - P[1]
    def add(self, P, Q):
        if P is None and Q is None:
            return None
        if P is None:
            return Q
        if Q is None:
            return P
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % self.p == 0:
                return
            tan = pow(P[1] + Q[1], self.p - 2, self.p) * (P[0] * Q[0] * 3 + self.a)
        else:
            tan = pow(Q[0] - P[0], self.p - 2, self.p) * (Q[1] - P[1])
        x = (tan * tan - P[0] - Q[0]) % self.p
        y = (tan * (P[0] - x) - P[1]) % self.p
        return x, y
    def dot(self, P, n):
        if n == +0:
            return None
        if n == -1:
            return self.inv(P)
        Q = self.dot(P, n >> 1)
        return self.add(self.add(Q, Q), P) if n & 1 else self.add(Q, Q)
if __name__ == '__main__':
    # Public Parameters (secp256k1)
    a = 0x0000000000000000000000000000000000000000000000000000000000000000
    b = 0x0000000000000000000000000000000000000000000000000000000000000007
    p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
    n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    x = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
    y = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
    ecc = ECC(a, b, p)
    G = (x, y)
    # Alice's Private Key
    u = random.randrange(1, n)
    U = ecc.dot(G, u)
    # Bob's Private Key
    v = random.randrange(1, n)
    V = ecc.dot(G, v)
    assert ecc.dot(U, v) == ecc.dot(V, u) # Shared Secret
