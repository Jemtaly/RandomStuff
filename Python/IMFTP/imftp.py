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
        return self.client.send(self.enc(data))
    def recv(self, size):
        return self.dec(self.client.recv(size))
    def sendall(self, data):
        self.client.sendall(self.enc(data))
    def recvall(self, size):
        return self.dec(self.client.recv(size, socket.MSG_WAITALL))
    def genkey(self):
        self.sendall(b'GK')
        assert self.recv(2) == b'GK', 'peer is not in key generation mode'
        sockecck = ECC.generate(curve = 'nistp256')
        sockexpk = sockecck.public_key().export_key(format = 'SEC1')
        self.sendall(sockexpk)
        peerexpk = self.recvall(65)
        peerecck = ECC.import_key(peerexpk, curve_name = 'nistp256')
        key = DH.key_agreement(static_priv = sockecck, static_pub = peerecck, kdf = lambda x: x)
        sockaesk = hashlib.sha256(sockexpk + key).digest()
        peeraesk = hashlib.sha256(peerexpk + key).digest()
        self.enc = AES.new(sockaesk[:16], AES.MODE_CTR, nonce = sockaesk[24:]).encrypt
        self.dec = AES.new(peeraesk[:16], AES.MODE_CTR, nonce = peeraesk[24:]).decrypt
    def sendstream(self, istream, rec):
        self.sendall(b'SS')
        assert self.recv(2) == b'RS', 'peer is not in receiving mode'
        datasize = 4094
        while datasize == 4094:
            data = istream.read(rec[0] if 0 <= rec[0] < 4094 else 4094)
            datasize = len(data)
            self.sendall(datasize.to_bytes(2, 'big') + data)
            rec[0] -= datasize
    def recvstream(self, ostream, rec):
        self.sendall(b'RS')
        assert self.recv(2) == b'SS', 'peer is not in sending mode'
        datasize = int.from_bytes(self.recvall(2), 'big')
        while datasize == 4094:
            temp = self.recvall(4096)
            rec[0] += ostream.write(temp[:4094])
            datasize = int.from_bytes(temp[4094:], 'big')
        rec[0] += ostream.write(self.recvall(datasize))
    def __sending(self):
        data = b'\n'
        while data and data[-1] == 10:
            data = sys.stdin.readline().encode()
            temp = len(data).to_bytes(2, 'big') + data
            while temp:
                temp = temp[self.send(temp[:4096]):]
    def __recving(self):
        data = b'\n'
        while data and data[-1] == 10:
            data = bytes()
            size = int.from_bytes(self.recvall(2), 'big')
            while size:
                temp = self.recv(min(4096, size))
                data += temp
                size -= len(temp)
            sys.stdout.write(data.decode())
    def talk(self):
        self.sendall(b'IM')
        assert self.recv(2) == b'IM', 'peer is not in instant messager mode'
        sending = threading.Thread(target = self.__sending)
        recving = threading.Thread(target = self.__recving)
        sending.start()
        recving.start()
        sending.join()
        recving.join()
def run(client, recv, send, size, enc):
    C = TCPClientWrapper(client)
    if enc:
        C.genkey()
    if recv:
        rec = [0 if size == None else size]
        C.recvstream(recv, rec)
        print(rec[0])
    elif send:
        rec = [-1 if size == None else size]
        C.sendstream(send, rec)
        print(rec[0])
    else:
        C.talk()
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
            run(client, args.recv, args.send, args.size, args.enc)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((args.server, args.port))
        with server:
            server.listen(1)
            client, addr = server.accept()
            with client:
                run(client, args.recv, args.send, args.size, args.enc)
if __name__ == '__main__':
    main()
