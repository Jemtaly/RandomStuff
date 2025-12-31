#!/usr/bin/env python3

import argparse
import turtle as tt


class StoreKVPairs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        result = {}
        for value in values:
            k, _, v = value.partition("=")
            result[k] = v
        setattr(namespace, self.dest, result)


class LSystem:
    def __init__(self, start: str, rules: dict[str, str]):
        self.start = start
        self.rules = rules

    def generate(self, n: int) -> str:
        if n == 0:
            return self.start
        last = self.generate(n - 1)
        return "".join(self.rules.get(x, x) for x in last)


def draw(turtle: tt.Turtle, sentence: str, instructions: dict[str, str], length: float, angle: float):
    stack = []
    turtle.penup()
    for x in sentence:
        for c in instructions[x]:
            if c == "0":
                turtle.forward(length)
            elif c == "1":
                turtle.pendown()
                turtle.forward(length)
                turtle.penup()
            elif c == "<":
                turtle.left(angle)
            elif c == ">":
                turtle.right(angle)
            elif c == "[":
                position = turtle.position()
                heading = turtle.heading()
                stack.append((position, heading))
            elif c == "]":
                position, heading = stack.pop()
                turtle.goto(position)
                turtle.setheading(heading)
            else:
                raise ValueError(f"Invalid character: {c}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", required=True)
    parser.add_argument("-r", "--rules", action=StoreKVPairs, nargs="*", default={})
    parser.add_argument("-i", "--instructions", action=StoreKVPairs, nargs="*", default={})
    parser.add_argument("-n", "--iterations", type=int, default=0)
    parser.add_argument("-l", "--length", type=float, default=0)
    parser.add_argument("-a", "--angle", type=float, default=90)
    parser.add_argument("-I", "--immediate", action="store_true")
    args = parser.parse_args()
    sentence = LSystem(args.start, args.rules).generate(args.iterations)
    turtle = tt
    if args.immediate:
        turtle.tracer(0, 0)
    draw(turtle, sentence, args.instructions, args.length, args.angle)
    turtle.hideturtle()
    turtle.mainloop()


if __name__ == "__main__":
    main()

# Example usage:
# py lindenmayer.py -s "0" -r "1=11" "0=1{0}0" -i "0=1" "1=1" "{=[<" "}=]>" -a 45 -l 5 -n 5
# py lindenmayer.py -s "A" -r "A=B<A<B" "B=A>B>A" -i "A=1" "B=1" "<=<" ">=>" -a 60 -l 5 -n 5
# py lindenmayer.py -s "F" -r "F=F>G" "G=F<G" -i "F=1" "G=1" "<=<" ">=>" -a 90 -l 5 -n 8
