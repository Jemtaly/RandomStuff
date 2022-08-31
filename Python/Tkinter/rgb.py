#!/usr/bin/python3
class RGB:
    def __init__(self, r, g, b):
        assert (r | g | b) >> 8 == 0
        self.r = r
        self.g = g
        self.b = b
    def __repr__(self):
        return '#{:02x}{:02x}{:02x}'.format(self.r, self.g, self.b)
    def __invert__(self):
        return RGB(255 - self.r, 255 - self.g, 255 - self.b)
def main():
    import tkinter
    tk = tkinter.Tk()
    tk.title('RGB')
    canvas = tkinter.Canvas(tk)
    def change(value = None):
        colour = RGB(R.get(), G.get(), B.get())
        canvas.delete(tkinter.ALL)
        canvas.configure(background = colour)
        canvas.create_text(0.0, 0.0, text = colour, fill = ~colour, anchor = tkinter.NW)
    R = tkinter.IntVar()
    G = tkinter.IntVar()
    B = tkinter.IntVar()
    R_scaler = tkinter.Scale(tk, variable = R, from_ = 255, to = 0, showvalue = False, command = change)
    G_scaler = tkinter.Scale(tk, variable = G, from_ = 255, to = 0, showvalue = False, command = change)
    B_scaler = tkinter.Scale(tk, variable = B, from_ = 255, to = 0, showvalue = False, command = change)
    R_scaler.pack(fill = tkinter.Y, side = tkinter.LEFT)
    G_scaler.pack(fill = tkinter.Y, side = tkinter.LEFT)
    B_scaler.pack(fill = tkinter.Y, side = tkinter.LEFT)
    canvas.pack(fill = tkinter.BOTH, expand = True)
    change()
    tk.mainloop()
if __name__ == '__main__':
    main()
