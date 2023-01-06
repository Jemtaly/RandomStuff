import functools
class View:
    def __init__(self):
        pass
    def __call__(self, range):
        pass
class FilterView(View):
    def __init__(self, func):
        self.func = func
    def __call__(self, range):
        return Range(*filter(self.func, range.args))
class MapView(View):
    def __init__(self, func):
        self.func = func
    def __call__(self, range):
        return Range(*map(self.func, range.args))
class ReduceView(View):
    def __init__(self, func):
        self.func = func
    def __call__(self, range):
        return functools.reduce(self.func, range.args)
class Range:
    def __init__(self, *args):
        self.args = args
    def __or__(self, rval):
        return rval(self)
    def __repr__(self):
        return "Range({})".format(", ".join(map(str, self.args)))
