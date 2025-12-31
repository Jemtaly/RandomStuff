#!/usr/bin/env python3

import random

from pyntl import FiniteField, genprime, sample, polyval, recover


def genshares(f: FiniteField, secret: int, k: int, n: int) -> list[tuple[int, int]]:
    coeffs = [secret]
    for _ in range(1, k - 1):
        coeffs.append(random.randrange(0, f.p))
    coeffs.append(random.randrange(1, f.p))  # leading coeff must be non-zero
    return [(x, polyval(f, coeffs, x)) for x in sample(1, f.p, n)]


def recsecret(f: FiniteField, shares: list[tuple[int, int]]) -> int:
    return recover(f, shares, 0)


def test():
    f = FiniteField(genprime(16))
    print("GF({})".format(f.p))
    K, N = 3, 5
    secret = random.randrange(0, f.p)
    print("secret:", secret)
    shares = genshares(f, secret, K, N)
    print("shares:", ", ".join("({}, {})".format(x, y) for x, y in shares))
    sample = random.sample(shares, K)
    print("sample:", ", ".join("({}, {})".format(x, y) for x, y in sample))
    recons = recsecret(f, sample)
    print("recons:", recons)


if __name__ == "__main__":
    test()
