import random
from PIL import Image
from Crypto.Cipher import AES
def encrypt(key, iSrc, len):
    iSrc = iSrc.convert('RGB')
    bSrc = iSrc.tobytes()
    nonce = random.randbytes(8)
    cipher = AES.new(key, AES.MODE_CTR, nonce = nonce)
    bDst = cipher.encrypt(bSrc)
    iDst = Image.frombytes('RGB', iSrc.size, bDst)
    for i in range(8):
        for j in range(8):
            bit = nonce[i] >> j & 1
            rgb = 255 * bit, 255 * bit, 255 * bit
            for x in range(len):
                for y in range(len):
                    iDst.putpixel((i * len + x, j * len + y), rgb)
    return iDst
def decrypt(key, iSrc, len):
    iSrc = iSrc.convert('RGB')
    bSrc = iSrc.tobytes()
    nonce = bytearray(8)
    for i in range(8):
        for j in range(8):
            rgb = iSrc.getpixel((i * len + len // 2, j * len + len // 2))
            bit = sum(rgb) // 383
            nonce[i] |= bit << j
    cipher = AES.new(key, AES.MODE_CTR, nonce = nonce)
    bDst = cipher.decrypt(bSrc)
    iDst = Image.frombytes('RGB', iSrc.size, bDst)
    return iDst
