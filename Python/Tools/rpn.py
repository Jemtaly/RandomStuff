#!/usr/bin/python3
import sys
oprs = {
    '+': int.__add__,
    '-': int.__sub__,
    '*': int.__mul__,
    '/': int.__floordiv__,
    '%': int.__mod__,
}
def RPN(expression):
    stack = []
    for token in expression.split():
        if token in oprs:
            b = stack.pop()
            a = stack.pop()
            stack.append(oprs[token](a, b))
        else:
            stack.append(int(token))
    return stack.pop()
def main():
    ps_in = '>> ' if sys.stderr.isatty() and sys.stdin.isatty() else ''
    ps_out = '=> ' if sys.stderr.isatty() and sys.stdout.isatty() else ''
    lf = True
    while lf:
        print(ps_in, file = sys.stderr, end = '', flush = True)
        line = sys.stdin.readline()
        if line and line[-1] == '\n':
            line = line[:-1]
        else:
            lf = False
            if sys.stderr.isatty() and sys.stdin.isatty():
                print(file = sys.stderr)
        if line.strip():
            out = RPN(line)
            print(ps_out, file = sys.stderr, end = '', flush = True)
            print(out)
if __name__ == '__main__':
    main()
