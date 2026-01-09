#!/usr/bin/env python3

from typing import Callable

import sys


def get_rho(hash: Callable[[bytes], bytes], seed: bytes) -> int:
    i = seed
    time = 1
    while True:
        t = i
        for r in range(1, time + 1):
            i = hash(i)
            if i == t:
                return r
        time <<= 1


def collide(hash: Callable[[bytes], bytes], seed: bytes) -> tuple[bytes, bytes]:
    x = seed
    y = seed
    r = get_rho(hash, seed)
    for _ in range(r):
        y = hash(y)
    while True:
        m = hash(x)
        n = hash(y)
        if m == n:
            return x, y
        x, y = m, n


def main():
    hlen = sys.hash_info.width // 8
    x, y = collide(lambda data: hash(data).to_bytes(hlen, "little", signed=True), hash(None).to_bytes(hlen, "little", signed=True))
    print(x.hex())
    print(y.hex())


if __name__ == "__main__":
    main()
