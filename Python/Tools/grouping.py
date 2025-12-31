#!/usr/bin/env python3

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Hashable, Sequence


@dataclass
class Comparator(ABC):
    @abstractmethod
    def key(self, filepath: Path) -> Hashable: ...

    def group(self, filepaths: Sequence[Path]) -> list[list[Path]]:
        groups: dict[Hashable, list[Path]] = {}
        for path in filepaths:
            k = self.key(path)
            groups.setdefault(k, []).append(path)
        return list(groups.values())


@dataclass
class SizeComparator(Comparator):
    def key(self, filepath: Path) -> int:
        return filepath.stat().st_size


@dataclass
class HeadHashComparator(Comparator):
    size: int = 4096
    algo: str = "sha1"

    def key(self, filepath: Path) -> str:
        h = hashlib.new(self.algo)
        with filepath.open("rb") as f:
            chunk = f.read(self.size)
            h.update(chunk)
        return h.hexdigest()


@dataclass
class FullHashComparator(Comparator):
    algo: str = "sha1"

    def key(self, filepath: Path) -> str:
        h = hashlib.new(self.algo)
        with filepath.open("rb") as f:
            while True:
                chunk = f.read(4096)
                h.update(chunk)
                if len(chunk) < 4096:
                    break
        return h.hexdigest()


@dataclass
class ByteByByteComparator(Comparator):
    def key(self, filepath: Path) -> bytes:
        with filepath.open("rb") as f:
            return f.read()


def collect_files(root_dir: Path, recursive: bool = True) -> list[Path]:
    if not root_dir.is_dir():
        raise ValueError(f"{root_dir} is not a valid directory.")
    if recursive:
        return [p for p in root_dir.rglob("*") if p.is_file()]
    else:
        return [p for p in root_dir.glob("*") if p.is_file()]


def compare_pipeline(group: list[Path], comparators: list[Comparator]) -> list[list[Path]]:
    filtered_groups: list[list[Path]] = [group] if len(group) > 1 else []
    for comp in comparators:
        print(f"Using comparator: {comp} for remaining {sum(map(len, filtered_groups))} files")
        splitted_groups = sum(map(comp.group, filtered_groups), [])
        filtered_groups = [group for group in splitted_groups if len(group) > 1]
    return filtered_groups


def print_duplicate_groups(duplicate_groups: list[list[Path]]) -> None:
    if not duplicate_groups:
        print("No duplicate files found.")
        return
    print("Duplicate files:")
    for i, group in enumerate(duplicate_groups, 1):
        print(f"Group {i}:")
        for path in group:
            print(f"  {path}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Find duplicate files in a directory (modular & extensible, pathlib version).")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--recursive", "-r", action="store_true", help="Scan subdirectories")
    parser.add_argument("--show-empty", action="store_true", help="Show empty files as duplicates")
    parser.add_argument("--hash-algo", "-a", default="sha1", help="Hash algorithm (default sha1)")
    parser.add_argument("--head-bytes", "-n", type=int, nargs="*", default=[4096], help="List of head byte sizes to use for hashing (default: 4096)")
    parser.add_argument("--byte-compare", "-b", action="store_true", help="Add final byte-by-byte comparison")

    args = parser.parse_args()

    root = Path(args.directory)
    files = collect_files(root, recursive=args.recursive)
    print(f"Found {len(files)} files in {root}.")

    if not args.show_empty:
        files = [f for f in files if f.stat().st_size > 0]

    comparators: list[Comparator] = []
    comparators.append(SizeComparator())
    for head_bytes in args.head_bytes:
        comparators.append(HeadHashComparator(size=head_bytes, algo=args.hash_algo))
    comparators.append(FullHashComparator(algo=args.hash_algo))
    if args.byte_compare:
        comparators.append(ByteByByteComparator())

    duplicate_groups = compare_pipeline(files, comparators)
    print_duplicate_groups(duplicate_groups)


if __name__ == "__main__":
    main()
