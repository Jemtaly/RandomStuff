#!/usr/bin/env python3

from dataclasses import dataclass, field
from fusepy import Operations, FuseOSError, errno, FUSE
from typing import BinaryIO


def split_path(path: str) -> list[str]:
    if path == "/":
        return []
    return path.strip("/").split("/")


def dump_bytes(buffer: BinaryIO, data: bytes, *, length: int) -> None:
    size = len(data)
    buffer.write(size.to_bytes(length, "big"))
    buffer.write(data)


def load_bytes(buffer: BinaryIO, *, length: int) -> bytes:
    size = int.from_bytes(buffer.read(length), "big")
    return buffer.read(size)


@dataclass
class Node:
    def get_node(self, *path: str) -> "Node":
        if not path:
            return self
        if not isinstance(self, Directory):
            raise FuseOSError(errno.ENOTDIR)
        part, *rest = path
        if part not in self.children:
            raise FuseOSError(errno.ENOENT)
        return self.children[part].get_node(*rest)


@dataclass
class Directory(Node):
    children: dict[str, Node] = field(default_factory=dict[str, Node])

    @property
    def count(self) -> int:
        return len(self.children)

    def add_node(self, *path: str, node: Node) -> None:
        if not path:
            raise FuseOSError(errno.EEXIST)
        part, *rest = path
        if not rest:
            if part in self.children:
                raise FuseOSError(errno.EEXIST)
            self.children[part] = node
        else:
            if part not in self.children:
                raise FuseOSError(errno.ENOENT)
            child = self.children[part]
            if not isinstance(child, Directory):
                raise FuseOSError(errno.ENOTDIR)
            return child.add_node(*rest, node=node)

    def pop_node(self, *path: str) -> Node:
        if not path:
            raise FuseOSError(errno.EINVAL)
        part, *rest = path
        if not rest:
            if part not in self.children:
                raise FuseOSError(errno.ENOENT)
            return self.children.pop(part)
        else:
            if part not in self.children:
                raise FuseOSError(errno.ENOENT)
            child = self.children[part]
            if not isinstance(child, Directory):
                raise FuseOSError(errno.ENOTDIR)
            return child.pop_node(*rest)

    def dump(self, buffer: BinaryIO):
        buffer.write(len(self.children).to_bytes(4, "big"))
        for name, child in self.children.items():
            dump_bytes(buffer, name.encode("utf-8"), length=2)
            if isinstance(child, Directory):
                buffer.write(b"D")
                child.dump(buffer)
            elif isinstance(child, File):
                buffer.write(b"F")
                child.dump(buffer)
            else:
                raise ValueError("Unknown node type")

    @classmethod
    def load(cls, buffer: BinaryIO):
        count = int.from_bytes(buffer.read(4), "big")
        children = {}
        for _ in range(count):
            name = load_bytes(buffer, length=2).decode("utf-8")
            kind = buffer.read(1)
            if kind == b"D":
                child = Directory.load(buffer)
            elif kind == b"F":
                child = File.load(buffer)
            else:
                raise ValueError("Unknown node type")
            children[name] = child
        return cls(children=children)


@dataclass
class File(Node):
    content: bytearray = field(default_factory=bytearray)

    @property
    def size(self) -> int:
        return len(self.content)

    def read(self, size: int, offset: int) -> bytes:
        data = self.content[offset : offset + size]
        return bytes(data)

    def write(self, data: bytes, offset: int) -> int:
        size = len(data)
        self.content[offset : offset + size] = data
        return size

    def truncate(self, size: int):
        cont = len(self.content)
        if size <= cont:
            self.content = self.content[:size]
        else:
            self.content.extend(b"\x00" * (size - cont))

    def dump(self, buffer: BinaryIO):
        dump_bytes(buffer, bytes(self.content), length=8)

    @classmethod
    def load(cls, buffer: BinaryIO):
        content = bytearray(load_bytes(buffer, length=8))
        return cls(content=content)


class MyFS(Operations):
    def __init__(self, root: Directory):
        self.root = root

    def getattr(self, path: str, fh: int | None = None):
        parts = split_path(path)
        try:
            node = self.root.get_node(*parts)
        except FuseOSError as e:
            raise e
        attr = {
            "st_uid": 1000,
            "st_gid": 1000,
            "st_atime": 0,
            "st_mtime": 0,
            "st_ctime": 0,
        }
        if isinstance(node, Directory):
            attr.update(
                {
                    "st_mode": 0o40755,
                    "st_nlink": 2 + node.count,
                    "st_size": 0,
                }
            )
        elif isinstance(node, File):
            attr.update(
                {
                    "st_mode": 0o100644,
                    "st_nlink": 1,
                    "st_size": node.size,
                }
            )
        else:
            raise FuseOSError(errno.ENOENT)
        return attr

    def readdir(self, path: str, fh: int):
        parts = split_path(path)
        try:
            node = self.root.get_node(*parts)
        except FuseOSError as e:
            raise e
        if not isinstance(node, Directory):
            raise FuseOSError(errno.ENOTDIR)
        return [".", ".."] + list(node.children.keys())

    def mkdir(self, path: str, mode: int):
        parts = split_path(path)
        try:
            self.root.add_node(*parts, node=Directory())
        except FuseOSError as e:
            raise e
        return 0

    def rmdir(self, path: str):
        parts = split_path(path)
        try:
            self.root.pop_node(*parts)
        except FuseOSError as e:
            raise e
        return 0

    def create(self, path: str, mode: int, fi: int | None = None):
        parts = split_path(path)
        try:
            self.root.add_node(*parts, node=File())
        except FuseOSError as e:
            raise e
        return 0

    def unlink(self, path: str):
        parts = split_path(path)
        try:
            self.root.pop_node(*parts)
        except FuseOSError as e:
            raise e
        return 0

    def rename(self, old: str, new: str):
        old_parts = split_path(old)
        new_parts = split_path(new)
        try:
            node = self.root.pop_node(*old_parts)
            self.root.add_node(*new_parts, node=node)
        except FuseOSError as e:
            raise e
        return 0

    def read(self, path: str, size: int, offset: int, fh: int):
        parts = split_path(path)
        try:
            node = self.root.get_node(*parts)
        except FuseOSError as e:
            raise e
        if not isinstance(node, File):
            raise FuseOSError(errno.EISDIR)
        return node.read(size, offset)

    def write(self, path: str, data: bytes, offset: int, fh: int):
        parts = split_path(path)
        try:
            node = self.root.get_node(*parts)
        except FuseOSError as e:
            raise e
        if not isinstance(node, File):
            raise FuseOSError(errno.EISDIR)
        return node.write(data, offset)

    def truncate(self, path: str, length: int, fh: int | None = None):
        parts = split_path(path)
        try:
            node = self.root.get_node(*parts)
        except FuseOSError as e:
            raise e
        if not isinstance(node, File):
            raise FuseOSError(errno.EISDIR)
        node.truncate(length)
        return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("mountpoint", type=str, help="Mount point")
    parser.add_argument("--load", type=str, help="Load from file")
    parser.add_argument("--dump", type=str, help="Dump to file")
    args = parser.parse_args()

    if args.load:
        with open(args.load, "rb") as f:
            root = Directory.load(f)
    else:
        root = Directory()
    fuse = FUSE(MyFS(root), args.mountpoint, foreground=True)
    if args.dump:
        with open(args.dump, "wb") as f:
            root.dump(f)
