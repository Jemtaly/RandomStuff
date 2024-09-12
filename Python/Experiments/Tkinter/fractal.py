#!/usr/bin/env python3


import tkinter as tk


class Canvas(tk.Canvas):
    def __init__(self, graph, master=None, width=800, height=800, scale=800):
        super().__init__(master, width=width, height=height)
        graph.draw(self)
        self.scale(tk.ALL, 0, 0, scale, scale)
        self.move(tk.ALL, width / 2, height / 2)
        self.width = width
        self.height = height
        self.bind("<ButtonPress-1>", self.drag_start)
        self.bind("<ButtonRelease-1>", self.drag_end)
        self.bind("<B1-Motion>", self.drag)
        self.bind("<Button-4>", self.zoom)
        self.bind("<Button-5>", self.zoom)
        self.bind("<MouseWheel>", self.zoom)
        self.bind("<Configure>", self.change)

    def drag_start(self, event):
        self.x_start = event.x
        self.y_start = event.y

    def drag_end(self, event):
        del self.x_start
        del self.y_start

    def drag(self, event):
        x = event.x - self.x_start
        y = event.y - self.y_start
        self.move(tk.ALL, x, y)
        self.x_start = event.x
        self.y_start = event.y

    def zoom(self, event):
        x = event.x
        y = event.y
        if event.delta > 0 or event.num == 4:
            self.scale(tk.ALL, x, y, 1.25, 1.25)
        if event.delta < 0 or event.num == 5:
            self.scale(tk.ALL, x, y, 0.80, 0.80)

    def change(self, event):
        self.move(tk.ALL, (event.width - self.width) / 2, (event.height - self.height) / 2)
        self.width = event.width
        self.height = event.height


class Affine:
    def __init__(self, b=0, u=1, v=0):
        self.b = b
        self.u = u
        self.v = v

    def __call__(self, p):
        p = self.u * p + self.v * p.conjugate() + self.b
        return p.real, -p.imag

    def __mul__(self, other):
        return Affine(
            b=self.u * other.b + self.v * other.b.conjugate() + self.b,
            u=self.u * other.u + self.v * other.v.conjugate(),
            v=self.u * other.v + self.v * other.u.conjugate(),
        )


class Polygon:
    def __init__(self, *points):
        self.points = points

    def draw(self, canvas, affine=Affine()):
        floats = sum(map(affine, self.points), ())
        if len(self.points) == 0:
            pass
        elif len(self.points) == 1:
            canvas.create_rectangle(*floats, *floats, fill="black", width=0)
        elif len(self.points) == 2:
            canvas.create_line(*floats, fill="black")
        else:
            canvas.create_polygon(*floats, fill="black")


class Compound:
    def __init__(self, *components):
        self.components = components

    def draw(self, canvas, affine=Affine()):
        for component, other in self.components:
            component.draw(canvas, affine * other)


def test():
    line = Polygon(
        -0.5,
        +0.5,
    )
    poly = Polygon(
        -0.5,
        +0.5j,
        +0.5,
        -0.5j,
    )
    for _ in range(10):
        poly = Compound(
            (line, Affine(-0.25, -0.5, 0)),
            (poly, Affine(+0.25, +0.5, 0)),
            (poly, Affine(-0.25j, -0.5j, 0)),
            (poly, Affine(+0.25j, +0.5j, 0)),
        )
    canvas = Canvas(graph=poly)
    canvas.pack(expand=True, fill=tk.BOTH)
    canvas.mainloop()


if __name__ == "__main__":
    test()
