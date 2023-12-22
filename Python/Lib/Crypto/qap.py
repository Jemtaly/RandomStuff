#!/usr/bin/python3
import util
import time
Q = util.genPrime(16)
def poly(ns):
    Z = [1]
    for n in ns:
        Z = [(v - n * u) % Q for u, v in zip(Z + [0], [0] + Z)]
    return Z
def gen(R1CS, ns): # time = k * len(gates) ** 2 * len(witness)
    return [util.lagrange(list(zip(ns, ys)), Q) for ys in zip(*R1CS)]
def dot(QAP, s):
    return [sum(i * j for i, j in zip(u, s)) % Q for u in zip(*QAP)]
class Asseter:
    def __init__(self):
        self.counter = util.counter()
        self.witfunc = {}
        self.asserts = []
        self.gateset = []
    def compile(self):
        count = len(self.witfunc)
        gates = []
        for a, b, c in self.gateset:
            gate = [[0 for _ in range(count)] for _ in range(3)]
            for j, n in a:
                gate[0][j] += n
            for j, n in b:
                gate[1][j] += n
            for j, n in c:
                gate[2][j] += n
            gates.append(gate)
        return gates
    def witness(self, **kwargs):
        count = len(self.witfunc)
        witness = [0 for _ in range(count)]
        for i, f in self.witfunc.items():
            witness[i] = f(witness, **kwargs)
        for f in self.asserts:
            assert f(witness, **kwargs)
        return witness
    def VAR(self, name):
        c = next(self.counter)
        self.witfunc[c] = lambda witness, **kwargs: kwargs[name]
        return c
    def VMUL(self, xs, ys, zs = [], N = 1):
        s = next(self.counter)
        self.witfunc[s] = lambda witness, **kwargs: (pow(sum(witness[x] * m for x, m in xs), +1, Q) * pow(sum(witness[y] * n for y, n in ys), +1, Q) - sum(witness[z] * o for z, o in zs)) * pow(N, -1, Q) % Q
        self.gateset.append((xs, ys, zs + [(s, N)]))
        return s
    def VDIV(self, zs, xs, ys = [], N = 1):
        s = next(self.counter)
        self.witfunc[s] = lambda witness, **kwargs: (pow(sum(witness[z] * o for z, o in zs), +1, Q) * pow(sum(witness[x] * m for x, m in xs), -1, Q) - sum(witness[y] * n for y, n in ys)) * pow(N, -1, Q) % Q
        self.gateset.append((xs, ys + [(s, N)], zs))
        return s
    def MUL(self, a, b):
        return self.VMUL([(a, 1)], [(b, 1)])
    def DIV(self, c, b):
        return self.VDIV([(c, 1)], [(b, 1)])
    def POW(self, e, a, N):
        if N < 0:
            N = -N
            a = self.DIV(e, a)
        p = a if N & 1 else e
        N >>= 1
        while N:
            a = self.MUL(a, a)
            if N & 1:
                p = self.MUL(p, a)
            N >>= 1
        return p
    def BOOL(self, xs):
        r = next(self.counter)
        y = next(self.counter)
        self.witfunc[r] = lambda witness, **kwargs: pow(sum(witness[x] * m for x, m in xs), Q - 2, Q)
        self.witfunc[y] = lambda witness, **kwargs: pow(sum(witness[x] * m for x, m in xs), Q - 1, Q)
        self.gateset.append((xs, [(y, 1)], xs))
        self.gateset.append((xs, [(r, 1)], [(y, 1)]))
        return y
    def COND(self, e, c, a, b):
        x = self.VMUL([(a, 1)], [(c, 1)])
        y = self.VMUL([(b, 1)], [(c, 1), (e, -1)])
        r = self.VMUL([(e, 1)], [(x, 1), (y, -1)])
        return r
    def ASSERT_BOOL(self, x):
        self.asserts.append(lambda witness, **kwargs: witness[x] ** 2 % Q == witness[x])
        self.gateset.append(([(x, 1)], [(x, 1)], [(x, 1)]))
    def ASSERT_NONZ(self, e, x):
        y = next(self.counter)
        self.witfunc[y] = lambda witness, **kwargs: pow(witness[x], Q - 2, Q)
        self.asserts.append(lambda witness, **kwargs: witness[x] * witness[y] % Q == 1)
        self.gateset.append(([(x, 1)], [(y, 1)], [(e, 1)]))
if __name__ == '__main__':
    print('GF({})'.format(Q))
    asseter = Asseter()
    # Variables
    x = asseter.VAR('x')
    e = asseter.VAR('e')
    # Gates
    y = asseter.MUL(x, x)
    z = asseter.VMUL([(y, 1), (e, 1)], [(x, 1)])
    w = asseter.VMUL([(z, 1), (e, 5)], [(e, 1)])
    # Compile
    gates = asseter.compile()
    A, B, C = zip(*gates) # R1CS
    ns = list(util.choice(0, Q, len(gates)))
    A = gen(A, ns)
    B = gen(B, ns)
    C = gen(C, ns)
    Z = poly(ns)
    print('Z =', Z)
    # Prove
    s = asseter.witness(x = 3, e = 1)
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
