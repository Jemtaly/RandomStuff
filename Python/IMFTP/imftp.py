#!/usr/bin/python3
import socket, sys, threading, hashlib
import Crypto.PublicKey.ECC as ECC
import Crypto.Protocol.DH as DH
import Crypto.Cipher.AES as AES
class TCPClientWrapper:
    def __init__(self, client):
        self.client = client
        self.dec = lambda x: x
        self.enc = lambda x: x
    @property
    def sockname(self):
        return self.client.getsockname()
    @property
    def peername(self):
        return self.client.getpeername()
    def send(self, data):
        self.client.sendall(self.enc(data))
    def recv(self, size):
        return self.dec(self.client.recv(size, socket.MSG_WAITALL))
    def genkey(self):
        self.send(b'GK')
        assert self.recv(2) == b'GK', 'peer is not in key generation mode'
        sockecck = ECC.generate(curve = 'nistp256')
        sockexpk = sockecck.public_key().export_key(format = 'SEC1')
        self.send(sockexpk)
        peerexpk = self.recv(65)
        peerecck = ECC.import_key(peerexpk, curve_name = 'nistp256')
        key = DH.key_agreement(static_priv = sockecck, static_pub = peerecck, kdf = lambda x: x)
        sockaesk = hashlib.sha256(sockexpk + key).digest()
        peeraesk = hashlib.sha256(peerexpk + key).digest()
        self.enc = AES.new(sockaesk[:16], AES.MODE_CTR, nonce = sockaesk[24:]).encrypt
        self.dec = AES.new(peeraesk[:16], AES.MODE_CTR, nonce = peeraesk[24:]).decrypt
    def sendstream(self, istream, r):
        self.send(b'SS')
        assert self.recv(2) == b'RS', 'peer is not in receiving mode'
        size = 4094
        while size == 4094:
            data = istream.read(r[0] if 0 <= r[0] < 4094 else 4094)
            size = len(data)
            self.send(size.to_bytes(2, 'big') + data)
            r[0] -= size
    def recvstream(self, ostream, r):
        self.send(b'RS')
        assert self.recv(2) == b'SS', 'peer is not in sending mode'
        size = int.from_bytes(self.recv(2), 'big')
        while size == 4094:
            temp = self.recv(4096)
            r[0] += ostream.write(temp[:4094])
            size = int.from_bytes(temp[4094:], 'big')
        r[0] += ostream.write(self.recv(size))
    def __sending(self):
        data = b'\n'
        while data and data[-1] == 10:
            data = sys.stdin.readline().encode()
            self.send(len(data).to_bytes(2, 'big') + data)
    def __recving(self):
        data = b'\n'
        while data and data[-1] == 10:
            data = self.recv(int.from_bytes(self.recv(2), 'big'))
            sys.stdout.write(data.decode())
    def talk(self):
        self.send(b'IM')
        assert self.recv(2) == b'IM', 'peer is not in instant messager mode'
        sending = threading.Thread(target = self.__sending)
        recving = threading.Thread(target = self.__recving)
        sending.start()
        recving.start()
        sending.join()
        recving.join()
def run(client, recv, send, talk, size, enc):
    C = TCPClientWrapper(client)
    if enc:
        C.genkey()
    if talk:
        C.talk()
    elif recv:
        rec = [0 if size == None else size]
        C.recvstream(recv, rec)
        print(rec[0])
    elif send:
        rec = [-1 if size == None else size]
        C.sendstream(send, rec)
        print(rec[0])
def main():
    import argparse
    parser = argparse.ArgumentParser(description = "Instant Messager and File Transfer")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--server', metavar = 'IP', nargs = '?', default = '', const = '', help = 'run as a server (default)')
    mode.add_argument('--client', metavar = 'IP', help = 'run as a client (server IP required)')
    parser.add_argument('--port', type = int, default = 4096, help = 'port number of the server (4096 by default)')
    action = parser.add_mutually_exclusive_group(required = True)
    action.add_argument('--send', metavar = 'FILENAME', nargs = '?', type = argparse.FileType('rb'), const = sys.stdin.buffer, help = 'send file')
    action.add_argument('--recv', metavar = 'FILENAME', nargs = '?', type = argparse.FileType('wb'), const = sys.stdout.buffer, help = 'receive file')
    action.add_argument('--talk', action = 'store_true', help = 'instant messager')
    parser.add_argument('--size', type = int, help = 'set size limit (unlimited by default, ignored in the instant messager mode)')
    parser.add_argument('--enc', action = 'store_true', help = 'encrypt the connection with DHKE and AES-CTR (cannot be set on one side only)')
    args = parser.parse_args()
    if args.client:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((args.client, args.port))
        with client:
            run(client, args.recv, args.send, args.talk, args.size, args.enc)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((args.server, args.port))
        with server:
            server.listen(1)
            client, addr = server.accept()
            with client:
                run(client, args.recv, args.send, args.talk, args.size, args.enc)
if __name__ == '__main__':
    main()
