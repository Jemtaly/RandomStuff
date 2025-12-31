#!/usr/bin/env python3

import tkinter as tk
from typing import TypeVar, cast

T = TypeVar("T", bound=tuple[float, ...])


def tpoint(t: float, p: T, q: T) -> T:
    return cast(T, tuple(x * (1 - t) + z * t for x, z in zip(p, q)))


def bpoint(t: float, points: list[T]) -> T:
    if len(points) == 1:
        return points[0]
    return bpoint(t, [tpoint(t, p, q) for p, q in zip(points[:-1], points[1:])])


def bezier(n: int, points: list[T]) -> list[T]:
    return [bpoint(i / (n - 1), points) for i in range(n)]


class BezierApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bezier")
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-3>", self.init_canvas)
        self.init_canvas()

    def init_canvas(self, event=None):
        self.points: list[tuple[float, float]] = []
        self.canvas.delete(tk.ALL)
        self.canvas.bind("<Button-1>", self.draw_point)
        self.canvas.bind("<Double-1>", self.draw_curve)

    def draw_point(self, event):
        self.canvas.create_text(event.x, event.y, text=str((event.x, event.y)), fill="blue")
        if self.points:
            self.canvas.create_line(*self.points[-1], event.x, event.y)
        self.points.append((event.x, event.y))

    def draw_curve(self, event):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Double-1>")
        curve = bezier(256, self.points)
        self.canvas.create_line(curve, fill="red")


def main():
    app = BezierApp()
    app.mainloop()


if __name__ == "__main__":
    main()
