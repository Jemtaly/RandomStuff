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
def ref(m):
    s, m = [], [[i for i in j] for j in m]
    for j in range(len(m[0])):
        for i in range(len(m)):
            if m[i][j] != 0:
                break
        else:
            continue
        s.append(reduce(m.pop(i)))
        for x in range(len(m)):
            mrecord = m[x][j]
            for y in range(len(m[0])):
                m[x][y] = m[x][y] * s[-1][j] - s[-1][y] * mrecord
    return s + m
def rref(m):
    m = ref(m)
    for i in range(len(m))[::-1]:
        for j in range(len(m[0])):
            if m[i][j] != 0:
                break
        else:
            continue
        m[i] = reduce(m[i])
        for x in range(i):
            mrecord = m[x][j]
            for y in range(len(m[0])):
                m[x][y] = m[x][y] * m[i][j] - m[i][y] * mrecord
    return m
