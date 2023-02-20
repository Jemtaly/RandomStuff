#!/usr/bin/python3
def main():
    import argparse, chardet
    parser = argparse.ArgumentParser(description = 'Text file decoder.')
    parser.add_argument(dest = 'encoded', help = 'encoded file', type = argparse.FileType('rb'))
    parser.add_argument('-o', dest = 'output', help = 'output file', type = argparse.FileType('w'), default = '-')
    parser.add_argument('-e', dest = 'encoding', help = 'encoding', type = str, default = None)
    args = parser.parse_args()
    cont = args.encoded.read()
    args.output.write(cont.decode(args.encoding or chardet.detect(cont)['encoding']))
if __name__ == '__main__':
    main()