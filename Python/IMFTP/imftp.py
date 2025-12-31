#!/usr/bin/env python3


import argparse
import os
import queue
import socket
import sys
import threading

from .messager import Messager

import Crypto.Cipher.AES as AES
import Crypto.Hash.SHA224 as SHA224
import Crypto.Protocol.DH as DH
import Crypto.PublicKey.ECC as ECC


class TCPClientWrapper:
    def __init__(self, client: socket.socket):
        self.client = client
        self.dec = lambda x: x
        self.enc = lambda x: x

    def sockname(self):
        return self.client.getsockname()

    def peername(self):
        return self.client.getpeername()

    def sendall(self, data):
        self.client.sendall(self.enc(data))

    def recvall(self, size):
        return self.dec(self.client.recv(size, socket.MSG_WAITALL))

    def keyexchange(self):
        self.sendall(b"KEYX")
        assert self.recvall(4) == b"KEYX", "peer is not in key generation mode"
        sockecck = ECC.generate(curve="nistp256")
        sockexpk = sockecck.public_key().export_key(format="SEC1")
        self.sendall(sockexpk)
        peerexpk = self.recvall(65)
        peerecck = ECC.import_key(peerexpk, curve_name="nistp256")
        key = DH.key_agreement(static_priv=sockecck, static_pub=peerecck, kdf=lambda x: x)
        sockaesk = SHA224.new(sockexpk + key).digest()
        peeraesk = SHA224.new(peerexpk + key).digest()
        self.enc = AES.new(sockaesk[:16], AES.MODE_CTR, nonce=sockaesk[16:]).encrypt
        self.dec = AES.new(peeraesk[:16], AES.MODE_CTR, nonce=peeraesk[16:]).decrypt

    def sendstream(self, istream, buff=sys.stderr):
        self.sendall(b"SBDS")
        assert self.recvall(4) == b"RBDS", "peer is not in receiving mode"
        recd = 0
        while True:
            data = istream.read(0x0FFE)
            size = len(data)
            self.sendall(size.to_bytes(2, "big") + data)
            buff.write("\r{} bytes sent".format(recd := recd + size))
            if size < 0x0FFE:
                break
        buff.write("\n")

    def recvstream(self, ostream, buff=sys.stderr):
        self.sendall(b"RBDS")
        assert self.recvall(4) == b"SBDS", "peer is not in sending mode"
        recd = 0
        size = int.from_bytes(self.recvall(2), "big")
        while size == 0x0FFE:
            temp = self.recvall(0x1000)
            ostream.write(temp[:0x0FFE])
            buff.write("\r{} bytes received".format(recd := recd + size))
            size = int.from_bytes(temp[0x0FFE:], "big")
        data = self.recvall(size)
        ostream.write(data)
        buff.write("\r{} bytes received".format(recd := recd + size))
        buff.write("\n")

    def chat(self):
        self.sendall(b"CHAT")
        assert self.recvall(4) == b"CHAT", "peer is not in chat mode"
        recv_queue = queue.Queue()

        def recv_loop():
            while True:
                try:
                    head = self.recvall(4)
                    mode = head[0]
                    data = self.recvall(int.from_bytes(head[1:], "big"))
                    recv_queue.put((mode, data))
                    if mode == 0:
                        break
                except ConnectionResetError:
                    recv_queue.put((-1, b""))
                    break

        def recv():
            try:
                return recv_queue.get_nowait()
            except queue.Empty:
                return None

        def send(mode, data):
            if len(data) > 0xFFFFFF:
                raise OverflowError("data too large")
            size = len(data)
            self.sendall(bytes([mode]) + size.to_bytes(3, "big") + data)

        recv_thrd = threading.Thread(target=recv_loop)
        recv_thrd.start()
        Messager(recv, send, self.sockname(), self.peername()).mainloop()
        recv_thrd.join()


def process(client, recv, send, chat, enc, buff):
    C = TCPClientWrapper(client)
    if enc:
        C.keyexchange()
    if chat:
        C.chat()
    elif recv:
        C.recvstream(recv, buff)
    elif send:
        C.sendstream(send, buff)


def main():
    parser = argparse.ArgumentParser(description="Chat and transfer files over TCP/IP")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--server", metavar="IP", nargs="?", default="", const="", help="run as a server (default)")
    mode.add_argument("--client", metavar="IP", help="run as a client (server IP required)")
    parser.add_argument("--port", type=int, default=4096, help="port number of the server (4096 by default)")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--send", metavar="FILENAME", nargs="?", type=argparse.FileType("rb"), const=sys.stdin.buffer, help="send file")
    action.add_argument("--recv", metavar="FILENAME", nargs="?", type=argparse.FileType("wb"), const=sys.stdout.buffer, help="receive file")
    action.add_argument("--chat", action="store_true", help="start a chat session")
    parser.add_argument("--enc", action="store_true", help="encrypt the connection with DHKE and AES-CTR (cannot be set on one side only)")
    parser.add_argument("--log", action="store_true", help="show sending/receiving progress")
    args = parser.parse_args()
    buff = sys.stderr if args.log else open(os.devnull, "w")
    if args.client:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((args.client, args.port))
        with client:
            process(client, args.recv, args.send, args.chat, args.enc, buff)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((args.server, args.port))
        with server:
            server.listen(1)
            client, addr = server.accept()
            with client:
                process(client, args.recv, args.send, args.chat, args.enc, buff)


if __name__ == "__main__":
    main()
