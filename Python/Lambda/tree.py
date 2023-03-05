#!/usr/bin/python3
import sys, copy
sys.setrecursionlimit(0x1000000)
defs = {}
sets = {}
oprs = {
    '+': int.__add__,
    '-': int.__sub__,
    '*': int.__mul__,
    '/': int.__floordiv__,
    '%': int.__mod__,
}
cmps = {
    '=': int.__eq__,
    '>': int.__gt__,
    '<': int.__lt__,
}
def read(str):
    start = 0
    while start < len(str) and str[start] == ' ':
        start += 1
    stop = start
    count = 0
    while stop < len(str):
        if count == 0 and str[stop] == ' ':
            break
        elif str[stop] == '(' or str[stop] == '[':
            count += 1
        elif str[stop] == ')' or str[stop] == ']':
            count -= 1
        stop += 1
    return str[start:stop], str[stop:]
class Expr:
    def __init__(self, type, data):
        self.type = type
        self.data = data
        self.done = False
    def fromstr(str):
        sym, str = read(str)
        if len(sym) == 0:
            return Expr(type = 's', data = 'NULL')
        elif sym[0] == '$' and len(sym) == 2:
            tmp = Expr(type = '$', data = sym[1:])
        elif sym[0] == '(' and sym[-1] == ')':
            tmp = Expr.fromstr(sym[1:-1])
        elif sym[0] == '[' and sym[-1] == ']':
            tmp = Expr(type = '^', data = Expr.fromstr(sym[1:-1]))
        elif sym[0] == '!':
            tmp = Expr(type = '!', data = sym[1:])
        elif sym[0] == '&':
            tmp = Expr(type = '&', data = sym[1:])
        elif sym[0] in oprs and len(sym) == 1:
            tmp = Expr(type = 'o', data = oprs[sym[0]])
        elif sym[0] in cmps and len(sym) == 1:
            tmp = Expr(type = 'c', data = cmps[sym[0]])
        else:
            try:
                tmp = Expr(type = 'i', data = int(sym))
            except:
                tmp = Expr(type = 's', data = sym)
        while True:
            sym, str = read(str)
            if len(sym) == 0:
                return tmp
            tmp = Expr(type = '|', data = (tmp, Expr.fromstr(sym)))
    def exprcal(self):
        match self.type:
            case '#':
                if not self.data.done:
                    self.data.exprcal()
                self.__dict__ = copy.deepcopy(self.data).__dict__
            case '!':
                self.__dict__ = copy.deepcopy(sets.get(self.data, Expr(type = 's', data = 'NULL'))).__dict__
            case '&':
                self.__dict__ = copy.deepcopy(defs.get(self.data, Expr(type = 's', data = 'NULL'))).__dict__
                self.exprcal()
            case '|':
                self.data[0].exprcal()
                if self.data[0].type == '^':
                    self.data[0].data.fnapply(self.data[1], 'a')
                    self.data[0].data.exprcal()
                    self.__dict__ = self.data[0].data.__dict__
                else:
                    self.data[1].exprcal()
                    if self.data[1].type == 'i':
                        match self.data[0].type:
                            case 'o':
                                self.__dict__.update(type = 'O', data = (self.data[0].data, self.data[1].data))
                            case 'O':
                                self.__dict__.update(type = 'i', data = self.data[0].data[0](self.data[1].data, self.data[0].data[1]))
                            case 'c':
                                self.__dict__.update(type = 'C', data = (self.data[0].data, self.data[1].data))
                            case 'C':
                                self.__dict__.update(
                                    type = '^', data = Expr(
                                    type = '^', data = Expr(
                                    type = '$', data = 'b' if self.data[0].data[0](self.data[1].data, self.data[0].data[1]) else 'a')))
        self.done = True
    def fnapply(self, arg, c):
        if self.type == '$' and self.data == c:
            self.type = '#'
            self.data = arg
        if self.type == '^':
            self.data.fnapply(arg, chr(ord(c) + 1))
        if self.type == '|':
            self.data[0].fnapply(arg, c)
            self.data[1].fnapply(arg, c)
    def __str__(self, brackets = False):
        match self.type:
            case 'o':
                return list(oprs.keys())[list(oprs.values()).index(self.data)]
            case 'O':
                return list(oprs.keys())[list(oprs.values()).index(self.data[0])] + ':' + str(self.data[1])
            case 'c':
                return list(cmps.keys())[list(cmps.values()).index(self.data)]
            case 'C':
                return list(cmps.keys())[list(cmps.values()).index(self.data[0])] + ':' + str(self.data[1])
            case '^':
                return '[' + str(self.data) + ']'
            case '$':
                return '$' + self.data
            case '#':
                return str(self.data)
            case '!':
                return '!' + self.data
            case '&':
                return '&' + self.data
            case 'i':
                return str(self.data)
            case 's':
                return self.data
            case '|':
                return ('({})' if brackets else '{}').format(self.data[0].__str__(False) + ' ' + self.data[1].__str__(True))
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
        buf, str = read(line)
        match buf:
            case 'cal':
                exp = Expr.fromstr(str)
                exp.exprcal()
                sets[''] = exp
                print(ps_out, file = sys.stderr, end = '', flush = True)
                print(exp)
            case 'fmt':
                exp = Expr.fromstr(str)
                defs[''] = exp
                print(ps_out, file = sys.stderr, end = '', flush = True)
                print(exp)
            case 'set':
                buf, str = read(str)
                if buf:
                    exp = Expr.fromstr(str)
                    exp.exprcal()
                    sets[buf] = exp
            case 'def':
                buf, str = read(str)
                if buf:
                    exp = Expr.fromstr(str)
                    defs[buf] = exp
            case 'clr':
                sets.clear()
                defs.clear()
            case 'dir':
                for buf, exp in sets.items():
                    print(ps_out, file = sys.stderr, end = '', flush = True)
                    print('!{:8s}'.format(buf if len(buf) <= 8 else buf[0:6] + '..'), exp)
                for buf, exp in defs.items():
                    print(ps_out, file = sys.stderr, end = '', flush = True)
                    print('&{:8s}'.format(buf if len(buf) <= 8 else buf[0:6] + '..'), exp)
if __name__ == '__main__':
    main()
