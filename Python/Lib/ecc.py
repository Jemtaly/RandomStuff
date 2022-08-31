#!/usr/bin/python3
import sys
sys.setrecursionlimit(0x10000)
class ECC:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
    def check(self, P):
        return not P or (P[0] * P[0] * P[0] - P[1] * P[1] + self.a * P[0] + self.b) % self.p == 0
    def inv(self, P):
        if not P:
            return
        return P[0], -P[1] % self.p
    def add(self, P, Q):
        if not P:
            return Q
        if not Q:
            return P
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % self.p == 0:
                return
            lmd = pow(P[1] + Q[1], self.p - 2, self.p) % self.p * (P[0] * Q[0] * 3 + self.a)
        else:
            lmd = pow(Q[0] - P[0], self.p - 2, self.p) % self.p * (Q[1] - P[1])
        x = (lmd * lmd - P[0] - Q[0]) % self.p
        y = (lmd * (P[0] - x) - P[1]) % self.p
        return x, y
    def mult(self, n, P):
        if n == 0:
            return
        if n == -1:
            return self.inv(P)
        Q = self.mult(n >> 1, P)
        return self.add(self.add(Q, Q), P) if n & 1 else self.add(Q, Q)
