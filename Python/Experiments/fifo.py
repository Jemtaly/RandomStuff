#!/usr/bin/env python3


import collections
import contextlib
import threading


class Signal:
    def __init__(self, *exc):
        self.type, self.value, self.traceback = exc


class Putter:
    def __init__(self, cond, queue, broken):
        self.cond = cond
        self.queue = queue
        self.broken = broken
        self.context = False

    def __enter__(self):
        if self.context:
            raise RuntimeError
        self.context = True

    def __exit__(self, *exc):
        with self.cond:
            self.queue.append(Signal(*exc))
            self.cond.notify()

    def __call__(self, data):
        with self.cond:
            if isinstance(self.broken[0], Signal):
                raise BrokenPipeError if self.broken[0].type is None else RuntimeError from self.broken[0].value
            self.queue.append(data)
            self.cond.notify()


class Getter:
    def __init__(self, cond, queue, broken):
        self.cond = cond
        self.queue = queue
        self.broken = broken
        self.context = False

    def __enter__(self):
        if self.context:
            raise RuntimeError
        self.context = True

    def __exit__(self, *exc):
        with self.cond:
            self.broken[0] = Signal(*exc)

    def __iter__(self):
        return self

    def __next__(self):
        with self.cond:
            while not self.queue:
                self.cond.wait()
            if isinstance(self.queue[0], Signal):
                raise StopIteration if self.queue[0].type is None else RuntimeError from self.queue[0].value
            return self.queue.popleft()


def mkfifo(Deque=collections.deque):
    cond = threading.Condition()
    queue = Deque()
    broken = [None]
    return Getter(cond, queue, broken), Putter(cond, queue, broken)


def foreground(func):
    def wrapper(*args, **kwargs):
        with contextlib.ExitStack() as stack:
            for arg in *args, *kwargs.values():
                if isinstance(arg, Putter | Getter):
                    stack.enter_context(arg)
            func(*args, **kwargs)

    return wrapper


def background(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=foreground(func), args=args, kwargs=kwargs).start()

    return wrapper


@background
def tee(getter, *putters):
    for i in getter:
        for putter in putters:
            putter(i)


@background
def producer(putter):
    for i in range(10):
        putter(i)


@background
def consumer(j, getter):
    for i in getter:
        print(f"consumer {j}: {i}")


def main():
    putters = []
    for j in range(10):
        getter, putter = mkfifo()
        consumer(j, getter)
        putters.append(putter)
    getter, putter = mkfifo()
    tee(getter, *putters)
    producer(putter)


if __name__ == "__main__":
    main()
