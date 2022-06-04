#!/usr/bin/python3
def tpoint(t, p, q):
    return tuple(x * (1 - t) + y * t for x, y in zip(p, q))
def bpoint(t, points):
    return points[0] if len(points) == 1 else bpoint(t, [tpoint(t, p, q) for p, q in zip(points[:-1], points[1:])])
def bezier(n, points):
    return [bpoint(i / (n - 1), points) for i in range(n)]
def main():
    import tkinter
    points = []
    tk = tkinter.Tk()
    canvas = tkinter.Canvas(tk)
    canvas.pack(fill=tkinter.BOTH, expand=True)
    def leftclick(event):
        if points:
            canvas.create_line(*points[-1], event.x, event.y)
        canvas.create_text(event.x, event.y, text=str((event.x, event.y)), fill='blue')
        points.append((event.x, event.y))
    def rightclick(event):
        canvas.unbind('<ButtonPress-1>')
        canvas.unbind('<ButtonPress-3>')
        leftclick(event)
        curve = bezier(256, points)
        for p, q in zip(curve[:-1], curve[1:]):
            canvas.create_line(*p, *q, fill='red')
    canvas.bind('<ButtonPress-1>', leftclick)
    canvas.bind('<ButtonPress-3>', rightclick)
    tk.mainloop()
if __name__ == '__main__':
    main()
