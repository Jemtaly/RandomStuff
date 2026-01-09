import argparse

import cv2
import numpy as np
import PIL.Image as Image

from .core import ImageProcessor, ImageEncrypter, ImageDecrypter


def process_video(
    src_name: str,
    dst_name: str,
    size: tuple[int, int] | None,
    processor: ImageProcessor,
):
    src = cv2.VideoCapture(src_name)
    if size is None:
        w = int(src.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(src.get(cv2.CAP_PROP_FRAME_HEIGHT))
        size = (w, h)
    print(f"Processing video to size: {size}")
    dst = cv2.VideoWriter(dst_name, cv2.VideoWriter_fourcc(*"XVID"), src.get(cv2.CAP_PROP_FPS), size)
    while src.isOpened():
        ret, mSrc = src.read()
        if ret:
            img = Image.fromarray(cv2.cvtColor(mSrc, cv2.COLOR_BGR2RGB)).resize(size)
            img = processor.process(img)
            dst.write(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))
        else:
            break
    src.release()
    dst.release()


def main():
    parser = argparse.ArgumentParser(description="Video Encrypter/Decrypter")
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("-p", "--password", required=True)
    parser.add_argument("-s", "--size", type=int, nargs=2, metavar=("W", "H"), default=None)
    parser.add_argument("-l", "--length", type=int, default=2)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--enc", action="store_true", help="Encrypt the video.")
    mode.add_argument("--dec", action="store_true", help="Decrypt the video.")

    args = parser.parse_args()

    salt = b"fixed_salt_for_demo"
    if not (args.enc or args.dec):
        parser.error("Either --enc or --dec must be specified.")
    elif args.enc:
        processor = ImageEncrypter(args.password, salt, args.length)
    elif args.dec:
        processor = ImageDecrypter(args.password, salt, args.length)

    process_video(args.input, args.output, args.size, processor)


if __name__ == "__main__":
    main()
