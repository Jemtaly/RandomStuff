#!/usr/bin/python3
import util
Q = util.genPrime(16)
def poly(ns):
    Z = [1]
    for n in ns:
        Z = [v - n * u for u, v in zip(Z + [0], [0] + Z)]
    return Z
def gen(R1CS, ns):
    return [util.lagrange(list(zip(ns, ys)), Q) for ys in zip(*R1CS)]
def dot(Poly, s):
    return [sum(i * j for i, j in zip(u, s)) % Q for u in zip(*Poly)]
# o = x * x * x + x + 5
def witness(x):
    y = x * x
    z = y * x
    w = z + x
    o = w + 5
    return [1, x, o, y, z, w]
gates = [
    [
        [0, 1, 0, 0, 0, 0], # x
        [0, 1, 0, 0, 0, 0], # x
        [0, 0, 0, 1, 0, 0], # y
    ],
    [
        [0, 0, 0, 1, 0, 0], # y
        [0, 1, 0, 0, 0, 0], # x
        [0, 0, 0, 0, 1, 0], # z
    ],
    [
        [0, 1, 0, 0, 1, 0], # x + z
        [1, 0, 0, 0, 0, 0], # 1
        [0, 0, 0, 0, 0, 1], # w
    ],
    [
        [5, 0, 0, 0, 0, 1], # 5 + w
        [1, 0, 0, 0, 0, 0], # 1
        [0, 0, 1, 0, 0, 0], # o
    ],
]
if __name__ == '__main__':
    print('GF({})'.format(Q))
    ns = [1, 2, 3, 4]
    s = witness(3)
    Z = poly(ns)
    A, B, C = zip(*gates)
    As = dot(gen(A, ns), s)
    Bs = dot(gen(B, ns), s)
    Cs = dot(gen(C, ns), s)
    t = util.polysub(util.polymul(As, Bs, Q), Cs, Q)
    print('Z =', Z)
    print('A . s =', As)
    print('B . s =', Bs)
    print('C . s =', Cs)
    print('t =', t)
    H, r = util.polydm(t, Z, Q)
    print('H =', H)
    print('r =', r)
