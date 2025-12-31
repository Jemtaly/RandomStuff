#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, NewType, Literal, TypeGuard, overload

import random
import sys


sys.setrecursionlimit(0x10000)


def sample(a: int, b: int, n: int) -> set[int]:
    """take n elements from [a, b) distinctively"""
    res = set()
    while len(res) < n:
        res.add(random.randrange(a, b))
    return res


def choice(a: int, b: int, n: int) -> list[int]:
    """take n elements from [a, b) independently"""
    res = []
    while len(res) < n:
        res.append(random.randrange(a, b))
    return res


def root(x: int, n: int) -> int:
    """
    - input: x, n
    - output: y such that y <= x ** (1 / n) < y + 1
    """
    l, r = 0, x + 1
    while r - l > 1:
        m = (r + l) // 2
        if m**n > x:
            r = m
        else:
            l = m
    return l


def exgcd(a: int, b: int) -> tuple[int, tuple[int, int]]:
    """
    - input: a, b
    - output: d, (x, y) such that d == (a, b) == a * x + b * y
    """
    if b == 0:
        return abs(a), ((a > 0) - (a < 0), 0)
    d, (x, y) = exgcd(b, a % b)
    return d, (y, x - a // b * y)


def modinv(a: int, m: int) -> int:
    """
    - input: a, m such that (a, m) == 1
    - output: the inverse of a modulo m
    """
    d, (r, _) = exgcd(a, m)
    if d != 1:
        raise ZeroDivisionError
    return r % m


def moddiv(a: int, b: int, m: int) -> tuple[int, int]:
    """
    - input: a, b, m such that (b, m) | a
    - output: k, n such that c == a / b (mod m) if and only if c == k (mod n)
    """
    d, (r, _) = exgcd(b, m)
    if a % d != 0:
        raise ZeroDivisionError
    k = a // d * r
    n = m // d
    return k % n, n


def modpow(a: int, n: int, m: int) -> int:
    """
    - input: a, n, m
    - output: a**n (mod m)
    """
    if n < 0:
        a, n = modinv(a, m), -n
    r = 1
    while n:
        if n % 2 == 1:
            r = r * a % m
        a, n = a * a % m, n // 2
    return r


Remainder = tuple[int, int]  # (remainder, modulus)


def crt(*D: Remainder) -> Remainder:
    """
    - input: D, which is a list of r, m pairs
    - output: R, M such that x == r (mod m) for all r, m in D if and only if x == R (mod M)
    """
    R, M = 0, 1
    for r, m in D:
        d, (N, n) = exgcd(M, m)
        c = r - R
        if c % d != 0:
            raise ZeroDivisionError
        R = R + c // d * N * M
        M = M * m // d
    return R % M, M


OddPrime = NewType("OddPrime", int)
AnyPrime = OddPrime | Literal[2]


@overload
def chkprime(n: int, *, k: int = 16, odd: Literal[True]) -> TypeGuard[OddPrime]: ...


@overload
def chkprime(n: int, *, k: int = 16, odd: Literal[False] = False) -> TypeGuard[AnyPrime]: ...


def chkprime(n: int, *, k: int = 16, odd: bool = False) -> bool:
    if n == 2:
        return not odd
    if n < 2 or n % 2 == 0:
        return False
    s, t = n - 1, 0
    while s % 2 == 0:
        s, t = s // 2, t + 1
    for _ in range(k):
        a = random.randrange(1, n)
        x = modpow(a, s, n)
        if x == 1:
            continue
        for _ in range(t):
            if x == n - 1:
                break
            x = x * x % n
        else:
            return False
    return True


@overload
def genprime(l: int, *, k: int = 16, odd: Literal[True]) -> OddPrime: ...


@overload
def genprime(l: int, *, k: int = 16, odd: Literal[False] = False) -> AnyPrime: ...


def genprime(l: int, *, k: int = 16, odd: bool = False) -> int:
    while True:
        n = random.randrange(1 << l - 1, 1 << l)
        if chkprime(n, k=k, odd=odd):
            return n


Factorization = dict[AnyPrime, int]  # {prime: exponent}


def phi(fact: Factorization) -> int:
    """
    - input: a dictionary that represents the prime factorization of n
    - output: the number of integers less than n and coprime to n
    """
    f = 1
    for p, k in fact.items():
        f *= p**k - p**k // p
    return f


def num(fact: Factorization) -> int:
    """
    - input: a dictionary that represents the prime factorization of n
    - output: the value of n
    """
    n = 1
    for p, k in fact.items():
        n *= p**k
    return n


def modroot(x: int, fact: Factorization, n: int) -> int:
    """
    - input: x, n and a dictionary that represents the prime factorization of m
    - output: x ** (1 / n) (mod m)
    """
    return modpow(x, modinv(n, phi(fact)), num(fact))


def rthroot(x: int, p: OddPrime, k: int, r: int) -> int:
    """
    - input: x, p, k, r such that p is odd prime, r is a prime factor of p**k * (1 - 1 / p)
    - output: h such that h**r == x (mod p**k)
    """
    q, f = p**k, p**k - p**k // p
    assert f % r == 0
    assert modpow(x, f // r, q) == 1
    for z in range(2, p):
        if modpow(z, f // r, q) != 1:
            break
    s, t = f, 0
    while s % r == 0:
        s, t = s // r, t + 1
    v = modinv(r, s)
    S = v * r - 1
    h = modpow(x, v, q)
    a = modpow(z, s, q)
    b = modpow(x, S, q)
    c = modpow(a, r ** (t - 1), q)
    for i in range(1, t):
        d = modpow(b, r ** (t - 1 - i), q)
        j, e = 0, 1
        while d != e:
            j, e = j - 1, e * c % q
        h = modpow(a, j, q) * h % q
        a = modpow(a, r, q)
        b = modpow(a, j, q) * b % q
    return h


def nthroot(x: int, p: OddPrime, k: int, n: int) -> set[int]:
    """
    - input: x, p, k, n such that p is odd prime, n | p**k * (1 - 1 / p)
    - output: all h in Z / p**k such that h**n == x (mod p**k)
    """
    q, f = p**k, p**k - p**k // p
    assert f % n == 0
    assert modpow(x, f // n, q) == 1
    g = 1  # g**n == 1 (mod p**k) and g**i != 1 (mod p**k) for all i < n
    r = 2
    while n > 1:
        a = 0
        while n % r == 0:
            n, a = n // r, a + 1
            x = rthroot(x, p, k, r)
        if a > 0:
            for z in range(2, p):
                if modpow(z, f // r, q) != 1:
                    break
            g = modpow(z, f // r**a, q) * g % q
        r = r + 1
    S = set()
    while x not in S:
        S.add(x)
        x = x * g % q
    return S


def binsqrt(x: int, k: int) -> int:
    """
    - input: x, k such that k >= 3 and x == 1 (mod 8)
    - output: y such that y**2 == x (mod 2**k), y == 1 (mod 8) and 0 <= y < 2 ** (k - 1)
    """
    assert k >= 3
    assert x % 8 == 1
    a = 1
    for i in range(2, k - 1):
        if (a * a - x) % 2 ** (i + 2) != 0:
            a = a + 2**i
    return a


def binroot(x: int, k: int, t: int) -> tuple[tuple[int, int], int]:
    """
    - input: x, k, t such that k >= t + 2 >= 3 and x == 1 (mod 2 ** (t + 2))
    - output: (a, b), c such that y**n == x (mod 2**k) if and only if y == a or b (mod c), where n == 2**t
    """
    assert k >= t + 2 >= 3
    assert x % 2 ** (t + 2) == 1
    for i in range(t):
        x = binsqrt(x, k - i)
    return (x, 2 ** (k - t) - x), 2 ** (k - t)


T = TypeVar("T")


class Group(Generic[T], ABC):
    @abstractmethod
    def zero(self, /) -> T: ...

    @abstractmethod
    def neg(self, a: T, /) -> T: ...

    @abstractmethod
    def add(self, a: T, b: T, /) -> T: ...

    @abstractmethod
    def sub(self, a: T, b: T, /) -> T: ...

    def dot(self, a: T, n: int, /) -> T:
        r = self.zero()
        while n:
            if n % 2 == 1:
                r = self.add(r, a)
            a, n = self.add(a, a), n // 2
        return r


class Ring(Group[T]):
    @abstractmethod
    def one(self, /) -> T: ...

    @abstractmethod
    def mul(self, a: T, b: T, /) -> T: ...

    def pow(self, a: T, n: int, /) -> T:
        r = self.one()
        while n:
            if n % 2 == 1:
                r = self.mul(r, a)
            a, n = self.mul(a, a), n // 2
        return r


class Field(Ring[T]):
    @abstractmethod
    def inv(self, a: T, /) -> T: ...

    @abstractmethod
    def div(self, a: T, b: T, /) -> T: ...


Matrix = list[list[T]]  # m * n matrix


def matadd(f: Group[T], a: Matrix[T], b: Matrix[T], h: int, w: int) -> Matrix[T]:
    """
    - input: a, b, h, w such that a and b are h * w matrices over Z / q
    - output: the sum of a and b
    """
    return [[f.add(a[i][j], b[i][j]) for j in range(w)] for i in range(h)]


def matsub(f: Group[T], a: Matrix[T], b: Matrix[T], h: int, w: int) -> Matrix[T]:
    """
    - input: a, b, h, w such that a and b are h * w matrices over Z / q
    - output: the difference of a and b
    """
    return [[f.sub(a[i][j], b[i][j]) for j in range(w)] for i in range(h)]


def matmul(f: Ring[T], a: Matrix[T], b: Matrix[T], h: int, m: int, w: int) -> Matrix[T]:
    """
    - input: a, b, h, m, w, q such that a is a h * m matrix, b is a m * w matrix over Z / q
    - output: a h * w matrix that is the product of a and b
    """
    res = [[f.zero() for _ in range(w)] for _ in range(h)]
    for i in range(h):
        for j in range(w):
            for k in range(m):
                res[i][j] = f.add(res[i][j], f.mul(a[i][k], b[k][j]))
    return res


def rref(f: Field[T], m: Matrix[T], h: int, w: int) -> Matrix:
    """
    - input: m, h, w, q such that m is a h * w matrix over Z / q
    - output: reduced row echelon form of m
    """
    m = [[m[i][j] for j in range(w)] for i in range(h)]
    for J in range(w):
        I = next((I for I in range(h) if all(m[I][j] == 0 for j in range(J)) and m[I][J] != 0), None)
        if I is None:
            continue
        k = f.inv(m[I][J])
        for j in range(J, w):
            m[I][j] = f.mul(m[I][j], k)
        for i in range(h):
            if i == I:
                continue
            k = m[i][J]
            for j in range(J, w):
                m[i][j] = f.sub(m[i][j], f.mul(m[I][j], k))
    return m


def matinv(f: Field[T], m: Matrix[T], r: int) -> Matrix[T]:
    """
    - input: m, r, q such that m is a r * r matrix over Z / q and det(m) != 0
    - output: the inverse of m
    """
    m = rref(f, [m[i] + [f.one() if i == j else f.zero() for j in range(r)] for i in range(r)], r, r * 2)
    s = [next((i, f.inv(m[i][j])) for i in range(r) if m[i][j] != 0) for j in range(r)]
    return [[f.mul(x, t) for x in m[i][r:]] for i, t in s]


Polynomial = list[T]  # coefficients list


def lagrange(f: Field[T], points: list[tuple[T, T]]) -> Polynomial[T]:
    """
    - input: n points, each of which is a pair of x and y
    - output: coefficients list of the n - 1 degree polynomial that passes through all the points
    """
    Z = [f.one()]
    for x, y in points:
        Z = [f.sub(v, f.mul(x, u)) for u, v in zip(Z + [f.zero()], [f.zero()] + Z)]
    n = len(points)
    Y = [f.zero() for _ in range(n)]
    for j, (x, y) in enumerate(points):
        d = f.one()
        for m, (u, v) in enumerate(points):
            if m != j:
                d = f.mul(d, f.sub(x, u))
        k = f.div(y, d)
        r = f.inv(x)
        t = f.zero()
        for i in range(n):
            t = f.mul(f.sub(t, Z[i]), r)
            Y[i] = f.add(Y[i], f.mul(k, t))
    return Y


def recover(f: Field[T], shares: list[tuple[T, T]], t: T) -> T:
    for x, y in shares:
        if x == t:
            return y
    Z = f.one()
    for x, y in shares:
        Z = f.mul(Z, f.sub(t, x))
    Y = f.zero()
    for j, (x, y) in enumerate(shares):
        d = f.one()
        for m, (u, v) in enumerate(shares):
            if m != j:
                d = f.mul(d, f.sub(x, u))
        k = f.div(y, d)
        r = f.inv(f.sub(t, x))
        Y = f.add(Y, f.mul(k, r))
    return f.mul(Y, Z)


def polyadd(f: Group[T], a: Polynomial[T], b: Polynomial[T]) -> Polynomial[T]:
    res = [f.zero()] * max(len(a), len(b))
    for i in range(len(a)):
        res[i] = f.add(res[i], a[i])
    for i in range(len(b)):
        res[i] = f.add(res[i], b[i])
    return res


def polysub(f: Group[T], a: Polynomial[T], b: Polynomial[T]) -> Polynomial[T]:
    res = [f.zero()] * max(len(a), len(b))
    for i in range(len(a)):
        res[i] = f.add(res[i], a[i])
    for i in range(len(b)):
        res[i] = f.sub(res[i], b[i])
    return res


def polymul(f: Ring[T], a: Polynomial[T], b: Polynomial[T]) -> Polynomial[T]:
    res = [f.zero()] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            res[i + j] = f.add(res[i + j], f.mul(a[i], b[j]))
    return res


def polydm(f: Field[T], a: Polynomial[T], b: Polynomial[T]) -> tuple[Polynomial[T], Polynomial[T]]:
    q = []
    r = a[::-1]
    d = b[::-1]
    for _ in range(len(a) - len(d) + 1):
        t = f.div(r[0], d[0])
        for i in range(len(d)):
            r[i] = f.sub(r[i], f.mul(t, d[i]))
        q.append(t)
        r.pop(0)
    return q[::-1], r[::-1]


def polyval(f: Ring[T], coeffs: Polynomial[T], x: T) -> T:
    r = f.zero()
    for i, c in enumerate(coeffs):
        r = f.add(r, f.mul(c, f.pow(x, i)))
    return r


class FiniteField(Field[int]):
    def __init__(self, p: AnyPrime):
        self.p = p

    def zero(self, /) -> int:
        return 0

    def neg(self, a: int, /) -> int:
        return -a % self.p

    def add(self, a: int, b: int, /) -> int:
        return (a + b) % self.p

    def sub(self, a: int, b: int, /) -> int:
        return (a - b) % self.p

    def one(self, /) -> int:
        return 1

    def inv(self, a: int, /) -> int:
        return modinv(a, self.p)

    def mul(self, a: int, b: int, /) -> int:
        return (a * b) % self.p

    def div(self, a: int, b: int, /) -> int:
        return moddiv(a, b, self.p)[0]


class CyclicGroup(Group[T]):
    @abstractmethod
    def order(self, /) -> int: ...

    @abstractmethod
    def check(self, a: T, /) -> bool: ...


ECCPoint = tuple[int, int] | None


class ECCGroup(CyclicGroup[ECCPoint]):
    def __init__(self, a: int, b: int, p: int, n: int):
        self.a = a
        self.b = b
        self.p = p
        self.n = n

    def check(self, P: ECCPoint, /) -> bool:
        return P is None or (P[0] * P[0] * P[0] - P[1] * P[1] + self.a * P[0] + self.b) % self.p == 0

    def order(self, /) -> int:
        return self.n

    def zero(self, /) -> ECCPoint:
        return None

    def neg(self, P: ECCPoint, /) -> ECCPoint:
        if P is None:
            return None
        return P[0], P[1] and self.p - P[1]

    def add(self, P: ECCPoint, Q: ECCPoint, /) -> ECCPoint:
        if Q is None:
            return P
        if P is None:
            return Q
        if P[0] == Q[0]:
            if (P[1] + Q[1]) % self.p == 0:
                return None
            tan = modinv(P[1] + Q[1], self.p) * (P[0] * Q[0] * 3 + self.a)
        else:
            tan = modinv(P[0] - Q[0], self.p) * (P[1] - Q[1])
        x = (tan * tan - P[0] - Q[0]) % self.p
        y = (tan * (P[0] - x) - P[1]) % self.p
        return x, y

    def sub(self, P: ECCPoint, Q: ECCPoint, /) -> ECCPoint:
        if Q is None:
            return P
        if P is None:
            return Q[0], Q[1] and self.p - Q[1]
        if P[0] == Q[0]:
            if P[1] == Q[1]:
                return None
            tan = modinv(P[1] - Q[1], self.p) * (P[0] * Q[0] * 3 + self.a)
        else:
            tan = modinv(P[0] - Q[0], self.p) * (Q[1] + P[1])
        x = (tan * tan - P[0] - Q[0]) % self.p
        y = (tan * (P[0] - x) - P[1]) % self.p
        return x, y


class UnitGroup(CyclicGroup[int]):
    def __init__(self, p: AnyPrime, k: int = 1, twice: bool = False):
        assert p != 2 and k >= 1 or p == 2 and k == 1
        self.p = p
        self.k = k
        self.m = p**k * (2 if twice else 1)
        self.n = p**k - p**k // k

    def check(self, a: int, /) -> bool:
        return a % self.p != 0

    def order(self, /) -> int:
        return self.n

    def zero(self, /) -> int:
        return 1

    def neg(self, a: int, /) -> int:
        return modinv(a, self.m)

    def add(self, a: int, b: int, /) -> int:
        return (a * b) % self.m

    def sub(self, a: int, b: int, /) -> int:
        return moddiv(a, b, self.m)[0]
