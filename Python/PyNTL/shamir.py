#!/usr/bin/env python3

import random

from pyntl import FiniteField, gen_prime, sample, polymap, lagrage_interpolation


def generate_shares(f: FiniteField, secret: int, k: int, n: int) -> list[tuple[int, int]]:
    coeffs = [secret]
    for _ in range(1, k - 1):
        coeffs.append(random.randrange(0, f.p))
    coeffs.append(random.randrange(1, f.p))  # leading coeff must be non-zero
    return [(x, polymap(f, coeffs, x)) for x in sample(1, f.p, n)]


def retrieve_secret(f: FiniteField, shares: list[tuple[int, int]]) -> int:
    return lagrage_interpolation(f, shares, 0)


def test():
    f = FiniteField(gen_prime(16))
    print("GF({})".format(f.p))
    K, N = 3, 5
    secret = random.randrange(0, f.p)
    print("secret:", secret)
    shares = generate_shares(f, secret, K, N)
    print("shares:", ", ".join("({}, {})".format(x, y) for x, y in shares))
    sample = random.sample(shares, K)
    print("sample:", ", ".join("({}, {})".format(x, y) for x, y in sample))
    secret = retrieve_secret(f, sample)
    print("secret:", secret)


if __name__ == "__main__":
    test()
