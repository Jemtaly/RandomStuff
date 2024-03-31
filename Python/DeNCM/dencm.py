#!/usr/bin/python3
import Crypto.Cipher.AES as AES
import Crypto.Util.Padding as Padding
import Crypto.Util.strxor as strxor
import base64, struct, json, os
import argparse, glob
core_key = bytes.fromhex('687A4852416D736F356B496E62617857')
meta_key = bytes.fromhex('2331346C6A6B5F215C5D2630553C2728')
core_cryptor = AES.new(core_key, AES.MODE_ECB)
meta_cryptor = AES.new(meta_key, AES.MODE_ECB)
def dump(ncm_path, original_name = False):
    print('{}:'.format(ncm_path))
    with open(ncm_path, 'rb') as ncm_file:
        if ncm_file.read(8) != b'CTENFDAM':
            print('Not a NCM file')
            return
        ncm_file.seek(2, 1)
        core_size = struct.unpack('<I', bytes(ncm_file.read(4)))[0]
        core_enc = strxor.strxor_c(ncm_file.read(core_size), 0x64)
        core_dec = Padding.unpad(core_cryptor.decrypt(core_enc), 16) # 'neteasecloudmusic' + key
        meta_size = struct.unpack('<I', bytes(ncm_file.read(4)))[0]
        meta_raw = strxor.strxor_c(ncm_file.read(meta_size), 0x63) # '163 key(Don't modify):' + base64
        meta_enc = base64.b64decode(meta_raw[22:])
        meta_dec = Padding.unpad(meta_cryptor.decrypt(meta_enc), 16) # 'music:' + json
        meta_info = json.loads(meta_dec[6:])
        print(json.dumps(meta_info, indent = 4, ensure_ascii = False))
        checksum = struct.unpack('<I', bytes(ncm_file.read(4)))[0]
        ncm_file.seek(5, 1)
        img_size = struct.unpack('<I', bytes(ncm_file.read(4)))[0]
        if original_name:
            mp3_path = os.path.splitext(ncm_path)[0] + '.' + meta_info['format']
            ncm_file.seek(img_size, 1)
        else:
            img_path = os.path.join(meta_info['album'], 'cover.jpg')
            mp3_path = os.path.join(meta_info['album'], '{musicName}.{format}'.format(**meta_info))
            os.makedirs(meta_info['album'], exist_ok = True)
            with open(img_path, 'wb') as img_file:
                img_file.write(ncm_file.read(img_size))
        with open(mp3_path, 'wb') as mp3_file:
            # A less secure variant of RC4, which is actually equivalent to a 256-byte Vigenère cipher
            k = core_dec[17:]
            n = len(k)
            S = bytearray(range(256))
            c = 0
            for i in range(256):
                swap = S[i]
                c = c + swap + k[i % n] & 0xff
                S[i] = S[c]
                S[c] = swap
            N = 65536 # Size of the chunk, must be a multiple of 256
            K = bytes(S[S[S[i & 0xff] + i & 0xff] + S[i & 0xff] & 0xff] for i in range(1, 257)) * (N // 256) # Expanded key stream
            while True:
                chunk = ncm_file.read(N)
                if len(chunk) == N:
                    mp3_file.write(strxor.strxor(chunk, K))
                else:
                    mp3_file.write(strxor.strxor(chunk, K[:len(chunk)]))
                    break
def main():
    parser = argparse.ArgumentParser(description = 'NCM file decryptor')
    parser.add_argument('pathlist', metavar = 'NCM', nargs = '*', help = 'NCM file path (if not specified, all .ncm files in current directory will be processed)')
    parser.add_argument('-o', '--original-name', action = 'store_true', help = 'Use original file name')
    args = parser.parse_args()
    if args.pathlist:
        for pathname in args.pathlist:
            for ncm_path in glob.glob(pathname):
                dump(ncm_path, args.original_name)
    else:
        for ncm_path in os.listdir():
            if os.path.splitext(ncm_path)[1] == '.ncm':
                dump(ncm_path, args.original_name)
if __name__ == '__main__':
    main()
