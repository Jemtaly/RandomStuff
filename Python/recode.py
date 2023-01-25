#!/usr/bin/python3
def main():
    import argparse
    parser = argparse.ArgumentParser(description = 'Text file recoder.')
    parser.add_argument('-d', '--decoding', help = 'decoding', default = 'utf-8')
    parser.add_argument('-e', '--encoding', help = 'encoding', default = 'utf-8')
    parser.add_argument('-i', dest = 'infile', help = 'input file', type = argparse.FileType('rb'), default = '-')
    parser.add_argument('-o', dest = 'outfile', help = 'output file', type = argparse.FileType('wb'), default = '-')
    args = parser.parse_args()
    args.outfile.write(args.infile.read().decode(args.decoding).encode(args.encoding))
if __name__ == '__main__':
    main()
