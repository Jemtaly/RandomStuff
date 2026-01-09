#!/usr/bin/env python3

import random

from pyntl import gen_prime


class RSAPublicKey:
    def __init__(self, n: int, e: int) -> None:
        self.n = n
        self.e = e

    def encrypt(self, x: int) -> int:
        return pow(x, self.e, self.n)


class RSASecretKey:
    def __init__(self, n: int, e: int, d: int) -> None:
        self.n = n
        self.d = d
        self.e = e

    def decrypt(self, x: int) -> int:
        return pow(x, self.d, self.n)

    def encrypt(self, x: int) -> int:
        return pow(x, self.e, self.n)

    def gen_public_key(self) -> RSAPublicKey:
        return RSAPublicKey(self.n, self.e)


class RSASecretKeyAccelerated(RSASecretKey):
    def __init__(self, n: int, e: int, d: int, p: int, q: int) -> None:
        super().__init__(n, e, d)
        self.p = p
        self.q = q
        # CRT optimization parameters
        self.invP = p * pow(p, -1, q)
        self.invQ = q * pow(q, -1, p)
        self.dP = d % (p - 1)
        self.dQ = d % (q - 1)
        self.eP = e % (p - 1)
        self.eQ = e % (q - 1)

    def decrypt(self, x: int) -> int:
        m = pow(x % self.p, self.dP, self.p)
        n = pow(x % self.q, self.dQ, self.q)
        return (m * self.invQ + n * self.invP) % self.n

    def encrypt(self, x: int) -> int:
        m = pow(x % self.p, self.eP, self.p)
        n = pow(x % self.q, self.eQ, self.q)
        return (m * self.invQ + n * self.invP) % self.n


def generate_rsa_secret_key(bit_length: int = 2048) -> RSASecretKeyAccelerated:
    p = gen_prime(bit_length // 2)
    q = gen_prime(bit_length // 2)
    n = p * q
    phi = (p - 1) * (q - 1)
    while True:
        e = random.randrange(2, phi)
        try:
            d = pow(e, -1, phi)
            break
        except ZeroDivisionError:
            pass
    return RSASecretKeyAccelerated(n, e, d, p, q)


def test():
    sk = generate_rsa_secret_key()
    pk = sk.gen_public_key()

    # sign and verify
    m = random.randrange(sk.n)
    s = sk.decrypt(m)  # signature
    v = pk.encrypt(s)  # verification
    assert m == v

    # encrypt and decrypt
    m = random.randrange(pk.n)
    c = pk.encrypt(m)  # encryption
    p = sk.decrypt(c)  # decryption
    assert m == p

    # 1-out-of-n oblivious transfer
    n = 10
    M = [random.randrange(sk.n) for _ in range(n)]  # secret messages
    X = [random.randrange(sk.n) for _ in range(n)]  # random messages
    b = random.randrange(n)  # secret choice
    k = random.randrange(pk.n)  # random key
    q = (X[b] + pk.encrypt(k)) % pk.n  # blinded query
    N = [(sk.decrypt(q - x) + m) % sk.n for x, m in zip(X, M)]  # responses
    m = (N[b] - k) % pk.n  # decryption
    assert m == M[b]


if __name__ == "__main__":
    test()
