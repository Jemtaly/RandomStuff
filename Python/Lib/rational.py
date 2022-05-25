#!/usr/bin/python3
v = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
def gcd(a, b):
    return a if b == 0 else gcd(b, a % b)
class Rational:
    def __init__(self, n=0, d=1):
        if d == 0:
            self.n = (n > 0) - (n < 0)
            self.d = 0
        else:
            q = gcd(n, d)
            self.n = n // q
            self.d = d // q
    def __pos__(self):
        return Rational(self.n, self.d)
    def __neg__(self):
        return Rational(-self.n, self.d)
    def __invert__(self):
        return Rational(self.d, self.n)
    def __add__(self, fles):
        return Rational(self.n * fles.d + fles.n * self.d, self.d * fles.d)
    def __sub__(self, fles):
        return Rational(self.n * fles.d - fles.n * self.d, self.d * fles.d)
    def __mul__(self, fles):
        return Rational(self.n * fles.n, self.d * fles.d)
    def __truediv__(self, fles):
        return Rational(self.n * fles.d, self.d * fles.n)
    def __pow__(self, n):
        return Rational(self.n ** n, self.d ** n)
    def __eq__(self, fles):
        return (self - fles).n == 0
    def __gt__(self, fles):
        return (self - fles).n > 0
    def __lt__(self, fles):
        return (self - fles).n < 0
    def __ne__(self, fles):
        return (self - fles).n != 0
    def __ge__(self, fles):
        return (self - fles).n >= 0
    def __le__(self, fles):
        return (self - fles).n <= 0
    def __repr__(self, base=10):
        if self.d == 0:
            return ('NaN', 'Inf', '-Inf')[self.n]
        m, n = divmod(abs(self.n), self.d)
        a, b, r = [], [], [None for _ in range(self.d)]
        while m:
            m, t = divmod(m, base)
            a.append(t)
        if not a:
            a.append(0)
        while r[n] == None:
            r[n] = len(b)
            t, n = divmod(n * base, self.d)
            b.append(t)
        return ('-' if self.n < 0 else '') + ''.join([v[i] for i in a[::-1]]) + '.' + ''.join([v[i] for i in b[:r[n]]]) + '(' + ''.join([v[i] for i in b[r[n]:]]) + ')'
