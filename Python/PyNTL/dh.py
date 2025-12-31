import random

from typing import TypeVar, Generic

from pyntl import CyclicGroup, ECCGroup, ECCPoint


T = TypeVar("T")


class DiffieHellman(Generic[T]):
    def __init__(self, group: CyclicGroup[T], generator: T) -> None:
        self._group = group
        self._gen = generator

    def gen_sec_key(self) -> int:
        return random.randrange(1, self._group.order())

    def gen_pub_key(self, sec_key: int) -> T:
        return self._group.dot(self._gen, sec_key)

    def gen_shared_key(self, pub_key: T, sec_key: int) -> T:
        return self._group.dot(pub_key, sec_key)


def test_diffie_hellman(dh: DiffieHellman[T]) -> None:
    # Alice
    a_sec = dh.gen_sec_key()
    a_pub = dh.gen_pub_key(a_sec)
    # Bob
    b_sec = dh.gen_sec_key()
    b_pub = dh.gen_pub_key(b_sec)
    # Shared Key
    a_shared = dh.gen_shared_key(b_pub, a_sec)
    b_shared = dh.gen_shared_key(a_pub, b_sec)
    assert a_shared == b_shared


# Public Parameters (secp256k1)
A = 0x0000000000000000000000000000000000000000000000000000000000000000
B = 0x0000000000000000000000000000000000000000000000000000000000000007
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G: ECCPoint = (X, Y)
F: ECCGroup = ECCGroup(A, B, P, N)


def test():
    test_diffie_hellman(DiffieHellman(F, G))


if __name__ == "__main__":
    test()
