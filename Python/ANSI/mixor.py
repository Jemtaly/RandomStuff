#!/usr/bin/python3
import numpy as np
import PIL.Image as Image
def xor(*images):
    sizes = set(image.size for image in images)
    modes = set(image.mode for image in images)
    if len(sizes) > 1 or len(modes) > 1:
        raise ValueError("Images must be of the same size and mode.")
    return Image.fromarray(np.bitwise_xor.reduce([np.asarray(image) for image in images]))
def main():
    import argparse
    parser = argparse.ArgumentParser(description = "XOR images")
    parser.add_argument("images", nargs = "+", type = Image.open)
    parser.add_argument("-o", "--output", default = "result.png")
    args = parser.parse_args()
    xor(*args.images).save(args.output)
if __name__ == "__main__":
    main()
