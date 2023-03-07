import numpy as np
def log(q):
    return q.__log__()
def exp(q):
    return q.__exp__()
class Quaternion:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z
    def __neg__(self):
        return Quaternion(-self.w, -self.x, -self.y, -self.z)
    def __pos__(self):
        return Quaternion(+self.w, +self.x, +self.y, +self.z)
    def __abs__(self):
        return (self.w ** 2 + self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    def __add__(self, fles):
        return Quaternion(self.w + fles.w, self.x + fles.x, self.y + fles.y, self.z + fles.z)
    def __sub__(self, fles):
        return Quaternion(self.w - fles.w, self.x - fles.x, self.y - fles.y, self.z - fles.z)
    def __rmul__(self, num):
        return Quaternion(self.w * num, self.x * num, self.y * num, self.z * num)
    def __truediv__(self, num):
        return Quaternion(self.w / num, self.x / num, self.y / num, self.z / num)
    def __mul__(self, fles):
        return Quaternion(
            self.w * fles.w - self.x * fles.x - self.y * fles.y - self.z * fles.z,
            self.w * fles.x + self.x * fles.w + self.y * fles.z - self.z * fles.y,
            self.w * fles.y - self.x * fles.z + self.y * fles.w + self.z * fles.x,
            self.w * fles.z + self.x * fles.y - self.y * fles.x + self.z * fles.w,
        )
    def __exp__(self):
        h = (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
        s, c = np.sin(h), np.cos(h)
        x, y, z = (self.x / h, self.y / h, self.z / h) if h else (0, 0, 0)
        return np.exp(self.w) * Quaternion(c, x * s, y * s, z * s)
    def __log__(self):
        scal = abs(self)
        unit = (self / scal) if scal else Quaternion(1, 0, 0, 0)
        s, h = (1 - unit.w ** 2) ** 0.5, np.arccos(unit.w)
        x, y, z = (unit.x / s, unit.y / s, unit.z / s) if s else (0, 0, 0)
        return Quaternion(np.log(scal), x * h, y * h, z * h)
    def __pow__(self, num):
        return exp(num * log(self))
    def __str__(self):
        return '{%s, %s, %s, %s}' % (self.w, self.x, self.y, self.z)
    def pauli(self):
        return np.array([
            [self.w * +1. + self.z * -1j, self.y * -1. + self.x * -1j],
            [self.y * +1. + self.x * -1j, self.w * +1. + self.z * +1j],
        ])
    def euler(self):
        scal = abs(self)
        unit = (self / scal) if scal else Quaternion(1, 0, 0, 0)
        s, h = (1 - unit.w ** 2) ** 0.5, np.arccos(unit.w)
        x, y, z = (unit.x / s, unit.y / s, unit.z / s) if s else (0, 0, 0)
        H = h * 2
        S, C = np.sin(H), np.cos(H)
        return np.array([
            [x * x * (1 - C) + 1 * C, x * y * (1 - C) + z * S, x * z * (1 - C) - y * S],
            [y * x * (1 - C) - z * S, y * y * (1 - C) + 1 * C, y * z * (1 - C) + x * S],
            [z * x * (1 - C) + y * S, z * y * (1 - C) - x * S, z * z * (1 - C) + 1 * C],
        ]) * scal
