class NumberFormatter:
    TABLE = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(
        self,
        base: int | str = 10,
    ) -> None:
        match base:
            case int():
                if base > len(self.TABLE):
                    raise ValueError(f"base must be <= {len(self.TABLE)}")
                self.table = self.TABLE[:base]
                self.b = base

            case str():
                if len(set(base)) != len(base):
                    raise ValueError("base string must have unique characters")
                self.table = base
                self.b = len(base)

        if len(self.table) < 2:
            raise ValueError("base must be at least 2")

    def format(self, n: int, d: int) -> str:
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
            q, t = divmod(q, self.b)
            int_l.append(t)

        while (l := len(dec_l)) == (k := rec_d.setdefault(r, l)):
            t, r = divmod(r * self.b, d)
            dec_l.append(t)

        int_s = "".join(self.table[q] for q in int_l[::-1])
        fst_s = "".join(self.table[r] for r in dec_l[:k:1])
        sec_s = "".join(self.table[r] for r in dec_l[k::1])

        return f"{sgn_s}{int_s}.{fst_s}({sec_s})"


if __name__ == "__main__":
    print(NumberFormatter().format(1000, 998))
    print(NumberFormatter(16).format(-255, 16))
