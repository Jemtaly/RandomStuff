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
    A, M = 0, 1
    for a, m in D:
        d, (r, _) = exgcd(M, m)
        assert (a - A) % d == 0
        A += (a - A) // d * r * M
        M *= m // d
    return A, M
def moddiv(a, b, m):
    d, (r, _) = exgcd(b, m)
    assert a % d == 0
    return a // d * r, m // d
def reduce(l):
    q = gcd(l)
    return type(l)((i // q for i in l) if q else (0 for _ in l))
def rref(m, h, w): # reduced row echelon form
    r = set()
    for j in range(w):
        for i in range(h):
            if m[i][j] != 0 and i not in r:
                break
        else:
            continue
        r.add(i) # pivot
        for x in range(h):
            if x == i:
                continue
            mrecord = m[x][j]
            for y in range(w):
                m[x][y] = m[x][y] * m[i][j] - m[i][y] * mrecord
            m[x] = reduce(m[x]) # optional
