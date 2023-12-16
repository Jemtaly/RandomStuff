#!/usr/bin/python3
import util
import random
Q = util.genPrime(16)
def poly(ns):
    Z = [1]
    for n in ns:
        Z = [(v - n * u) % Q for u, v in zip(Z + [0], [0] + Z)]
    return Z
def gen(R1CS, ns):
    return [util.lagrange(list(zip(ns, ys)), Q) for ys in zip(*R1CS)]
def dot(Poly, s):
    return [sum(i * j for i, j in zip(u, s)) % Q for u in zip(*Poly)]
def compile(f):
    eqs = []
    ids = iter(range(0, 1 << 16))
    def reg(name):
        i = next(ids)
        return i
    def mul(a, b, d = 1):
        i = next(ids)
        eqs.append((i, a, b, d))
        return i
    f(reg, mul)
    gates = []
    for i, a, b, d in eqs:
        gate = [[0 for _ in range(next(ids))] for _ in range(3)]
        for j, n in a:
            gate[0][j] += n
        for j, n in b:
            gate[1][j] += n
        gate[2][i] = d
        gates.append(gate)
    return gates
def witness(f, **kwargs):
    s = []
    ids = iter(range(0, 1 << 16))
    def reg(name):
        i = next(ids)
        s.append(kwargs[name])
        return i
    def mul(a, b, d = 1):
        i = next(ids)
        A = sum(s[i] * n for i, n in a)
        B = sum(s[i] * n for i, n in b)
        s.append(A * B * util.modinv(d, Q) % Q)
        return i
    f(reg, mul)
    return s
if __name__ == '__main__':
    print('GF({})'.format(Q))
    def fibonacci(reg, mul):
        U = reg('u')
        X = reg('x')
        Y = mul([(X, 1)], [(X, 1)])
        Z = mul([(Y, 1)], [(X, 1)])
        O = mul([(Z, 1), (X, 1), (U, 5)], [(U, 1)])
    # Compile
    gates = compile(fibonacci)
    A, B, C = zip(*gates)
    ns = list(util.choice(0, Q, len(gates)))
    A = gen(A, ns)
    B = gen(B, ns)
    C = gen(C, ns)
    Z = poly(ns)
    print('Z =', Z)
    # Prove
    s = witness(fibonacci, u = 1, x = 3)
    print('s =', s)
    a = dot(A, s)
    b = dot(B, s)
    c = dot(C, s)
    t = util.polysub(util.polymul(a, b, Q), c, Q)
    print('A . s =', a)
    print('B . s =', b)
    print('C . s =', c)
    print('t =', t)
    H, r = util.polydm(t, Z, Q)
    print('H =', H)
    print('r =', r)
