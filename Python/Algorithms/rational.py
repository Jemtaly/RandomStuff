MAP = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def show_frac(n: int, d: int, b: int = 10):
    assert 2 <= b <= 36
    if d == 0:
        return "-Inf" if n < 0 else "+Inf" if n > 0 else "±NaN"
    elif d > 0:
        d, n = +d, +n
    elif d < 0:
        d, n = -d, -n
    sgn_s = "-" if n < 0 else "+" if n > 0 else "±"
    n = abs(n)
    q, r = divmod(n, d)
    int_l: list[int] = []
    dec_l: list[int] = []
    rec_d: dict[int, int] = {}
    while q:
        q, t = divmod(q, b)
        int_l.append(t)
    while (l := len(dec_l)) == (k := rec_d.setdefault(r, l)):
        t, r = divmod(r * b, d)
        dec_l.append(t)
    int_s = "".join(MAP[q] for q in int_l[::-1])
    fst_s = "".join(MAP[r] for r in dec_l[:k:1])
    sec_s = "".join(MAP[r] for r in dec_l[k::1])
    return f"{sgn_s}{int_s}.{fst_s}({sec_s})"


if __name__ == "__main__":
    print(show_frac(1000, 998))
