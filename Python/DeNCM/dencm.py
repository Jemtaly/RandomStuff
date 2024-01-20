#!/usr/bin/python3
import Crypto.Cipher.AES as AES
import Crypto.Util.Padding as Padding
import os
import base64
import json
import struct
core_key = bytes.fromhex('687A4852416D736F356B496E62617857')
meta_key = bytes.fromhex('2331346C6A6B5F215C5D2630553C2728')
core_cryptor = AES.new(core_key, AES.MODE_ECB)
meta_cryptor = AES.new(meta_key, AES.MODE_ECB)
def dump(ncm_path):
    print('{}:'.format(ncm_path))
    with open(ncm_path, 'rb') as ncm_file:
        if ncm_file.read(8) != b'CTENFDAM':
            print('Not a NCM file')
            return
        ncm_file.seek(2, 1)
        core_size = struct.unpack('<I', bytes(ncm_file.read(4)))[0]
        core_enc = bytes(i ^ 0x64 for i in ncm_file.read(core_size))
        core_dec = Padding.unpad(core_cryptor.decrypt(core_enc), 16) # 'neteasecloudmusic' + key
        meta_size = struct.unpack('<I', bytes(ncm_file.read(4)))[0]
        meta_raw = bytes(i ^ 0x63 for i in ncm_file.read(meta_size)) # '163 key(Don't modify):' + base64
        meta_enc = base64.b64decode(meta_raw[22:])
        meta_dec = Padding.unpad(meta_cryptor.decrypt(meta_enc), 16) # 'music:' + json
        meta_info = json.loads(meta_dec.decode('utf-8')[6:])
        print(json.dumps(meta_info, indent = 4, ensure_ascii = False))
        os.makedirs(meta_info['album'], exist_ok = True)
        checksum = struct.unpack('<I', bytes(ncm_file.read(4)))[0]
        ncm_file.seek(5, 1)
        img_size = struct.unpack('<I', bytes(ncm_file.read(4)))[0]
        img_path = os.path.join(meta_info['album'], 'cover.jpg')
        with open(img_path, 'wb') as img_file:
            img_file.write(ncm_file.read(img_size))
        mp3_path = os.path.join(meta_info['album'], '{musicName}.{format}'.format(**meta_info))
        with open(mp3_path, 'wb') as mp3_file:
            # An less secure variant of RC4 that is actually equivalent to a 256-byte Vigenère cipher
            k = core_dec[17:]
            n = len(k)
            S = bytearray(range(256))
            c = 0
            for i in range(256):
                swap = S[i]
                c = c + swap + k[i % n] & 0xff
                S[i] = S[c]
                S[c] = swap
            K = bytes(S[S[i] + S[S[i] + i & 0xff] & 0xff] for i in range(256))
            i = 0
            while True:
                chunk = ncm_file.read(0x10000)
                mp3_file.write(bytes(a ^ K[i := i + 1 & 0xff] for a in chunk))
                if len(chunk) < 0x10000:
                    break
def main():
    import argparse
    import glob
    parser = argparse.ArgumentParser(description = 'NCM file decryptor')
    parser.add_argument('ncm_path', nargs = '*', help = 'NCM file path')
    args = parser.parse_args()
    if args.ncm_path:
        for ncm_path in args.ncm_path:
            for ncm_file in glob.glob(ncm_path):
                dump(ncm_file)
    else:
        for ncm_file in os.listdir():
            if os.path.splitext(ncm_file)[1] == '.ncm':
                dump(ncm_file)
if __name__ == '__main__':
    main()
