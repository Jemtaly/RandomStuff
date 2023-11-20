def exgcd(a, b):
    if b == 0:
        return abs(a), ((a > 0) - (a < 0), 0)
    d, (x, y) = exgcd(b, a % b)
    return d, (y, x - a // b * y)
def gcd(l):
    return 0 if len(l) == 0 else l[0] if len(l) == 1 else exgcd(gcd(l[::2]), gcd(l[1::2]))[0]
def lcm(l):
    return 1 if len(l) == 0 else l[0] if len(l) == 1 else (lambda x, y: x * y // exgcd(x, y)[0])(lcm(l[::2]), lcm(l[1::2]))
def crt(D):
    R, M = 0, 1
    for r, m in D:
        d, (N, n) = exgcd(M, m)
        assert (r - R) % d == 0
        R += (r - R) // d * N * M
        M *= m // d
    return R, M
def moddiv(a, b, m):
    d, (r, _) = exgcd(b, m)
    assert a % d == 0
    return a // d * r, m // d
def reduce(l):
    q = gcd(l)
    return type(l)((i // q for i in l) if q else (0 for _ in l))
def rref(m, h, w): # reduced row echelon form
    for J in range(w):
        I = next((I for I in range(h) if all(m[I][j] == 0 for j in range(J)) and m[I][J] != 0), None)
        if I is None:
            continue
        for i in range(h):
            if i == I:
                continue
            mrecord = m[i][J]
            for j in range(J, w):
                m[i][j] = m[i][j] * m[I][J] - m[I][j] * mrecord
            m[i] = reduce(m[i]) # optional
