#!/usr/bin/python3
import requests
def translate(text, source, target):
    url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl={}&tl={}&dt=t&q={}'.format(source, target, text)
    ans = requests.get(url).json()[0] or []
    return ''.join(i[0] for i in ans)
def main():
    import argparse
    parser = argparse.ArgumentParser(description = "Command Line Translator")
    parser.add_argument('-s', dest = 'source', help = 'source language', default = 'auto')
    parser.add_argument('-t', dest = 'target', help = 'target language', default = 'auto')
    parser.add_argument('-i', dest = 'input', help = 'input file', type = argparse.FileType('r'), default = '-')
    parser.add_argument('-o', dest = 'output', help = 'output file', type = argparse.FileType('w'), default = '-')
    args = parser.parse_args()
    for line in args.input:
        args.output.write(translate(line, args.source, args.target) + '\n')
if __name__ == '__main__':
    main()
