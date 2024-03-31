#!/usr/bin/python3
import numpy as np
import PIL.Image as Image
import ansi, os
import argparse
def imcat(image, size):
    cols, rows = size
    image.thumbnail((cols * 1, rows * 2), Image.LANCZOS)
    image = image.convert('RGB')
    R, G, B = np.array(image).transpose((2, 0, 1))
    pixel = np.vectorize(ansi.RGB)(R, G, B)
    h, w = pixel.shape
    pixel = np.pad(pixel, ((0, -h % 2), (0, 0)), 'constant').reshape((-1, 2, w)).transpose((0, 2, 1))
    for twoln in pixel:
        for h, l in twoln:
            print(ansi.SGR(fgc = h, bgc = l) + '▀', end = '')
        print(ansi.SGR())
def main():
    parser = argparse.ArgumentParser(description = 'Image Viewer for ANSI Terminal')
    parser.add_argument('image', type = Image.open, help = 'image file')
    parser.add_argument('-s', '--size', metavar = ('COLS', 'ROWS'), default = None, type = int, nargs = 2, help = 'size (columns, rows)')
    args = parser.parse_args()
    imcat(args.image, args.size or os.get_terminal_size())
if __name__ == '__main__':
    main()
