#!/usr/bin/env python3


import matplotlib.pyplot as plt

import quthon


def main():
    qsta = quthon.Qubits(26)
    for i in range(0, 22, 11):
        for j in range(0, 8, 4):
            for k in range(0, 2, 1):
                t = sum([i, j, k])
                qsta.H(t + 0).ADDER(range(t + 0 + 0, t + 0 + 0), range(t + 0 + 0, t + 0 + 0), range(t + 0, t + 1))
            t = sum([i, j])
            qsta.H(t + 2).ADDER(range(t + 0 + 0, t + 0 + 1), range(t + 1 + 0, t + 1 + 1), range(t + 2, t + 4))
        t = sum([i])
        qsta.H(t + 8).ADDER(range(t + 0 + 2, t + 0 + 4), range(t + 4 + 2, t + 4 + 4), range(t + 8, t + 11))
    t = sum([])
    qsta.H(t + 22).ADDER(range(t + 0 + 8, t + 0 + 11), range(t + 11 + 8, t + 11 + 11), range(t + 22, t + 26))
    prob = qsta.getprob(22, 23, 24, 25).T.reshape((-1,))
    plt.bar(range(16), prob)
    plt.show()


if __name__ == "__main__":
    main()
