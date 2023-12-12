import random
import util
Q = util.genPrime(1024)
def generateShares(k, n, secret):
    coeffs = [secret]
    for _ in range(1, k):
        coeffs.append(random.randrange(0, Q))
    shares = set()
    while len(shares) < n:
        x = random.randrange(0, Q)
        shares.add((x, sum(c * x ** i for i, c in enumerate(coeffs)) % Q))
    return list(shares)
def reconstructSecret(shares):
    secret = 0
    for xj, yj in shares:
        prod = 1
        for xm, ym in shares:
            if xm != xj:
                prod = prod * xm * pow(xm - xj, -1, Q) % Q
        secret = (secret + yj * prod) % Q
    return secret
if __name__ == '__main__':
    print('GF({})'.format(Q))
    K, N = 3, 5
    secret = random.randrange(0, Q)
    print('secret:', secret)
    shares = generateShares(K, N, secret)
    print('shares:', ', '.join('({}, {})'.format(x, y) for x, y in shares))
    sample = random.sample(shares, K)
    print('sample:', ', '.join('({}, {})'.format(x, y) for x, y in sample))
    resecret = reconstructSecret(sample)
    print('resecret:', resecret)
