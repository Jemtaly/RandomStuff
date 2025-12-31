import argparse
import tkinter as tk

import PIL.ImageGrab as ImageGrab
import PIL.ImageTk as ImageTk

from .core import decrypt


class Selecter(tk.Toplevel):
    def __init__(self, parent, res, len):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.5)
        self.attributes("-transparentcolor", "#000000")
        self.n = 4
        self.a = 8 * len / res[0]
        self.b = 8 * len / res[1]
        self.ml = tk.Frame(self, bg="#ff0000", width=self.n, cursor="left_side")
        self.mr = tk.Frame(self, bg="#ff0000", width=self.n, cursor="right_side")
        self.tm = tk.Frame(self, bg="#ff0000", height=self.n, cursor="top_side")
        self.bm = tk.Frame(self, bg="#ff0000", height=self.n, cursor="bottom_side")
        self.tl = tk.Frame(self, bg="#ff0000", width=self.n, height=self.n, cursor="top_left_corner")
        self.tr = tk.Frame(self, bg="#ff0000", width=self.n, height=self.n, cursor="top_right_corner")
        self.bl = tk.Frame(self, bg="#ff0000", width=self.n, height=self.n, cursor="bottom_left_corner")
        self.br = tk.Frame(self, bg="#ff0000", width=self.n, height=self.n, cursor="bottom_right_corner")
        self.mm = tk.Frame(self, bg="#808080", width=res[0], height=res[1], cursor="fleur")
        self.nonce = tk.Frame(self.mm, bg="#000000", width=8 * len, height=8 * len)
        self.tl.grid(row=0, column=0, sticky="nw")
        self.tm.grid(row=0, column=1, sticky="ew")
        self.tr.grid(row=0, column=2, sticky="ne")
        self.ml.grid(row=1, column=0, sticky="ns")
        self.mm.grid(row=1, column=1, sticky="nsew")
        self.mr.grid(row=1, column=2, sticky="ns")
        self.bl.grid(row=2, column=0, sticky="sw")
        self.bm.grid(row=2, column=1, sticky="ew")
        self.br.grid(row=2, column=2, sticky="se")
        self.nonce.place(x=0, y=0)
        self.bind("<ButtonPress-1>", self.click)
        self.bind("<Button1-Motion>", self.drag)
        self.bind("<ButtonRelease-1>", self.release)

    def click(self, event):
        self.x = self.winfo_pointerx()
        self.y = self.winfo_pointery()
        self.l = self.mm.winfo_rootx()
        self.t = self.mm.winfo_rooty()
        self.w = self.mm.winfo_width()
        self.h = self.mm.winfo_height()

    def drag(self, event):
        dx = self.winfo_pointerx() - self.x
        dy = self.winfo_pointery() - self.y
        if event.widget == self.mr or event.widget == self.br or event.widget == self.tr:
            self.mm.configure(width=self.w + dx)
            self.nonce.configure(width=self.a * (self.w + dx))
        if event.widget == self.bm or event.widget == self.bl or event.widget == self.br:
            self.mm.configure(height=self.h + dy)
            self.nonce.configure(height=self.b * (self.h + dy))
        if event.widget == self.ml or event.widget == self.bl or event.widget == self.tl:
            self.mm.configure(width=self.w - dx)
            self.nonce.configure(width=self.a * (self.w - dx))
        if event.widget == self.tm or event.widget == self.tl or event.widget == self.tr:
            self.mm.configure(height=self.h - dy)
            self.nonce.configure(height=self.b * (self.h - dy))
        if event.widget == self.mm or event.widget == self.nonce:
            self.geometry("+{}+{}".format(self.l + dx - self.n, self.t + dy - self.n))
        elif event.widget == self.tl:
            self.geometry("+{}+{}".format(self.l + min(dx, self.w) - self.n, self.t + min(dy, self.h) - self.n))
        elif event.widget == self.tm or event.widget == self.tr:
            self.geometry("+{}+{}".format(self.l - self.n, self.t + min(dy, self.h) - self.n))
        elif event.widget == self.ml or event.widget == self.bl:
            self.geometry("+{}+{}".format(self.l + min(dx, self.w) - self.n, self.t - self.n))

    def release(self, event):
        del self.l
        del self.t
        del self.h
        del self.w
        del self.x
        del self.y

    def grab(self):
        l = self.mm.winfo_rootx()
        t = self.mm.winfo_rooty()
        w = self.mm.winfo_width()
        h = self.mm.winfo_height()
        return ImageGrab.grab((l, t, l + w, t + h))


class Decrypter(tk.Tk):
    def __init__(self, key, len, res):
        super().__init__()
        self.title("Video Decrypter")
        self.resizable(False, False)
        self.label = tk.Label(self, bd=0)
        self.label.pack(fill="both", expand=1)
        self.bind("<Double-Button-1>", self.select)
        self.selecter = Selecter(self, res, len)
        self.key = key
        self.len = len
        self.res = res
        self.after(20, self.refresh)

    def refresh(self):
        iSrc = self.selecter.grab().resize(self.res)
        iDst = decrypt(self.key, iSrc, self.len)
        self.imgtk = ImageTk.PhotoImage(iDst)
        self.label.configure(image=self.imgtk)
        self.after(20, self.refresh)

    def select(self, event=None):
        if self.selecter.mm.cget("bg") == "#808080":
            self.selecter.mm.configure(bg="#000000")
        else:
            self.selecter.mm.configure(bg="#808080")


def main():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="Video Encrypter/Decrypter")
    parser.add_argument("-k", "--key", type=bytes.fromhex, default=bytes(16), help="16/24/32-byte key in hex")
    parser.add_argument("-l", "--len", type=int, default=2, help="ratio of the edge length of each pixel in the nonce marker to each pixel in the ciphertext (default: 2)")
    parser.add_argument("-r", "--res", type=int, required=True, nargs=2, metavar=("WIDTH", "HEIGHT"), help="ciphertext resolution")
    args = parser.parse_args()
    Decrypter(args.key, args.len, args.res).mainloop()


if __name__ == "__main__":
    main()
