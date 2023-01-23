#!/usr/bin/python3
import argparse
def main():
    parser = argparse.ArgumentParser(description = 'Text file recoder.')
    parser.add_argument('infile', type = argparse.FileType('rb'), help = 'Input file', nargs = '?', default = '-')
    parser.add_argument('outfile', type = argparse.FileType('wb'), help = 'Output file', nargs = '?', default = '-')
    parser.add_argument('-d', '--decoding', help = 'Decoding', default = 'utf-8')
    parser.add_argument('-e', '--encoding', help = 'Encoding', default = 'utf-8')
    args = parser.parse_args()
    args.outfile.write(args.infile.read().decode(args.decoding).encode(args.encoding))
if __name__ == '__main__':
    main()
