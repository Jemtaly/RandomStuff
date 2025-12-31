#!/usr/bin/env python3

import argparse
from urllib.parse import quote

import requests


class Translator:
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target

    def translate(self, text: str) -> str:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q={q}".format(
            sl=self.source,
            tl=self.target,
            q=quote(text),
        )
        ans = requests.get(url).json()[0] or []
        return "".join(t for t, s, *info in ans)


def main():
    parser = argparse.ArgumentParser(description="Command Line Translator")
    parser.add_argument("-s", dest="source", help="source language", default="auto")
    parser.add_argument("-t", dest="target", help="target language", default="auto")
    parser.add_argument("-i", dest="input", help="input file", type=argparse.FileType("r"), default="-")
    parser.add_argument("-o", dest="output", help="output file", type=argparse.FileType("w"), default="-")
    parser.add_argument("-a", dest="all", action="store_true", help="translate all at once")
    args = parser.parse_args()

    translator = Translator(args.source, args.target)
    if args.all:
        cont = args.input.read()
        args.output.write(translator.translate(cont) + "\n")
    else:
        for line in args.input:
            args.output.write(translator.translate(line) + "\n")


if __name__ == "__main__":
    main()
