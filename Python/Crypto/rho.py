#!/usr/bin/python3
def get_rho(hash, seed):
    i = seed
    time = 1
    while True:
        t = i
        for r in range(1, time + 1):
            i = hash(i)
            if i == t:
                return r
        time <<= 1
def collide(hash, seed):
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
    x, y = collide(lambda data: (hash(data) % 2 ** 64).to_bytes(8, 'little'), (2 ** 64 - 1).to_bytes(8, 'little'))
    print(x.hex())
    print(y.hex())
if __name__ == '__main__':
    main()
