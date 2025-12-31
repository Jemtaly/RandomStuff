#!/usr/bin/env python3

import argparse
from pathlib import Path


TWI = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
T2I = {t: i for i, t in enumerate(TWI)}
LEN = 15
DEC = len(str(64**LEN - 1))


def is_twitter_name(s: str) -> bool:
    return len(s) == LEN and all(c in T2I for c in s)


def is_decimal_name(s: str) -> bool:
    return len(s) == DEC and s.isdigit()


def twitter_decode(s: str) -> int:
    return sum(T2I[c] * 64**i for i, c in zip(range(LEN), reversed(s), strict=True))


def twitter_encode(n: int) -> str:
    return "".join(TWI[n // 64**i % 64] for i in reversed(range(LEN)))


def twitter_decode_str(s: str) -> str:
    return "{:0{width}d}".format(twitter_decode(s), width=DEC)


def twitter_encode_str(n: str) -> str:
    return twitter_encode(int(n))


def twitter_sort(l: list[Path]) -> list[Path]:
    return sorted(l, key=lambda x: twitter_decode(x.stem))


def twitter_decode_file(f: Path) -> Path:
    return f.parent / (twitter_decode_str(f.stem) + f.suffix)


def twitter_encode_file(f: Path) -> Path:
    return f.parent / (twitter_encode_str(f.stem) + f.suffix)


def main():
    parser = argparse.ArgumentParser(description="Sort Twitter-style filenames.")
    subs = parser.add_subparsers(dest="command", required=True)
    parser_sort = subs.add_parser("sort", help="Sort Twitter-style filenames")
    parser_sort.add_argument("files", nargs="*", type=Path, help="Files to sort")
    parser_decode = subs.add_parser("decode", help="Decode Twitter-style filenames to decimal")
    parser_decode.add_argument("files", nargs="*", type=Path, help="Files to decode")
    parser_encode = subs.add_parser("encode", help="Encode decimal filenames to Twitter-style")
    parser_encode.add_argument("files", nargs="*", type=Path, help="Files to encode")
    args = parser.parse_args()

    if args.command == "sort":
        files = [f for f in args.files if is_twitter_name(f.stem)]
        sorted_files = twitter_sort(files)
        for f in sorted_files:
            print(f)
    elif args.command == "decode":
        for f in args.files:
            if is_twitter_name(f.stem):
                g = twitter_decode_file(f)
                print(f"Renaming {f} to {g}")
                f.rename(g)
            else:
                print(f"Skipping {f}, not a Twitter-style filename")
    elif args.command == "encode":
        for f in args.files:
            if is_decimal_name(f.stem):
                g = twitter_encode_file(f)
                print(f"Renaming {f} to {g}")
                f.rename(g)
            else:
                print(f"Skipping {f}, not a decimal filename")


if __name__ == "__main__":
    main()
