# Image Utils

## ImCat

Image Viewer for ANSI Terminal.

![image](https://user-images.githubusercontent.com/83796250/231065095-68255527-25b1-463c-8494-1048b3893696.png)

### Usage

```
usage: imcat.py [-h] [-s COLS ROWS] image

Image Viewer for ANSI Terminal

positional arguments:
  image                 image file

options:
  -h, --help            show this help message and exit
  -s COLS ROWS, --size COLS ROWS
                        size (columns, rows)
```

## Sixel

Sixel Image Viewer.

### Usage

```
usage: sixel.py [-h] [-s WIDTH HEIGHT] image

Sixel Image Viewer

positional arguments:
  image                 image file

options:
  -h, --help            show this help message and exit
  -s WIDTH HEIGHT, --size WIDTH HEIGHT
                        size (width, height)
```

## Mixor

Tools to XOR input images.

### Usage

```
usage: mixor.py [-h] [-o OUTPUT] images [images ...]

XOR images

positional arguments:
  images

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
```

