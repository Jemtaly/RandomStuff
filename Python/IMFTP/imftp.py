#!/usr/bin/python3
import socket, sys, threading
class TCPClientWrapper:
    def __init__(self, client):
        self.client = client
    @property
    def sockname(self):
        return self.client.getsockname()
    @property
    def peername(self):
        return self.client.getpeername()
    def sendstream(self, istream, rec = [-1]):
        self.client.send(b'SS')
        assert self.client.recv(2) == b'RS'
        datasize = 4094
        while datasize == 4094:
            data = istream.read(rec[0] if 0 <= rec[0] < 4094 else 4094)
            datasize = len(data)
            self.client.sendall(datasize.to_bytes(2, 'big') + data)
            rec[0] -= datasize
    def recvstream(self, ostream, rec = [0]):
        self.client.send(b'RS')
        assert self.client.recv(2) == b'SS'
        datasize = int.from_bytes(self.client.recv(2, socket.MSG_WAITALL), 'big')
        while datasize == 4094:
            temp = self.client.recv(4096, socket.MSG_WAITALL)
            rec[0] += ostream.write(temp[:4094])
            datasize = int.from_bytes(temp[4094:], 'big')
        rec[0] += ostream.write(self.client.recv(datasize, socket.MSG_WAITALL))
    def __sending(self):
        data = b'\n'
        while data and data[-1] == 10:
            data = sys.stdin.readline().encode()
            temp = len(data).to_bytes(2, 'big') + data
            while temp:
                temp = temp[self.client.send(temp[:4096]):]
    def __recving(self):
        data = b'\n'
        while data and data[-1] == 10:
            data = bytes()
            size = int.from_bytes(self.client.recv(2, socket.MSG_WAITALL), 'big')
            while size:
                temp = self.client.recv(min(4096, size))
                data += temp
                size -= len(temp)
            sys.stdout.write(data.decode())
    def talk(self):
        self.client.send(b'IM')
        assert self.client.recv(2) == b'IM'
        sending = threading.Thread(target = self.__sending)
        recving = threading.Thread(target = self.__recving)
        sending.start()
        recving.start()
        sending.join()
        recving.join()
def run(client, recv, send, size):
    C = TCPClientWrapper(client)
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
    parser = argparse.ArgumentParser(description = "Instant Messager and File Transfer.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--server', metavar = 'IP', nargs = '?', default = '', const = '', help = 'run as a server (default)')
    mode.add_argument('--client', metavar = 'IP', help = 'run as a client')
    parser.add_argument('--port', type = int, default = 2351, help = 'set port (2351 by default)')
    action = parser.add_mutually_exclusive_group(required = True)
    action.add_argument('--send', metavar = 'FILENAME', nargs = '?', type = argparse.FileType('rb'), const = sys.stdin.buffer, help = 'send file')
    action.add_argument('--recv', metavar = 'FILENAME', nargs = '?', type = argparse.FileType('wb'), const = sys.stdout.buffer, help = 'receive file')
    action.add_argument('--talk', action = 'store_true', help = 'instant messager')
    parser.add_argument('--size', type = int, help = 'set the initial value')
    args = parser.parse_args()
    if args.client:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((args.client, args.port))
        with client:
            run(client, args.recv, args.send, args.size)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((args.server, args.port))
        with server:
            server.listen(1)
            client, addr = server.accept()
            with client:
                run(client, args.recv, args.send, args.size)
if __name__ == '__main__':
    main()
