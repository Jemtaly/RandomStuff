import random

from typing import TypeVar

from pyntl import CyclicGroup, ECCGroup, ECCPoint


T = TypeVar("T")


def gen_key_pair(context: CyclicGroup[T]) -> tuple[int, CyclicGroup[T]]:
    secret_key = random.randrange(1, context.order)
    public_key = context.subgroup(secret_key)
    return secret_key, public_key


def gen_shared_key(secret_key: int, public_key: CyclicGroup[T]) -> CyclicGroup[T]:
    return public_key.subgroup(secret_key)


def test_diffie_hellman(context: CyclicGroup[T]) -> None:
    # Alice
    a_secret_key, a_public_key = gen_key_pair(context)
    # Bob
    b_secret_key, b_public_key = gen_key_pair(context)
    # Shared Key
    a_shared_key = gen_shared_key(a_secret_key, b_public_key)
    b_shared_key = gen_shared_key(b_secret_key, a_public_key)
    assert a_shared_key == b_shared_key


# Public Parameters (secp256k1)
A = 0x0000000000000000000000000000000000000000000000000000000000000000
B = 0x0000000000000000000000000000000000000000000000000000000000000007
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
F: ECCGroup = ECCGroup(A, B, P)
X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G: ECCPoint = (X, Y)
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP256K1 = CyclicGroup(F, G, N)


def test():
    test_diffie_hellman(SECP256K1)


if __name__ == "__main__":
    test()
