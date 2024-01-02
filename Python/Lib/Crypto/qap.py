#!/usr/bin/python3
import util
import ecc
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
class QAP:
    def __init__(self):
        self.gatereg = []
        self.funcreg = []
        self.asserts = []
    def funcregnew(self, fun):
        i = len(self.funcreg)
        self.funcreg.append(fun)
        return i
    def compile(self):
        gaten = len(self.gatereg)
        funcn = len(self.funcreg)
        gates = [[[0 for _ in range(funcn)] for _ in range(3)] for _ in range(gaten)]
        for i, reg in enumerate(self.gatereg):
            xs, ys, zs = reg
            for x, m in xs:
                gates[i][0][x] += m
            for y, n in ys:
                gates[i][1][y] += n
            for z, o in zs:
                gates[i][2][z] += o
        return gates
    def witness(self, **kwargs):
        funcn = len(self.funcreg)
        witness = [0 for _ in range(funcn)]
        for i, fun in enumerate(self.funcreg):
            witness[i] = fun(witness, **kwargs)
        for fun in self.asserts:
            assert fun(witness, **kwargs)
        return witness
    def VAR(self, name): # return new variable
        o = self.funcregnew(lambda witness, **kwargs: kwargs[name])
        return o
    def VMUL(self, xs, ys, zs = [], N = 1): # return (sum(xs) * sum(ys) - sum(zs)) / N (mod Q)
        o = self.funcregnew(lambda witness, **kwargs: (sum(witness[x] * m for x, m in xs) * pow(sum(witness[y] * n for y, n in ys), +1, Q) - sum(witness[z] * o for z, o in zs)) * pow(N, -1, Q) % Q)
        self.gatereg.append((xs, ys, zs + [(o, N)]))
        return o
    def VDIV(self, zs, ys, xs = [], N = 1): # return (sum(xs) / sum(ys) - sum(zs)) / N (mod Q)
        o = self.funcregnew(lambda witness, **kwargs: (sum(witness[z] * o for z, o in zs) * pow(sum(witness[y] * n for y, n in ys), -1, Q) - sum(witness[x] * m for x, m in xs)) * pow(N, -1, Q) % Q)
        self.gatereg.append((xs + [(o, N)], ys, zs))
        return o
    def MUL(self, a, b): # return a * b (mod Q)
        return self.VMUL([(a, 1)], [(b, 1)])
    def DIV(self, c, b): # return c / b (mod Q)
        return self.VDIV([(c, 1)], [(b, 1)])
    def POW(self, e, a, N): # return a ** N (mod Q)
        if N < 0:
            N = -N
            a = self.DIV(e, a)
        if N & 1:
            e = a
        N >>= 1
        while N:
            a = self.MUL(a, a)
            if N & 1:
                e = self.MUL(e, a)
            N >>= 1
        return e
    def BOOL(self, xs): # return sum(xs) != 0 (0 or 1)
        i = self.funcregnew(lambda witness, **kwargs: pow(sum(witness[x] * m for x, m in xs), Q - 2, Q))
        o = self.funcregnew(lambda witness, **kwargs: pow(sum(witness[x] * m for x, m in xs), Q - 1, Q))
        self.gatereg.append((xs, [(o, 1)], xs))
        self.gatereg.append((xs, [(i, 1)], [(o, 1)]))
        return o
    def COND(self, e, c, t, f): # return c ? t : f
        t = self.VMUL([(t, 1)], [(c, 1)])
        f = self.VMUL([(f, 1)], [(c, 1), (e, -1)])
        r = self.VMUL([(e, 1)], [(t, 1), (f, -1)])
        return r
    def ASSERT_BOOL(self, x): # assert x == 0 or x == 1
        self.asserts.append(lambda witness, **kwargs: witness[x] ** 2 % Q == witness[x])
        self.gatereg.append(([(x, 1)], [(x, 1)], [(x, 1)]))
    def ASSERT_ZERO(self, e, xs): # assert sum(xs) == 0 (mod Q)
        self.asserts.append(lambda witness, **kwargs: (sum(witness[x] * m for x, m in xs) + witness[e]) * witness[e] % Q == witness[e])
        self.gatereg.append((xs + [(e, 1)], [(e, 1)], [(e, 1)]))
    def ASSERT_NONZ(self, e, xs): # assert sum(xs) != 0 (mod Q)
        i = self.funcregnew(lambda witness, **kwargs: pow(sum(witness[x] * m for x, m in xs), Q - 2, Q) * witness[e] % Q)
        self.asserts.append(lambda witness, **kwargs: pow(sum(witness[x] * m for x, m in xs), Q - 1, Q) * witness[e] % Q == witness[e])
        self.gatereg.append((xs, [(i, 1)], [(e, 1)]))
if __name__ == '__main__':
    print('GF({})'.format(Q))
    qap = QAP()
    # Variables
    x = qap.VAR('x')
    e = qap.VAR('e')
    # Gates
    y = qap.MUL(x, x)
    z = qap.VMUL([(y, 1), (e, 1)], [(x, 1)])
    w = qap.VMUL([(z, 1), (e, 5)], [(e, 1)])
    # Compile
    gates = qap.compile()
    A, B, C = zip(*gates) # R1CS
    ns = list(util.choice(0, Q, len(gates)))
    Z = poly(ns) # QAP
    A = gen(A, ns)
    B = gen(B, ns)
    C = gen(C, ns)
    print('Z =', Z)
    # Prove
    s = qap.witness(x = 3, e = 1)
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
