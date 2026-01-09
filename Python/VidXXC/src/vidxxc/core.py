import hashlib
from typing import Literal
from abc import ABC, abstractmethod

import random
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

import numpy as np
import PIL.Image as Image


Mode = Literal["enc", "dec"]


def generate_key32(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000, dklen=32)


def generate_nonce16(salt: bytes, itag: bytes, ctag: bytes, label: bytes) -> bytes:
    return hashlib.blake2s(salt + itag + ctag + label, digest_size=16).digest()


def generate_chacha20_stream(key32: bytes, nonce16: bytes, nbytes: int) -> bytes:
    cipher = Cipher(algorithms.ChaCha20(key32, nonce16), mode=None)
    enc = cipher.encryptor()
    return enc.update(b"\x00" * nbytes)


def generate_random_array(key32: bytes, nonce16: bytes, shape) -> np.ndarray:
    n = int(np.prod(shape))
    b = generate_chacha20_stream(key32, nonce16, 4 * n)
    u = np.frombuffer(b, dtype="<u4").astype(np.float64)
    u = (u / 2**32)  # [0,1)
    return u.reshape(shape)


def set_real_irfft2_conditions(phi: np.ndarray, H: int, W: int) -> None:
    ny = W // 2

    phi[0, 0] = 0.0
    if H % 2 == 0:
        phi[H // 2, 0] = 0.0
    for kx in range(1, H):
        phi[(H - kx) % H, 0] = -phi[kx, 0]

    if W % 2 == 0:
        phi[0, ny] = 0.0
        if H % 2 == 0:
            phi[H // 2, ny] = 0.0
        for kx in range(1, H):
            phi[(H - kx) % H, ny] = -phi[kx, ny]


def array_process(x: np.ndarray, key32: bytes, salt: bytes, itag: bytes, ctag: bytes, mode: Mode) -> np.ndarray:
    H, W = x.shape
    F = np.fft.rfft2(x)

    nonce_amp = generate_nonce16(salt, itag, ctag, b"amp")
    amp = generate_random_array(key32, nonce_amp, F.shape) * 0.0  # amplitude modulation disabled

    nonce_phi = generate_nonce16(salt, itag, ctag, b"phi")
    phi = generate_random_array(key32, nonce_phi, F.shape) * 2.0 * np.pi
    set_real_irfft2_conditions(phi, H, W)

    exp = amp + 1j * phi
    match mode:
        case "enc":
            F2 = F * np.exp(+exp)
        case "dec":
            F2 = F * np.exp(-exp)

    y = np.fft.irfft2(F2, s=(H, W)).astype(np.float64)
    return y


def image_process(img: Image.Image, key32: bytes, salt: bytes, itag: bytes, mode: Mode) -> Image.Image:
    src = np.asarray(img.convert("RGB")).astype(np.float64)

    H, W, _ = src.shape
    dst = np.empty((H, W, 3), dtype=np.float64)

    for c, ctag in enumerate([b"R", b"G", b"B"]):
        dst[..., c] = array_process(src[..., c], key32, salt, itag=itag, ctag=ctag, mode=mode)

    out = Image.fromarray(np.clip(dst, 0, 255).astype(np.uint8), mode="RGB")
    return out


class ImageProcessor(ABC):
    @abstractmethod
    def process(self, img: Image.Image) -> Image.Image:
        pass


class ImageEncrypter(ImageProcessor):
    def __init__(self, password: str, salt: bytes, len: int):
        self.key32 = generate_key32(password, salt)
        self.salt = salt
        self.len = len

    def gen_nonce(self) -> bytes:
        return random.randbytes(8)

    def put_nonce(self, img: Image.Image, nonce: bytes) -> Image.Image:
        img = img.convert("RGB")
        for i in range(8):
            for j in range(8):
                bit = nonce[i] >> j & 1
                rgb = 255 * bit, 255 * bit, 255 * bit
                for x in range(i * self.len, i * self.len + self.len):
                    for y in range(j * self.len, j * self.len + self.len):
                        img.putpixel((x, y), rgb)
        return img

    def process(self, img: Image.Image) -> Image.Image:
        nonce = self.gen_nonce()
        img = image_process(img, self.key32, self.salt, nonce, mode="enc")
        img = self.put_nonce(img, nonce)
        return img


class ImageDecrypter(ImageProcessor):
    def __init__(self, password: str, salt: bytes, len: int):
        self.key32 = generate_key32(password, salt)
        self.salt = salt
        self.len = len

    def get_nonce(self, img: Image.Image) -> bytes:
        img = img.convert("RGB")
        nonce = bytearray(8)
        for i in range(8):
            for j in range(8):
                x = i * self.len + self.len // 2
                y = j * self.len + self.len // 2
                rgb = img.getpixel((x, y))
                bit = sum(rgb) // 383
                nonce[i] |= bit << j
        return bytes(nonce)

    def process(self, img: Image.Image) -> Image.Image:
        nonce = self.get_nonce(img)
        img = image_process(img, self.key32, self.salt, nonce, mode="dec")
        return img

