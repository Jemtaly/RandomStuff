#!/usr/bin/python3
import argparse
import chardet
def main():
    parser = argparse.ArgumentParser(description = 'Text File Decoder')
    parser.add_argument(dest = 'encoded', help = 'encoded file', type = argparse.FileType('rb'))
    parser.add_argument('-o', dest = 'output', help = 'output file', type = argparse.FileType('w'), default = '-')
    parser.add_argument('-e', dest = 'encoding', help = 'encoding', type = str, default = None)
    args = parser.parse_args()
    cont = args.encoded.read()
    args.output.write(cont.decode(args.encoding or chardet.detect(cont)['encoding'] or 'utf-8'))
if __name__ == '__main__':
    main()
