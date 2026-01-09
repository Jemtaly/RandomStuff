#!/usr/bin/env python3

from dataclasses import dataclass
from typing import Callable, TypeVar, ParamSpec, Generic

from collections import deque
from contextlib import ExitStack
from threading import Condition, Thread


@dataclass
class Signal:
    exc_type: type | None
    exc_val: BaseException | None
    exc_tb: object | None


T = TypeVar("T")


class Putter(Generic[T]):
    def __init__(self, cond: Condition, queue: deque[T | Signal], broken: list[Signal | None]):
        self.cond = cond
        self.queue = queue
        self.broken = broken
        self.context = False

    def __enter__(self):
        if self.context:
            raise RuntimeError
        self.context = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.cond:
            self.queue.append(Signal(exc_type, exc_val, exc_tb))
            self.cond.notify()

    def __call__(self, data: T):
        with self.cond:
            if isinstance(self.broken[0], Signal):
                raise BrokenPipeError if self.broken[0].exc_type is None else RuntimeError from self.broken[0].exc_val
            self.queue.append(data)
            self.cond.notify()


class Getter(Generic[T]):
    def __init__(self, cond: Condition, queue: deque[T | Signal], broken: list[Signal | None]):
        self.cond = cond
        self.queue = queue
        self.broken = broken
        self.context = False

    def __enter__(self):
        if self.context:
            raise RuntimeError
        self.context = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.cond:
            self.broken[0] = Signal(exc_type, exc_val, exc_tb)

    def __iter__(self):
        return self

    def __next__(self) -> T:
        with self.cond:
            while not self.queue:
                self.cond.wait()
            if isinstance(self.queue[0], Signal):
                raise StopIteration if self.queue[0].exc_type is None else RuntimeError from self.queue[0].exc_val
            return self.queue.popleft()


def mkfifo(factory: Callable[[], deque[T | Signal]]) -> tuple[Getter[T], Putter[T]]:
    cond = Condition()
    queue = factory()
    broken = [None]
    return Getter(cond, queue, broken), Putter(cond, queue, broken)


P = ParamSpec("P")


def foreground(func: Callable[P, None]) -> Callable[P, None]:
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        with ExitStack() as stack:
            for arg in *args, *kwargs.values():
                if isinstance(arg, Putter | Getter):
                    stack.enter_context(arg)
            func(*args, **kwargs)

    return wrapper


def background(func: Callable[P, None]) -> Callable[P, None]:
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        Thread(target=foreground(func), args=args, kwargs=kwargs).start()

    return wrapper


@background
def tee(getter: Getter[T], *putters: Putter[T]):
    for i in getter:
        for putter in putters:
            putter(i)


@background
def producer(putter: Putter[int]):
    for i in range(10):
        putter(i)


@background
def consumer(j: int, getter: Getter[int]):
    for i in getter:
        print(f"consumer {j}: {i}")


def main():
    putters = []
    for j in range(10):
        getter, putter = mkfifo(deque[int | Signal])
        consumer(j, getter)
        putters.append(putter)
    getter, putter = mkfifo(deque[int | Signal])
    tee(getter, *putters)
    producer(putter)


if __name__ == "__main__":
    main()
