#!/usr/bin/python3
def tpoint(t, p, q):
    return tuple(x * (1 - t) + z * t for x, z in zip(p, q))
def bpoint(t, points):
    return points[0] if len(points) == 1 else bpoint(t, [tpoint(t, p, q) for p, q in zip(points[:-1], points[1:])])
def bezier(n, points):
    return [bpoint(i / (n - 1), points) for i in range(n)]
def main():
    import tkinter
    tk = tkinter.Tk()
    tk.title('Bezier')
    canvas = tkinter.Canvas(tk)
    canvas.pack(fill = tkinter.BOTH, expand = True)
    def init_canvas(event = None):
        global points
        points = []
        canvas.delete(tkinter.ALL)
        canvas.bind('<Button-1>', draw_point)
        canvas.bind('<Double-1>', draw_curve)
    def draw_point(event):
        canvas.create_text(event.x, event.y, text = str((event.x, event.y)), fill = 'blue')
        if points:
            canvas.create_line(*points[-1], event.x, event.y)
        points.append((event.x, event.y))
    def draw_curve(event):
        canvas.unbind('<Button-1>')
        canvas.unbind('<Double-1>')
        curve = bezier(256, points)
        canvas.create_line(*curve, fill = 'red')
    canvas.bind('<Button-3>', init_canvas)
    init_canvas()
    tk.mainloop()
if __name__ == '__main__':
    main()
