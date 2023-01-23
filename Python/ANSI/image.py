#!/usr/bin/python3
import PIL.Image, numpy, ansi, argparse
def ishow(image, rows, cols):
    if rows <= 0 and cols <= 0:
        diagonal = (image.width ** 2 + image.height ** 2) ** 0.5
        rows, cols = int(image.height * 80 / diagonal), int(image.width * 80 / diagonal)
    elif cols <= 0:
        cols = int(image.width * rows / image.height)
    elif rows <= 0:
        rows = int(image.height * cols / image.width)
    image = image.resize((cols, rows)).convert('RGB')
    pixel = numpy.vectorize(ansi.RGB)(*numpy.array(image).transpose((2, 0, 1)))
    if rows % 2:
        pixel = numpy.concatenate((pixel, numpy.empty((1, cols), dtype = object)))
    for hi, lo in zip(pixel[0::2], pixel[1::2]):
        for h, l in zip(hi, lo):
            print(ansi.SGR(fgc = h, bgc = l) + '▀', end = '')
        print(ansi.SGR())
def main():
    parser = argparse.ArgumentParser(description = 'Image Viewer for ANSI Terminal.')
    parser.add_argument('image', type = str, help = 'image file')
    parser.add_argument('-c', '--cols', type = int, default = 0, help = 'number of pixel cols')
    parser.add_argument('-r', '--rows', type = int, default = 0, help = 'number of pixel rows')
    args = parser.parse_args()
    image = PIL.Image.open(args.image)
    ishow(image, args.rows, args.cols)
if __name__ == '__main__':
    main()
