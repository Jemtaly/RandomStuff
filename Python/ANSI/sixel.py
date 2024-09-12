#!/usr/bin/env python3


import argparse

import numpy as np
import PIL.Image as Image


def sixel(image, size):
    if size:
        image.thumbnail(size, Image.LANCZOS)
    image = image.convert("1")
    pixel = np.array(image)
    h, w = pixel.shape
    pixel = np.pad(pixel, ((0, -h % 6), (0, 0)), "constant").reshape((-1, 6, w)).transpose((0, 2, 1))
    print("\033Pq", end="")
    for sixln in pixel:
        for sixel in sixln:
            print(chr(sum(v << i for i, v in enumerate(sixel)) + 0o77), end="")
        print("-", end="")
    print("\033\\", end="")


def main():
    parser = argparse.ArgumentParser(description="Sixel Image Viewer")
    parser.add_argument("image", type=Image.open, help="image file")
    parser.add_argument("-s", "--size", metavar=("WIDTH", "HEIGHT"), default=None, type=int, nargs=2, help="size (width, height)")
    args = parser.parse_args()
    sixel(args.image, args.size)


if __name__ == "__main__":
    main()
