#!/usr/bin/env python3


import quthon


def simon(func, i, o):
    qsta = quthon.Qubits(i + o)
    for j in range(i):
        qsta.H(j)
    qsta.UF(func, range(i), range(i, i + o))
    for j in range(i):
        qsta.H(j)
    prob = qsta.getprob(*range(i)).reshape((-1,))
    for j, p in enumerate(prob):
        print("p({:0{}b}) = {:.6f}".format(j, i, p))


def test():
    v, u = 0b000111, 0b110000
    func = lambda x: max(x, x ^ u, x ^ v, x ^ u ^ v)
    simon(func, 6, 6)


if __name__ == "__main__":
    test()
