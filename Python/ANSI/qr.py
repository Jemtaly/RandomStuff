#!/usr/bin/python3
import qrcode, argparse
def qrshow(data, **kwargs):
    qr = qrcode.QRCode(**kwargs)
    qr.add_data(data)
    qr.make(fit = True)
    M = qr.get_matrix()
    if len(M) % 2:
        M += [[False] * len(M)]
    for hi, lo in zip(M[0::2], M[1::2]):
        for h, l in zip(hi, lo):
            print(' ▄▀█'[3 - h * 2 - l], end = '')
        print()
def main():
    parser = argparse.ArgumentParser(description = 'QR Code Generator.')
    parser.add_argument('data', type = str, help = 'data to encode')
    parser.add_argument('-v', '--version', type = int, default = 1, help = 'version of QR code')
    parser.add_argument('-e', '--error', type = int, default = 0, help = 'error correction level')
    args = parser.parse_args()
    qrshow(args.data, version = args.version, error_correction = args.error)
if __name__ == '__main__':
    main()
