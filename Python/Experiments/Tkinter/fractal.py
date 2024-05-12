#!/usr/bin/env python3
import turtle
class Affine:
    def __init__(self, b = 0, u = 1, v = 0):
        self.b = b
        self.u = u
        self.v = v
    def __call__(self, p):
        p = self.u * p + self.v * p.conjugate() + self.b
        return p.real, -p.imag
    def __mul__(self, former):
        return Affine(
            b = self.u * former.b + self.v * former.b.conjugate() + self.b,
            u = self.u * former.u + self.v * former.v.conjugate(),
            v = self.u * former.v + self.v * former.u.conjugate(),
        )
class Polygon:
    def __init__(self, start, *points):
        self.start = start
        self.points = points
    def draw(self, affine):
        turtle.goto(affine(self.start))
        turtle.pendown()
        turtle.begin_fill()
        for point in self.points:
            turtle.goto(affine(point))
        turtle.end_fill()
        turtle.penup()
class Compound:
    def __init__(self, *components):
        self.leaves = components
    def draw(self, affine):
        for component, former in self.leaves:
            component.draw(affine * former)
def test():
    turtle.tracer(0, 0)
    turtle.penup()
    line = Polygon(
        -0.5,
        +0.5,
    )
    poly = Polygon(
        -0.5, +0.5j,
        +0.5, -0.5j,
    )
    for i in range(8):
        poly = Compound(
            (line, Affine(-0.25 , -0.5 , 0)),
            (poly, Affine(+0.25 , +0.5 , 0)),
            (poly, Affine(-0.25j, -0.5j, 0)),
            (poly, Affine(+0.25j, +0.5j, 0)),
        )
    poly.draw(Affine(0, 256, 0))
    turtle.hideturtle()
    turtle.mainloop()
if __name__ == '__main__':
    test()
