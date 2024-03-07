#!/usr/bin/python3
import quthon
import numpy as np
def simon(func, i, o):
    qsta = quthon.Qubits(i + o)
    for j in range(i):
        qsta.H(j)
    qsta.UF(func, range(i), range(i, i + o))
    for j in range(i):
        qsta.H(j)
    prob = qsta.getprob(*range(i)).reshape((-1,))
    for j, p in enumerate(prob):
        print('p({:0{}b}) = {:.6f}'.format(j, i, p))
def test():
    v, u = 0b000111, 0b110000
    f, g = lambda x: max(x, x ^ u), lambda x: max(x, x ^ v)
    func = lambda x: f(g(x))
    simon(func, 6, 6)
if __name__ == '__main__':
    test()
