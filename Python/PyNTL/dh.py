import random

from typing import TypeVar, Generic

from pyntl import CyclicTorsionGroup, ECCGroup, ECCPoint


T = TypeVar("T")


class DiffieHellmanFactory(Generic[T]):
    def __init__(self, group: CyclicTorsionGroup[T]) -> None:
        self._group = group
        self._generator = group.generator()

    def gen_secret_key(self) -> int:
        return random.randrange(1, self._group.order())

    def gen_public_key(self, secret_key: int) -> T:
        return self._group.dot(self._generator, secret_key)

    def gen_shared_key(self, secret_key: int, public_key: T) -> T:
        return self._group.dot(public_key, secret_key)


def test_diffie_hellman(factory: DiffieHellmanFactory[T]) -> None:
    # Alice
    a_secret_key = factory.gen_secret_key()
    a_public_key = factory.gen_public_key(a_secret_key)
    # Bob
    b_secret_key = factory.gen_secret_key()
    b_public_key = factory.gen_public_key(b_secret_key)
    # Shared Key
    a_shared_key = factory.gen_shared_key(a_secret_key, b_public_key)
    b_shared_key = factory.gen_shared_key(b_secret_key, a_public_key)
    assert a_shared_key == b_shared_key


# Public Parameters (secp256k1)
A = 0x0000000000000000000000000000000000000000000000000000000000000000
B = 0x0000000000000000000000000000000000000000000000000000000000000007
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G: ECCPoint = (X, Y)
F: ECCGroup = ECCGroup(A, B, P, N, G)
SECP256K1 = DiffieHellmanFactory(F)


def test():
    test_diffie_hellman(SECP256K1)


if __name__ == "__main__":
    test()
