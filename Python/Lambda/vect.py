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
        self.vect = list()
        self.done = False
    def fromstr(str):
        sym, str = read(str)
        if len(sym) == 0:
            return Expr(type = 's', data = 'NULL')
        def fun():
            if sym[0] == '$' and len(sym) == 2:
                return Expr(type = '$', data = sym[1:])
            if sym[0] == '(' and sym[-1] == ')':
                return Expr.fromstr(sym[1:-1])
            if sym[0] == '[' and sym[-1] == ']':
                return Expr(type = '^', data = Expr.fromstr(sym[1:-1]))
            if sym[0] == '!':
                return Expr(type = '!', data = sym[1:])
            if sym[0] == '&':
                return Expr(type = '&', data = sym[1:])
            if sym[0] in oprs and len(sym) == 1:
                return Expr(type = 'o', data = oprs[sym[0]])
            if sym[0] in cmps and len(sym) == 1:
                return Expr(type = 'c', data = cmps[sym[0]])
            try:
                return Expr(type = 'i', data = int(sym))
            except:
                return Expr(type = 's', data = sym)
        res = fun()
        while True:
            sym, str = read(str)
            if len(sym) == 0:
                return res
            res.vect.append(fun())
    def exprcal(self):
        vect, self.vect, self.done = self.vect, list(), True
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
        for arg in vect:
            if self.type == '^':
                self.__dict__ = self.data.__dict__
                self.fnapply(arg, 'a')
                self.exprcal()
            else:
                arg.exprcal()
                if arg.type == 'i' and len(self.vect) == 0:
                    match self.type:
                        case 'o':
                            self.__dict__.update(type = 'O', data = (self.data, arg.data))
                        case 'O':
                            self.__dict__.update(type = 'i', data = self.data[0](arg.data, self.data[1]))
                        case 'c':
                            self.__dict__.update(type = 'C', data = (self.data, arg.data))
                        case 'C':
                            self.__dict__.update(
                                type = '^', data = Expr(
                                type = '^', data = Expr(
                                type = '$', data = 'b' if self.data[0](arg.data, self.data[1]) else 'a')))
                        case _:
                            self.vect.append(arg)
                else:
                    self.vect.append(arg)
    def fnapply(self, arg, c):
        if self.type == '$' and self.data == c:
            self.type = '#'
            self.data = arg
        if self.type == '^':
            self.data.fnapply(arg, chr(ord(c) + 1))
        for i in self.vect:
            i.fnapply(arg, c)
    def __str__(self, brackets = False):
        match self.type:
            case 'o':
                s = list(oprs.keys())[list(oprs.values()).index(self.data)]
            case 'O':
                s = list(oprs.keys())[list(oprs.values()).index(self.data[0])] + ':' + str(self.data[1])
            case 'c':
                s = list(cmps.keys())[list(cmps.values()).index(self.data)]
            case 'C':
                s = list(cmps.keys())[list(cmps.values()).index(self.data[0])] + ':' + str(self.data[1])
            case '^':
                s = '[' + str(self.data) + ']'
            case '$':
                s = '$' + self.data
            case '#':
                s = str(self.data)
            case '!':
                s = '!' + self.data
            case '&':
                s = '&' + self.data
            case 'i':
                s = str(self.data)
            case 's':
                s = self.data
        return s if len(self.vect) == 0 else ('({})' if brackets else '{}').format(s + ' ' + ' '.join([i.__str__(True) for i in self.vect]))
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
