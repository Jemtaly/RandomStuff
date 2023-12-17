#!/usr/bin/python3
import util
import time
Q = util.genPrime(16)
def poly(ns):
    Z = [1]
    for n in ns:
        Z = [(v - n * u) % Q for u, v in zip(Z + [0], [0] + Z)]
    return Z
def gen(R1CS, ns): # time = k * len(gates) ** 2 * len(vars)
    return [util.lagrange(list(zip(ns, ys)), Q) for ys in zip(*R1CS)]
def dot(QAP, s):
    return [sum(i * j for i, j in zip(u, s)) % Q for u in zip(*QAP)]
def compile(f):
    eqs = []
    ids = iter(range(0, 1 << 16))
    def const(n):
        i = next(ids)
        return i
    def reg(name):
        i = next(ids)
        return i
    def mul(a, b):
        i = next(ids)
        eqs.append((i, a, b))
        return i
    f(const, reg, mul)
    count = next(ids)
    gates = []
    for i, a, b in eqs:
        gate = [[0 for _ in range(count)] for _ in range(3)]
        for j, n in a:
            gate[0][j] += n
        for j, n in b:
            gate[1][j] += n
        gate[2][i] = 1
        gates.append(gate)
    return gates
def witness(f, **kwargs):
    s = []
    ids = iter(range(0, 1 << 16))
    def const(n):
        i = next(ids)
        s.append(n)
        return i
    def reg(name):
        i = next(ids)
        s.append(kwargs[name])
        return i
    def mul(a, b):
        i = next(ids)
        A = sum(s[i] * n for i, n in a) % Q
        B = sum(s[i] * n for i, n in b) % Q
        s.append(A * B % Q)
        return i
    f(const, reg, mul)
    return s
if __name__ == '__main__':
    print('GF({})'.format(Q))
    def fibonacci(const, reg, mul):
        U = const(0)
        A = const(0)
        B = const(1)
        X = reg('x')
        O = const(0)
        for i in range(32):
            T = A
            for j in range(32):
                if i != j:
                    a, _ = util.moddiv(1, i - j, Q)
                    b, _ = util.moddiv(j, j - i, Q)
                    T = mul([(T, 1)], [(X, a), (U, b)])
            O = mul([(O, 1), (T, 1)], [(U, 1)])
            A, B = B, mul([(A, 1), (B, 1)], [(U, 1)])
    # Compile
    gates = compile(fibonacci)
    A, B, C = zip(*gates) # R1CS
    ns = list(util.choice(0, Q, len(gates)))
    A = gen(A, ns)
    B = gen(B, ns)
    C = gen(C, ns)
    Z = poly(ns)
    print('Z =', Z)
    # Prove
    s = witness(fibonacci, x = 25)
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
