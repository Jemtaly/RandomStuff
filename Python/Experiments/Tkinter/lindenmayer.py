#!/usr/bin/python3
import turtle
import argparse
class StoreKVPairs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string = None):
        result = {}
        for value in values:
            k, _, v = value.partition('=')
            result[k] = v
        setattr(namespace, self.dest, result)
def generate(start, rules, final, iterations):
    sentence = start
    for _ in range(iterations):
        sentence = ''.join(rules.get(c, c) for c in sentence)
    sentence = ''.join(final.get(c, c) for c in sentence)
    return sentence
def draw(turtle, sentence, length, angle):
    stack = []
    turtle.penup()
    for c in sentence:
        if c == '0':
            turtle.forward(length)
        elif c == '1':
            turtle.pendown()
            turtle.forward(length)
            turtle.penup()
        elif c == '<':
            turtle.left(angle)
        elif c == '>':
            turtle.right(angle)
        elif c == '[':
            position = turtle.position()
            heading = turtle.heading()
            stack.append((position, heading))
        elif c == ']':
            position, heading = stack.pop()
            turtle.goto(position)
            turtle.setheading(heading)
        else:
            raise ValueError(f'Invalid character: {c}')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start', required = True)
    parser.add_argument('-r', '--rules', action = StoreKVPairs, nargs = '*', default = {})
    parser.add_argument('-f', '--final', action = StoreKVPairs, nargs = '*', default = {})
    parser.add_argument('-n', '--iterations', type = int, default = 0)
    parser.add_argument('-l', '--length', type = float, default = 0)
    parser.add_argument('-a', '--angle', type = float, default = 90)
    parser.add_argument('-i', '--immediate', action = 'store_true')
    args = parser.parse_args()
    sentence = generate(args.start, args.rules, args.final, args.iterations)
    if args.immediate:
        turtle.tracer(0, 0)
    draw(turtle, sentence, args.length, args.angle)
    turtle.hideturtle()
    turtle.mainloop()
if __name__ == '__main__':
    main()
