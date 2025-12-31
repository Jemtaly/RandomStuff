#!/usr/bin/env python3

from dataclasses import dataclass
import math
import tkinter as tk


@dataclass
class RGB:
    r: int
    g: int
    b: int

    def __post_init__(self):
        assert (self.r | self.g | self.b) >> 8 == 0

    def __repr__(self):
        return "#{:02x}{:02x}{:02x}".format(self.r, self.g, self.b)

    def __invert__(self):
        return RGB(255 - self.r, 255 - self.g, 255 - self.b)


def HSB(hues: float, saturation: float = math.inf, brightness: float = 0.0):
    S = (math.exp(+saturation) - math.exp(-saturation)) / (math.exp(+saturation) + math.exp(-saturation))
    H = 1 / (1 + math.exp(-brightness))
    R = S / (1 + math.exp(-brightness) + math.exp(+brightness))
    r = min(255, math.floor(256 * (H + R * math.cos(hues))))
    g = min(255, math.floor(256 * (H + R * math.cos(hues - math.tau / 3))))
    b = min(255, math.floor(256 * (H + R * math.cos(hues + math.tau / 3))))
    return RGB(r, g, b)


def RGB_main():
    root = tk.Tk()
    root.title("RGB")
    canvas = tk.Canvas(root)

    def change(value=None):
        colour = RGB(R.get(), G.get(), B.get())
        canvas.delete(tk.ALL)
        canvas.configure(background=str(colour))
        canvas.create_text(0.0, 0.0, text=str(colour), fill=str(~colour), anchor=tk.NW)

    R = tk.IntVar()
    G = tk.IntVar()
    B = tk.IntVar()
    R_scaler = tk.Scale(root, variable=R, from_=255, to=0, showvalue=False, command=change)
    G_scaler = tk.Scale(root, variable=G, from_=255, to=0, showvalue=False, command=change)
    B_scaler = tk.Scale(root, variable=B, from_=255, to=0, showvalue=False, command=change)
    R_scaler.pack(fill=tk.Y, side=tk.LEFT)
    G_scaler.pack(fill=tk.Y, side=tk.LEFT)
    B_scaler.pack(fill=tk.Y, side=tk.LEFT)
    canvas.pack(fill=tk.BOTH, expand=True)
    change()
    root.mainloop()


def HSB_main():
    root = tk.Tk()
    root.title("HSB")
    canvas = tk.Canvas(root)

    def change(value=None):
        colour = HSB(H.get(), math.tan(S.get()), math.tan(B.get()))
        canvas.delete(tk.ALL)
        canvas.configure(background=str(colour))
        canvas.create_text(0.0, 0.0, text=str(colour), fill=str(~colour), anchor=tk.NW)

    H = tk.DoubleVar()
    S = tk.DoubleVar()
    B = tk.DoubleVar()
    H_scaler = tk.Scale(root, variable=H, from_=+3.14, to=-3.14, resolution=0.01, showvalue=False, command=change)
    S_scaler = tk.Scale(root, variable=S, from_=+1.56, to=+0.00, resolution=0.01, showvalue=False, command=change)
    B_scaler = tk.Scale(root, variable=B, from_=+1.56, to=-1.56, resolution=0.01, showvalue=False, command=change)
    H_scaler.pack(fill=tk.Y, side=tk.LEFT)
    S_scaler.pack(fill=tk.Y, side=tk.LEFT)
    B_scaler.pack(fill=tk.Y, side=tk.LEFT)
    canvas.pack(fill=tk.BOTH, expand=True)
    change()
    root.mainloop()


if __name__ == "__main__":
    HSB_main()
