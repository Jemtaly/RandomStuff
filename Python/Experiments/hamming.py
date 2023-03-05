#!/usr/bin/python3
encoder = {}
for i in range(16):
    msg_old = tuple(int(x) for x in '{:04b}'.format(i))
    a, b, c, d = msg_old
    e = a ^ c ^ d
    f = a ^ b ^ d
    g = a ^ b ^ c
    encoder[msg_old] = a, b, c, d, e, f, g
decoder = {}
for i in range(16):
    msg_old = tuple(int(x) for x in '{:04b}'.format(i))
    cod_old = encoder[msg_old]
    decoder[cod_old] = msg_old
    for j in range(7):
        cod_err = tuple(int(x) for x in '{:07b}'.format(1 << j))
        cod_new = tuple(x ^ y for x, y in zip(cod_old, cod_err))
        cod_new = tuple(cod_new)
        decoder[cod_new] = msg_old
def errprob(p):
    errprob = 0
    for i in range(16):
        msg_old = tuple(int(x) for x in '{:04b}'.format(i))
        cod_old = encoder[msg_old]
        for j in range(128):
            cod_err = tuple(int(x) for x in '{:07b}'.format(j))
            cod_new = tuple(x ^ y for x, y in zip(cod_old, cod_err))
            msg_new = decoder[cod_new]
            msg_err = tuple(x ^ y for x, y in zip(msg_old, msg_new))
            q = p ** cod_err.count(1) * (1 - p) ** cod_err.count(0) / 16
            errbits = msg_err.count(1)
            errprob += errbits / 4 * q
    return errprob
def main():
    import sympy
    p = sympy.symbols('p')
    P = sympy.simplify(errprob(p))
    print('P =', P)
if __name__ == '__main__':
    main()
