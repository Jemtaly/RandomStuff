#!/usr/bin/python3
def gcd(a, b):
    return a if b == 0 else gcd(b, a % b)
class Rational:
    V = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    def __init__(self, n = 0, d = 1):
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
        return Rational(self.d ** -n, self.n ** -n) if n < 0 else Rational(self.n ** n, self.d ** n)
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
    def __repr__(self, base = 10):
        assert 2 <= base <= 36
        s = '-' if self.n < 0 else '+' if self.n > 0 else '±'
        if self.d:
            m, n = divmod(abs(self.n), self.d)
            a, b, r = [], [], {}
            while m:
                m, t = divmod(m, base)
                a.append(t)
            while n not in r:
                r[n] = len(b)
                t, n = divmod(n * base, self.d)
                b.append(t)
            v = ''.join(Rational.V[i] for i in a[::-1]) + '.' + ''.join(Rational.V[i] for i in b[:r[n]]) + '(' + ''.join(Rational.V[i] for i in b[r[n]:]) + ')'
        else:
            v = 'Inf' if self.n else 'NaN'
        return s + v
