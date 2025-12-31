import argparse

import cv2
import numpy as np
import PIL.Image as Image

from .core import encrypt


def generate(key, len, nSrc, nDst, num, red):
    vSrc = cv2.VideoCapture(nSrc)
    wSrc = int(vSrc.get(cv2.CAP_PROP_FRAME_WIDTH))
    hSrc = int(vSrc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    rate = max((wSrc * hSrc / num) ** 0.5, 1)
    wEnc = int(wSrc / rate)
    hEnc = int(hSrc / rate)
    print("Ciphertext resolution: %dx%d" % (wEnc, hEnc))
    wDst = wEnc * red
    hDst = hEnc * red
    vDst = cv2.VideoWriter(nDst, cv2.VideoWriter_fourcc(*"XVID"), vSrc.get(cv2.CAP_PROP_FPS), (wDst, hDst))
    while vSrc.isOpened():
        ret, mSrc = vSrc.read()
        if ret:
            iSrc = Image.fromarray(cv2.cvtColor(mSrc, cv2.COLOR_BGR2RGB)).resize((wEnc, hEnc))
            iDst = encrypt(key, iSrc, len)
            vDst.write(cv2.cvtColor(np.array(iDst.resize((wDst, hDst), Image.NEAREST)), cv2.COLOR_RGB2BGR))
        else:
            break
    vSrc.release()
    vDst.release()


def main():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="Video Encrypter/Decrypter")
    parser.add_argument("-k", "--key", type=bytes.fromhex, default=bytes(16), help="16/24/32-byte key in hex")
    parser.add_argument("-l", "--len", type=int, default=2, help="ratio of the edge length of each pixel in the nonce marker to each pixel in the ciphertext (default: 2)")
    parser.add_argument("-s", "--src", type=str, required=True, help="source file")
    parser.add_argument("-d", "--dst", type=str, default="out.avi", help="destination file (default: out.avi)")
    parser.add_argument("-n", "--num", type=int, default=60000, help="maximum number of pixels per frame of the ciphertext (default: 60000)")
    parser.add_argument("-r", "--red", type=int, default=4, help="pixel side length redundancy multiplier in the output video (default: 4)")
    args = parser.parse_args()
    generate(args.key, args.len, args.src, args.dst, args.num, args.red)


if __name__ == "__main__":
    main()
