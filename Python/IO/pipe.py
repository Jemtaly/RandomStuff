import os
import socket
import threading
from typing import Any, Callable, Protocol, ParamSpec, TypeVar


P = ParamSpec("P")  # Parameters for the callable
Q = TypeVar("Q", covariant=True)  # Return type of the callable
R = TypeVar("R", covariant=True)  # Intermediate return type of the async callable


class AsyncCallable(Protocol[P, Q, R]):
    def __call__(
        self,
        on_success: Callable[[Q], Any],
        on_failure: Callable[[Exception], Any],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R: ...


def make_async(sync_callable: Callable[P, Q]) -> AsyncCallable[P, Q, None]:
    def async_callable(
        on_success: Callable[[Q], Any],
        on_failure: Callable[[Exception], Any],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        def target() -> None:
            try:
                res = sync_callable(*args, **kwargs)
            except Exception as err:
                on_failure(err)
            else:
                on_success(res)

        threading.Thread(target=target, daemon=False).start()

    return async_callable


class Readable(Protocol):
    def read(self, size: int, /) -> bytes: ...
    def close(self) -> None: ...


class Writable(Protocol):
    def write(self, data: bytes, /) -> Any: ...
    def flush(self) -> None: ...
    def close(self) -> None: ...


class AsyncWriter(Protocol[P, Q, R]):
    def __call__(
        self,
        on_success: Callable[[Q], Any],
        on_failure: Callable[[Exception], Any],
        writable: Writable,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R: ...


class AsyncReader(Protocol[P, Q, R]):
    def __call__(
        self,
        on_success: Callable[[Q], Any],
        on_failure: Callable[[Exception], Any],
        readable: Readable,
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R: ...


def async_writer_to_readable(
    async_writer: AsyncWriter[P, Q, R],
    r_buffering: int = -1,
    w_buffering: int = 0,
) -> tuple[Readable, AsyncCallable[P, Q, R]]:
    r_fd, w_fd = os.pipe()
    readable = os.fdopen(r_fd, "rb", buffering=r_buffering)
    writable = os.fdopen(w_fd, "wb", buffering=w_buffering)
    used = False

    def wrapped_async_writer(
        on_success: Callable[[Q], Any],
        on_failure: Callable[[Exception], Any],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        nonlocal used
        if used:
            raise RuntimeError("This async writer has already been used once.")
        used = True
        return async_writer(
            lambda res: writable.close() or on_success(res),
            lambda err: writable.close() or on_failure(err),
            writable,
            *args,
            **kwargs,
        )

    return readable, wrapped_async_writer


def async_reader_to_writable(
    async_reader: AsyncReader[P, Q, R],
    r_buffering: int = -1,
    w_buffering: int = 0,
) -> tuple[Writable, AsyncCallable[P, Q, R]]:
    r_fd, w_fd = os.pipe()
    readable = os.fdopen(r_fd, "rb", buffering=r_buffering)
    writable = os.fdopen(w_fd, "wb", buffering=w_buffering)
    used = False

    def wrapped_async_reader(
        on_success: Callable[[Q], Any],
        on_failure: Callable[[Exception], Any],
        /,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R:
        nonlocal used
        if used:
            raise RuntimeError("This async reader has already been used once.")
        used = True
        return async_reader(
            lambda res: readable.close() or on_success(res),
            lambda err: readable.close() or on_failure(err),
            readable,
            *args,
            **kwargs,
        )

    return writable, wrapped_async_reader


class SocketReadable:
    def __init__(self, sock: socket.socket, buffering: int = -1):
        self.sock = sock
        self.file = sock.makefile("rb", buffering=buffering)

    def read(self, size: int, /) -> bytes:
        return self.file.read(size)

    def close(self) -> None:
        self.file.close()
        self.sock.shutdown(socket.SHUT_RD)


class SocketWritable:
    def __init__(self, sock: socket.socket, buffering: int = -1):
        self.sock = sock
        self.file = sock.makefile("wb", buffering=buffering)

    def write(self, data: bytes, /) -> Any:
        return self.file.write(data)

    def flush(self) -> None:
        self.file.flush()

    def close(self) -> None:
        self.file.close()
        self.sock.shutdown(socket.SHUT_WR)


def main():
    def fork(*writables: Writable, readable: Readable) -> int:
        i = 0
        while c := readable.read(1):
            for writable in writables:
                writable.write(c)
                writable.flush()
            i += 1
        return i

    async_fork = make_async(fork)

    readables: list[Readable] = []
    for _ in range(3):
        readable, async_fork = async_writer_to_readable(async_fork)
        readables.append(readable)

    def fill(writable: Writable, data: bytes, interval: float = 1) -> int:
        import time

        i = 0
        for byte in data:
            time.sleep(interval)
            writable.write(byte.to_bytes(1, "big"))
            writable.flush()
            i += 1

        return i

    async_fill = make_async(fill)
    readable, async_callable = async_writer_to_readable(async_fill)

    # start filling the readable
    async_callable(
        lambda res: print(f"Filled with {res} bytes"),
        lambda err: print(f"Error: {err}"),
        b"Hello, World!",
    )

    # start reading from the readable
    async_fork(
        lambda res: print(f"Read {res} bytes from readable"),
        lambda err: print(f"Error: {err}"),
        readable=readable,
    )

    print(readables[0].read(3))
    print(readables[1].read(2))
    print(readables[2].read(7))
    print(readables[2].read(7))


if __name__ == "__main__":
    main()
