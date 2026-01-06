#!/usr/bin/env python3

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    # Basic types
    Iterable,
    # Strictness-related
    NewType,
    Literal,
    TypeGuard,
    # Generic programming-related
    Generic,
    TypeVar,
    overload,
)

from fractions import Fraction
import random
import sys


sys.setrecursionlimit(0x10000)


def sample(a: int, b: int, n: int) -> set[int]:
    """Generate n distinct random integers in [a, b).

    :param a: lower bound (inclusive)
    :type a: int
    :param b: upper bound (exclusive)
    :type b: int
    :param n: number of integers to generate
    :type n: int
    :return: a set of n distinct random integers in [a, b)
    :rtype: set[int]
    """
    res = set()
    while len(res) < n:
        res.add(random.randrange(a, b))
    return res


def choice(a: int, b: int, n: int) -> list[int]:
    """Generate n random integers in [a, b).

    :param a: lower bound (inclusive)
    :type a: int
    :param b: upper bound (exclusive)
    :type b: int
    :param n: number of integers to generate
    :type n: int
    :return: a list of n random integers in [a, b)
    :rtype: list[int]
    """
    res = []
    while len(res) < n:
        res.append(random.randrange(a, b))
    return res


def root(x: int, n: int) -> int:
    """Compute the integer n-th root of x.

    :param x: the number to compute the n-th root of
    :type x: int
    :param n: the degree of the root
    :type n: int
    :return: the integer n-th root of x
    :rtype: int
    """
    l, r = 0, x + 1
    while r - l > 1:
        m = (r + l) // 2
        if m**n > x:
            r = m
        else:
            l = m
    return l


OddPrime = NewType("OddPrime", int)
AnyPrime = OddPrime | Literal[2]


@overload
def is_prime(n: int, *, k: int = 16, require_odd: Literal[True]) -> TypeGuard[OddPrime]: ...


@overload
def is_prime(n: int, *, k: int = 16, require_odd: Literal[False] = False) -> TypeGuard[AnyPrime]: ...


def is_prime(n: int, *, k: int = 16, require_odd: bool = False) -> bool:
    """Check if n is a prime number using the Miller-Rabin primality test.

    :param n: the number to check for primality
    :type n: int
    :param k: the number of iterations for the test (default is 16)
    :type k: int
    :param require_odd: whether to require n to be odd (default is False)
    :type require_odd: bool
    :return: True if n is probably prime, False otherwise
    :rtype: bool
    """
    if n == 2:
        return not require_odd
    if n < 2 or n % 2 == 0:
        return False
    s, t = n - 1, 0
    while s % 2 == 0:
        s, t = s // 2, t + 1
    for _ in range(k):
        a = random.randrange(1, n)
        x = pow(a, s, n)
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
def gen_prime(w: int, *, k: int = 16, require_odd: Literal[True]) -> OddPrime: ...


@overload
def gen_prime(w: int, *, k: int = 16, require_odd: Literal[False] = False) -> AnyPrime: ...


def gen_prime(w: int, *, k: int = 16, require_odd: bool = False) -> int:
    """Generate a random prime number with a bit length of w.

    :param w: the bit length of the prime number
    :type w: int
    :param k: the number of iterations for the primality test (default is 16)
    :type k: int
    :param require_odd: whether to require the prime number to be odd (default is False)
    :type require_odd: bool
    :return: a random prime number with a bit length of w
    :rtype: int
    """
    while True:
        n = random.randrange(1 << w - 1, 1 << w)
        if is_prime(n, k=k, require_odd=require_odd):
            return n


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)


@dataclass
class Factorization:
    data: dict[AnyPrime, int]

    @property
    def phi(self) -> int:
        """Compute Euler's totient function φ(n) where n's prime factorization is self."""
        F = 1
        for p, k in self.data.items():
            if k == 0:
                continue
            f = p**k - p**k // p
            F = F * f
        return F

    @property
    def lam(self) -> int:
        """Compute Carmichael's function λ(n) where n's prime factorization is self."""
        L = 1
        for p, k in self.data.items():
            if k == 0:
                continue
            l = 2 ** (k - 2) if p == 2 and k >= 3 else p**k - p**k // p
            L = lcm(L, l)
        return L

    @property
    def num(self) -> int:
        """Compute the number n where n's prime factorization is self."""
        N = 1
        for p, k in self.data.items():
            if k == 0:
                continue
            n = p**k
            N *= n
        return N


def binsqrt(k: int, x: int) -> int:
    """Square root modulo 2^k.

    :param k: the exponent of 2
    :type k: int
    :param x: the number to compute the square root of
    :type x: int
    :return: y such that y^2 == x (mod 2^k)
    :rtype: int
    """
    assert k >= 3
    assert x % 8 == 1
    a = 1
    for i in range(2, k - 1):
        if (a * a - x) % 2 ** (i + 2) != 0:
            a = a + 2**i
    return a


def binroot(k: int, t: int, x: int) -> tuple[tuple[int, int], int]:
    """2^t-th root modulo 2^k.

    :param k: the exponent of 2
    :type k: int
    :param t: the exponent of 2 in the degree of the root
    :type t: int
    :param x: the number to compute the 2^t-th root of
    :type x: int
    :return: (a, b), c such that y^2^t == x (mod 2^k) if and only if y == a or b (mod c)
    :rtype: tuple[tuple[int, int], int]
    """
    assert k >= t + 2 >= 3
    assert x % 2 ** (t + 2) == 1
    for i in range(t):
        x = binsqrt(k - i, x)
    c = 2 ** (k - t)
    return (x, c - x), c


def ammroot(p: OddPrime, k: int, r: AnyPrime, x: int) -> int:
    """Compute the r-th root modulo p^k.

    :param p: an odd prime
    :type p: OddPrime
    :param k: the exponent of p
    :type k: int
    :param r: a prime divisor of φ(p^k)
    :type r: int
    :param x: the number to compute the r-th root of
    :type x: int
    :return: h such that h^r == x (mod p^k)
    :rtype: int
    """
    q, f = p**k, p**k - p**k // p
    assert f % r == 0
    assert pow(x, f // r, q) == 1
    for z in range(2, p):
        if pow(z, f // r, q) != 1:
            break
    s, t = f, 0
    while s % r == 0:
        s, t = s // r, t + 1
    v = pow(r, -1, s)
    S = v * r - 1
    h = pow(x, v, q)
    a = pow(z, s, q)
    b = pow(x, S, q)
    c = pow(a, r ** (t - 1), q)
    for i in range(1, t):
        d = pow(b, r ** (t - 1 - i), q)
        j, e = 0, 1
        while d != e:
            j, e = j - 1, e * c % q
        h = pow(a, j, q) * h % q
        a = pow(a, r, q)
        b = pow(a, j, q) * b % q
    return h


def generator(p: OddPrime, k: int, n: Factorization) -> int:
    """Compute a generator of the cyclic group of order n modulo p^k.

    :param p: an odd prime
    :type p: OddPrime
    :param k: the exponent of p
    :type k: int
    :param n: the factorization of the order of the cyclic group
    :type n: Factorization
    :return: a generator of the cyclic group of order n modulo p^k
    :rtype: int
    """
    q, f = p**k, p**k - p**k // p
    g = 1
    for r, a in n.data.items():
        if a == 0:
            continue
        for z in range(2, p):
            if pow(z, f // r, q) != 1:
                break
        g = pow(z, f // r**a, q) * g % q
    return g


#######################
# Algebraic Structure #
#######################


T = TypeVar("T")


class AlgebraicStructure(Generic[T], ABC):
    @abstractmethod
    def eq(self, a: T, b: T, /) -> bool: ...


class Monoid(AlgebraicStructure[T], ABC):
    @abstractmethod
    def zero(self, /) -> T: ...
    @abstractmethod
    def add(self, a: T, b: T, /) -> T: ...

    def lsum(self, args: Iterable[T]) -> T:
        r = self.zero()
        for a in args:
            r = self.add(r, a)
        return r

    def rsum(self, args: Iterable[T]) -> T:
        r = self.zero()
        for a in args:
            r = self.add(a, r)
        return r

    def dot(self, a: T, n: int, /) -> T:
        r = self.zero()
        while n:
            if n % 2 == 1:
                r = self.add(r, a)
            a = self.add(a, a)
            n = n // 2
        return r


class Group(Monoid[T], ABC):
    @abstractmethod
    def neg(self, a: T, /) -> T: ...

    def lsub(self, a: T, b: T, /) -> T:
        return self.add(self.neg(b), a)

    def rsub(self, a: T, b: T, /) -> T:
        return self.add(a, self.neg(b))


class AbelianGroup(Group[T], ABC):
    @abstractmethod
    def sub(self, a: T, b: T, /) -> T: ...


class Ring(AbelianGroup[T], ABC):
    @abstractmethod
    def one(self, /) -> T: ...
    @abstractmethod
    def mul(self, a: T, b: T, /) -> T: ...

    def lprod(self, args: Iterable[T]) -> T:
        r = self.one()
        for a in args:
            r = self.mul(r, a)
        return r

    def rprod(self, args: Iterable[T]) -> T:
        r = self.one()
        for a in args:
            r = self.mul(a, r)
        return r

    def pow(self, a: T, n: int, /) -> T:
        r = self.one()
        while n:
            if n % 2 == 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            n = n // 2
        return r


class DivisionRing(Ring[T], ABC):
    @abstractmethod
    def inv(self, a: T, /) -> T: ...

    def ldiv(self, a: T, b: T, /) -> T:
        return self.mul(self.inv(b), a)

    def rdiv(self, a: T, b: T, /) -> T:
        return self.mul(a, self.inv(b))


class Field(DivisionRing[T], ABC):
    @abstractmethod
    def div(self, a: T, b: T, /) -> T: ...


Matrix = list[list[T]]  # m * n matrix


def matzero(f: Monoid[T], h: int, w: int) -> Matrix[T]:
    return [[f.zero() for _ in range(w)] for _ in range(h)]


def matneg(f: Group[T], a: Matrix[T], h: int, w: int) -> Matrix[T]:
    return [[f.neg(a[i][j]) for j in range(w)] for i in range(h)]


def matadd(f: AbelianGroup[T], a: Matrix[T], b: Matrix[T], h: int, w: int) -> Matrix[T]:
    return [[f.add(a[i][j], b[i][j]) for j in range(w)] for i in range(h)]


def matsub(f: AbelianGroup[T], a: Matrix[T], b: Matrix[T], h: int, w: int) -> Matrix[T]:
    return [[f.sub(a[i][j], b[i][j]) for j in range(w)] for i in range(h)]


def mateye(f: Ring[T], r: int) -> Matrix[T]:
    return [[f.one() if i == j else f.zero() for j in range(r)] for i in range(r)]


def matmul(f: Ring[T], a: Matrix[T], b: Matrix[T], h: int, m: int, w: int) -> Matrix[T]:
    res = [[f.zero() for _ in range(w)] for _ in range(h)]
    for i in range(h):
        for j in range(w):
            for k in range(m):
                res[i][j] = f.add(res[i][j], f.mul(a[i][k], b[k][j]))
    return res


def rref(f: Field[T], m: Matrix[T], h: int, w: int) -> Matrix:
    m = [[m[i][j] for j in range(w)] for i in range(h)]
    for J in range(w):
        I = next((I for I in range(h) if all(f.eq(m[I][j], f.zero()) for j in range(J)) and not f.eq(m[I][J], f.zero())), None)
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
    e = mateye(f, r)
    m = [m[i] + e[i] for i in range(r)]
    m = rref(f, m, r, r * 2)
    s = [next((i, f.inv(m[i][j])) for i in range(r) if m[i][j] != 0) for j in range(r)]
    return [[f.mul(x, t) for x in m[i][r:]] for i, t in s]


Polynomial = list[T]  # coefficients list


def polyneg(f: Group[T], a: Polynomial[T]) -> Polynomial[T]:
    return [f.neg(c) for c in a]


def polyadd(f: AbelianGroup[T], a: Polynomial[T], b: Polynomial[T]) -> Polynomial[T]:
    n = max(len(a), len(b))
    a = a + [f.zero() for _ in range(n - len(a))]
    b = b + [f.zero() for _ in range(n - len(b))]
    return [f.add(a[i], b[i]) for i in range(n)]


def polysub(f: AbelianGroup[T], a: Polynomial[T], b: Polynomial[T]) -> Polynomial[T]:
    n = max(len(a), len(b))
    a = a + [f.zero() for _ in range(n - len(a))]
    b = b + [f.zero() for _ in range(n - len(b))]
    return [f.sub(a[i], b[i]) for i in range(n)]


def polymul(f: Ring[T], a: Polynomial[T], b: Polynomial[T]) -> Polynomial[T]:
    res = [f.zero()] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            res[i + j] = f.add(res[i + j], f.mul(a[i], b[j]))
    return res


def polydivmod(f: Field[T], a: Polynomial[T], b: Polynomial[T]) -> tuple[Polynomial[T], Polynomial[T]]:
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


def polymap(f: Ring[T], coeffs: Polynomial[T], x: T) -> T:
    r = f.zero()
    for i, c in enumerate(coeffs):
        r = f.add(r, f.mul(c, f.pow(x, i)))
    return r


def lagrange_polynomial(f: Field[T], points: list[tuple[T, T]]) -> Polynomial[T]:
    """Compute the coefficients of the Lagrange interpolation polynomial.

    :param f: the field
    :type f: Field[T]
    :param points: n points, each of which is a pair of x and y
    :type points: list[tuple[T, T]]
    :return: coefficients list of the n - 1 degree polynomial that passes through all the points
    :rtype: Polynomial[T]
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


def lagrage_interpolation(f: Field[T], points: list[tuple[T, T]], t: T) -> T:
    """Compute the value of the Lagrange interpolation polynomial at t.

    :param f: the field
    :type f: Field[T]
    :param points: n points, each of which is a pair of x and y
    :type points: list[tuple[T, T]]
    :param t: the point to evaluate the polynomial at
    :type t: T
    :return: the value of the polynomial at t
    :rtype: T
    """
    for x, y in points:
        if f.eq(x, t):
            return y
    Z = f.one()
    for x, y in points:
        Z = f.mul(Z, f.sub(t, x))
    Y = f.zero()
    for j, (x, y) in enumerate(points):
        d = f.one()
        for m, (u, v) in enumerate(points):
            if m != j:
                d = f.mul(d, f.sub(x, u))
        k = f.div(y, d)
        r = f.inv(f.sub(t, x))
        Y = f.add(Y, f.mul(k, r))
    return f.mul(Y, Z)


class FiniteField(Field[int]):
    def __init__(self, p: AnyPrime):
        self.p = p

    def eq(self, a: int, b: int, /) -> bool:
        return a % self.p == b % self.p

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
        return pow(a, -1, self.p)

    def mul(self, a: int, b: int, /) -> int:
        return (a * b) % self.p

    def div(self, a: int, b: int, /) -> int:
        return pow(b, -1, self.p) * a % self.p


class RationalField(Field[Fraction]):
    def eq(self, a: Fraction, b: Fraction, /) -> bool:
        return a == b

    def zero(self, /) -> Fraction:
        return Fraction(0)

    def neg(self, a: Fraction, /) -> Fraction:
        return -a

    def add(self, a: Fraction, b: Fraction, /) -> Fraction:
        return a + b

    def sub(self, a: Fraction, b: Fraction, /) -> Fraction:
        return a - b

    def one(self, /) -> Fraction:
        return Fraction(1)

    def inv(self, a: Fraction, /) -> Fraction:
        return 1 / a

    def mul(self, a: Fraction, b: Fraction, /) -> Fraction:
        return a * b

    def div(self, a: Fraction, b: Fraction, /) -> Fraction:
        return a / b


class RealField(Field[float]):
    def eq(self, a: float, b: float, /) -> bool:
        return a == b

    def zero(self, /) -> float:
        return 0.0

    def neg(self, a: float, /) -> float:
        return -a

    def add(self, a: float, b: float, /) -> float:
        return a + b

    def sub(self, a: float, b: float, /) -> float:
        return a - b

    def one(self, /) -> float:
        return 1.0

    def inv(self, a: float, /) -> float:
        return 1.0 / a

    def mul(self, a: float, b: float, /) -> float:
        return a * b

    def div(self, a: float, b: float, /) -> float:
        return a / b


class ComplexField(Field[complex]):
    def eq(self, a: complex, b: complex, /) -> bool:
        return a == b

    def zero(self, /) -> complex:
        return 0.0 + 0.0j

    def neg(self, a: complex, /) -> complex:
        return -a

    def add(self, a: complex, b: complex, /) -> complex:
        return a + b

    def sub(self, a: complex, b: complex, /) -> complex:
        return a - b

    def one(self, /) -> complex:
        return 1.0 + 0.0j

    def inv(self, a: complex, /) -> complex:
        return 1.0 / a

    def mul(self, a: complex, b: complex, /) -> complex:
        return a * b

    def div(self, a: complex, b: complex, /) -> complex:
        return a / b


class MatrixRing(DivisionRing[Matrix[T]]):
    def __init__(self, base: Field[T], r: int):
        self.base = base
        self.r = r

    def eq(self, a: Matrix[T], b: Matrix[T], /) -> bool:
        for i in range(self.r):
            for j in range(self.r):
                if not self.base.eq(a[i][j], b[i][j]):
                    return False
        return True

    def zero(self, /) -> Matrix[T]:
        return matzero(self.base, self.r, self.r)

    def neg(self, a: Matrix[T], /) -> Matrix[T]:
        return matneg(self.base, a, self.r, self.r)

    def add(self, a: Matrix[T], b: Matrix[T], /) -> Matrix[T]:
        return matadd(self.base, a, b, self.r, self.r)

    def sub(self, a: Matrix[T], b: Matrix[T], /) -> Matrix[T]:
        return matsub(self.base, a, b, self.r, self.r)

    def one(self, /) -> Matrix[T]:
        return mateye(self.base, self.r)

    def mul(self, a: Matrix[T], b: Matrix[T], /) -> Matrix[T]:
        return matmul(self.base, a, b, self.r, self.r, self.r)

    def inv(self, a: Matrix[T], /) -> Matrix[T]:
        return matinv(self.base, a, self.r)


####################
# Euclidean Domain #
####################


Remainder = tuple[T, T]  # (remainder, modulus)
DivisionResult = tuple[T, T]  # (quotient, remainder)


class EuclideanDomain(Ring[T], ABC):
    @abstractmethod
    def divmod(self, a: T, b: T, /) -> DivisionResult[T]: ...

    def div(self, a: T, b: T, /) -> T:
        q, _ = self.divmod(a, b)
        return q

    def mod(self, a: T, b: T, /) -> T:
        _, r = self.divmod(a, b)
        return r

    def modpow(self, a: T, n: int, m: T, /) -> T:
        r = self.one()
        while n:
            if n % 2 == 1:
                r = self.mod(self.mul(r, a), m)
            a = self.mod(self.mul(a, a), m)
            n = n // 2
        return r

    def exgcd(self, a: T, b: T, /) -> tuple[T, tuple[T, T]]:
        if self.eq(b, self.zero()):
            return a, (self.one(), self.zero())
        q, r = self.divmod(a, b)
        d, (x, y) = self.exgcd(b, r)
        return d, (y, self.sub(x, self.mul(q, y)))

    def modinv(self, a: T, m: T, /) -> T:
        d, (x, _) = self.exgcd(a, m)
        if d != self.one():
            raise ZeroDivisionError
        return x

    def moddiv(self, a: T, b: T, m: T, /) -> Remainder[T]:
        d, (x, _) = self.exgcd(b, m)
        q, r = self.divmod(a, d)
        if r != self.zero():
            raise ZeroDivisionError
        k = self.mul(q, x)
        n = self.div(m, d)
        return k, n

    def crt(self, *D: Remainder[T]) -> Remainder[T]:
        R, M = self.zero(), self.one()
        for r, m in D:
            d, (N, _) = self.exgcd(M, m)
            c = self.sub(r, R)
            q, t = self.divmod(c, d)
            if t != self.zero():
                raise ZeroDivisionError
            R = self.add(R, self.mul(self.mul(N, M), q))
            M = self.mul(M, self.div(m, d))
        return self.mod(R, M), M


class IntegerRing(EuclideanDomain[int]):
    def eq(self, a: int, b: int, /) -> bool:
        return a == b

    def zero(self, /) -> int:
        return 0

    def neg(self, a: int, /) -> int:
        return -a

    def add(self, a: int, b: int, /) -> int:
        return a + b

    def sub(self, a: int, b: int, /) -> int:
        return a - b

    def one(self, /) -> int:
        return 1

    def mul(self, a: int, b: int, /) -> int:
        return a * b

    def divmod(self, a: int, b: int, /) -> DivisionResult[int]:
        return divmod(a, b)


class PolynomialRing(EuclideanDomain[Polynomial[T]]):
    def eq(self, a: Polynomial[T], b: Polynomial[T], /) -> bool:
        n = max(len(a), len(b))
        a = a + [self.base.zero() for _ in range(n - len(a))]
        b = b + [self.base.zero() for _ in range(n - len(b))]
        for i in range(n):
            if not self.base.eq(a[i], b[i]):
                return False
        return True

    def __init__(self, base: Field[T]):
        self.base = base

    def zero(self, /) -> Polynomial[T]:
        return []

    def neg(self, a: Polynomial[T], /) -> Polynomial[T]:
        return polyneg(self.base, a)

    def add(self, a: Polynomial[T], b: Polynomial[T], /) -> Polynomial[T]:
        return polyadd(self.base, a, b)

    def sub(self, a: Polynomial[T], b: Polynomial[T], /) -> Polynomial[T]:
        return polysub(self.base, a, b)

    def one(self, /) -> Polynomial[T]:
        return [self.base.one()]

    def mul(self, a: Polynomial[T], b: Polynomial[T], /) -> Polynomial[T]:
        return polymul(self.base, a, b)

    def divmod(self, a: Polynomial[T], b: Polynomial[T], /) -> DivisionResult[Polynomial[T]]:
        return polydivmod(self.base, a, b)


################
# Finite group #
################


class FiniteGroup(AbelianGroup[T], ABC):
    @abstractmethod
    def order(self, a: T, /) -> int: ...
    @abstractmethod
    def check(self, a: T, /) -> bool: ...

    def div(self, a: T, n: int, /) -> T:
        return self.dot(a, pow(n, -1, self.order(a)))


ECCPoint = tuple[int, int] | None


class ECCGroup(FiniteGroup[ECCPoint]):
    def __init__(self, a: int, b: int, p: int, n: int):
        self.a = a
        self.b = b
        self.p = p
        self.n = n

    def check(self, P: ECCPoint, /) -> bool:
        return P is None or (P[0] * P[0] * P[0] - P[1] * P[1] + self.a * P[0] + self.b) % self.p == 0

    def order(self, P: ECCPoint, /) -> int:
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
        if (P[0] - Q[0]) % self.p == 0:
            if (P[1] + Q[1]) % self.p == 0:
                return None
            tan = pow(P[1] + Q[1], -1, self.p) * (P[0] * Q[0] * 3 + self.a)
        else:
            tan = pow(P[0] - Q[0], -1, self.p) * (P[1] - Q[1])
        x = (tan * tan - P[0] - Q[0]) % self.p
        y = (tan * (P[0] - x) - P[1]) % self.p
        return x, y

    def sub(self, P: ECCPoint, Q: ECCPoint, /) -> ECCPoint:
        if Q is None:
            return P
        if P is None:
            return Q[0], Q[1] and self.p - Q[1]
        if (P[0] - Q[0]) % self.p == 0:
            if (P[1] - Q[1]) % self.p == 0:
                return None
            tan = pow(P[1] - Q[1], -1, self.p) * (P[0] * Q[0] * 3 + self.a)
        else:
            tan = pow(P[0] - Q[0], -1, self.p) * (P[1] + Q[1])
        x = (tan * tan - P[0] - Q[0]) % self.p
        y = (tan * (P[0] - x) - P[1]) % self.p
        return x, y


class UnitGroup(FiniteGroup[int]):
    def __init__(self, p: AnyPrime, k: int = 1, double: bool = False):
        assert p != 2 and k >= 1 or p == 2 and k == 1
        self.p = p
        self.k = k
        self.m = p**k * (2 if double else 1)
        self.n = p**k - p**k // k

    def check(self, a: int, /) -> bool:
        return a % self.p != 0

    def order(self, a: int, /) -> int:
        return self.n

    def zero(self, /) -> int:
        return 1

    def neg(self, a: int, /) -> int:
        return pow(a, -1, self.m)

    def add(self, a: int, b: int, /) -> int:
        return (a * b) % self.m

    def sub(self, a: int, b: int, /) -> int:
        return pow(b, -1, self.m) * a % self.m


if __name__ == "__main__":
    p = gen_prime(16)
    F = FiniteField(p)
    P = PolynomialRing(F)

    k_len = 5
    a_len = 5
    b_len = 5

    k = [*(random.randrange(0, p) for _ in range(k_len)), random.randrange(1, p)]

    while True:
        a = [*(random.randrange(0, p) for _ in range(a_len)), random.randrange(1, p)]
        b = [*(random.randrange(0, p) for _ in range(b_len)), random.randrange(1, p)]
        d, (x, y) = P.exgcd(a, b)
        assert P.eq(P.add(P.mul(x, a), P.mul(y, b)), d)
        if P.eq(d, P.one()):
            break

    A = P.mul(k, a)
    B = P.mul(k, b)
    D, (X, Y) = P.exgcd(A, B)
    assert P.eq(P.add(P.mul(X, A), P.mul(Y, B)), D)
    assert P.eq(D, k)
