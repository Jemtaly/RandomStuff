#!/usr/bin/python3
def tpoint(t, p, q):
    return tuple(x * (1 - t) + y * t for x, y in zip(p, q))
def bpoint(t, points):
    return points[0] if len(points) == 1 else bpoint(t, [tpoint(t, p, q) for p, q in zip(points[:-1], points[1:])])
def bezier(n, points):
    return [bpoint(i / (n - 1), points) for i in range(n)]
def main():
    import turtle
    points = []
    def leftclick(x, y):
        turtle.goto(x, y)
        turtle.write(turtle.pos())
        points.append(turtle.pos())
    def rightclick(x, y):
        turtle.onscreenclick(None, 1)
        turtle.onscreenclick(None, 3)
        curve = bezier(256, points)
        turtle.penup()
        turtle.pencolor('red')
        turtle.goto(curve[0])
        turtle.pendown()
        for p in curve[1:]:
            turtle.goto(p)
    turtle.hideturtle()
    turtle.speed(0)
    turtle.write(turtle.pos())
    points.append(turtle.pos())
    turtle.onscreenclick(leftclick, 1)
    turtle.onscreenclick(rightclick, 3)
    turtle.done()
if __name__ == '__main__':
    main()
