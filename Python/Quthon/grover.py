#!/usr/bin/python3
import quthon
import numpy as np
def grover(func, d):
    qsta = quthon.Qubits(d + 1)
    for i in range(d):
        qsta.H(i)
    qsta.X(d).H(d)
    for i in range(np.ceil(np.pi / 4 * np.sqrt(2 ** d)).astype(int)):
        qsta.UF(func, range(d), (d,)) \
            .SF(*range(d))
    prob = qsta.getprob(*range(d)).reshape((-1,))
    for i, p in enumerate(prob):
        print('p({:0{}b}) = {:.6f}'.format(i, d, p))
def test():
    dest = 0b110111
    func = lambda x: x == dest
    grover(func, 6)
if __name__ == '__main__':
    test()
