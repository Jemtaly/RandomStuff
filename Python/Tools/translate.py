#!/usr/bin/python3
from urllib.parse import quote
import requests
import argparse
def translate(text, source, target):
    url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl={}&tl={}&dt=t&q={}'.format(source, target, quote(text))
    ans = requests.get(url).json()[0] or []
    return ''.join(t for t, s, *info in ans)
def main():
    parser = argparse.ArgumentParser(description = "Command Line Translator")
    parser.add_argument('-s', dest = 'source', help = 'source language', default = 'auto')
    parser.add_argument('-t', dest = 'target', help = 'target language', default = 'auto')
    parser.add_argument('-i', dest = 'input', help = 'input file', type = argparse.FileType('r'), default = '-')
    parser.add_argument('-o', dest = 'output', help = 'output file', type = argparse.FileType('w'), default = '-')
    parser.add_argument('-a', dest = 'all', action = 'store_true', help = 'translate all at once')
    args = parser.parse_args()
    if args.all:
        cont = args.input.read()
        args.output.write(translate(cont, args.source, args.target) + '\n')
    else:
        for line in args.input:
            args.output.write(translate(line, args.source, args.target) + '\n')
if __name__ == '__main__':
    main()
