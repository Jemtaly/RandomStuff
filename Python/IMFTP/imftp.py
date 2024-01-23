#!/usr/bin/python3
import sys, io, socket, threading, queue, tkinter
from tkinter import filedialog, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import Crypto.PublicKey.ECC as ECC
import Crypto.Protocol.DH as DH
import Crypto.Cipher.AES as AES
import Crypto.Hash.SHA224 as SHA224
class TCPClientWrapper:
    def __init__(self, client):
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
    def genkey(self):
        self.sendall(b'GK')
        assert self.recvall(2) == b'GK', 'peer is not in key generation mode'
        sockecck = ECC.generate(curve = 'nistp256')
        sockexpk = sockecck.public_key().export_key(format = 'SEC1')
        self.sendall(sockexpk)
        peerexpk = self.recvall(65)
        peerecck = ECC.import_key(peerexpk, curve_name = 'nistp256')
        key = DH.key_agreement(static_priv = sockecck, static_pub = peerecck, kdf = lambda x: x)
        sockaesk = SHA224.new(sockexpk + key).digest()
        peeraesk = SHA224.new(peerexpk + key).digest()
        self.enc = AES.new(sockaesk[:16], AES.MODE_CTR, nonce = sockaesk[16:]).encrypt
        self.dec = AES.new(peeraesk[:16], AES.MODE_CTR, nonce = peeraesk[16:]).decrypt
    def sendstream(self, istream, r):
        self.sendall(b'SS')
        assert self.recvall(2) == b'RS', 'peer is not in receiving mode'
        size = 4094
        while size == 4094:
            data = istream.read(r[0] if 0 <= r[0] < 4094 else 4094)
            size = len(data)
            self.sendall(size.to_bytes(2, 'big') + data)
            r[0] -= size
    def recvstream(self, ostream, r):
        self.sendall(b'RS')
        assert self.recvall(2) == b'SS', 'peer is not in sending mode'
        size = int.from_bytes(self.recvall(2), 'big')
        while size == 4094:
            temp = self.recvall(4096)
            r[0] += ostream.write(temp[:4094])
            size = int.from_bytes(temp[4094:], 'big')
        data = self.recvall(size)
        r[0] += ostream.write(data)
    def chat(self):
        self.sendall(b'CH')
        assert self.recvall(2) == b'CH', 'peer is not in chat mode'
        def on_quit(event = None):
            time = datetime.now()
            self.sendall(int(time.timestamp()).to_bytes(4, 'big') + b'\0\0\0\0')
            root.destroy()
        def on_send(event = None):
            cont = line.get()
            data = cont.encode()
            size = len(data)
            if size > 16777215:
                tkinter.messagebox.showerror('Error', 'Message too long')
                return
            time = datetime.now()
            self.sendall(int(time.timestamp()).to_bytes(4, 'big') + b'\1' + size.to_bytes(3, 'big') + data)
            text.config(state = tkinter.NORMAL)
            text.insert(tkinter.END, time.strftime('%Y-%m-%d %H:%M:%S - Local:'), 'Local')
            text.insert(tkinter.END, '\n')
            text.insert(tkinter.END, cont)
            text.insert(tkinter.END, '\n')
            text.see(tkinter.END)
            text.config(state = tkinter.DISABLED)
            line.delete(0, tkinter.END)
        def on_file(event = None):
            path = filedialog.askopenfilename()
            if not path:
                return
            try:
                imgtk = ImageTk.PhotoImage(Image.open(path))
            except:
                messagebox.showerror('Error', 'Invalid image')
                return
            data = open(path, 'rb').read()
            size = len(data)
            if size > 16777215:
                messagebox.showerror('Error', 'Image too large')
                return
            time = datetime.now()
            self.sendall(int(time.timestamp()).to_bytes(4, 'big') + b'\2' + size.to_bytes(3, 'big') + data)
            text.config(state = tkinter.NORMAL)
            text.insert(tkinter.END, time.strftime('%Y-%m-%d %H:%M:%S - Local:'), 'Local')
            text.insert(tkinter.END, '\n')
            text.image_create(tkinter.END, image = imgtk)
            text.insert(tkinter.END, '\n')
            text.see(tkinter.END)
            text.config(state = tkinter.DISABLED)
            imgs.append(imgtk)
        def recvloop():
            while True:
                head = self.recvall(8)
                time = datetime.fromtimestamp(int.from_bytes(head[:4], 'big'))
                mode = head[4]
                data = self.recvall(int.from_bytes(head[5:], 'big'))
                fifo.put((time, mode, data))
                if mode == 0:
                    break
        def update():
            while not fifo.empty():
                time, mode, data = fifo.get()
                text.config(state = tkinter.NORMAL)
                if mode == 0:
                    text.insert(tkinter.END, time.strftime('%Y-%m-%d %H:%M:%S - Remote left the chat'), 'Remote')
                    text.insert(tkinter.END, '\n')
                elif mode == 1:
                    cont = data.decode()
                    text.insert(tkinter.END, time.strftime('%Y-%m-%d %H:%M:%S - Remote:'), 'Remote')
                    text.insert(tkinter.END, '\n')
                    text.insert(tkinter.END, cont)
                    text.insert(tkinter.END, '\n')
                elif mode == 2:
                    imgtk = ImageTk.PhotoImage(Image.open(io.BytesIO(data)))
                    text.insert(tkinter.END, time.strftime('%Y-%m-%d %H:%M:%S - Remote:'), 'Remote')
                    text.insert(tkinter.END, '\n')
                    text.image_create(tkinter.END, image = imgtk)
                    text.insert(tkinter.END, '\n')
                    imgs.append(imgtk)
                text.see(tkinter.END)
                text.config(state = tkinter.DISABLED)
            root.after(1, update)
        imgs = []
        root = tkinter.Tk()
        root.title('Chat')
        root.minsize(640, 480)
        root.protocol('WM_DELETE_WINDOW', on_quit)
        text = tkinter.Text(root, state = tkinter.DISABLED)
        text.tag_config('Local', foreground = 'red')
        text.tag_config('Remote', foreground = 'blue')
        down = tkinter.Frame(root)
        line = tkinter.Entry(down)
        line.bind('<Return>', on_send)
        send = tkinter.Button(down, text = 'Send', command = on_send)
        file = tkinter.Button(down, text = 'File', command = on_file)
        text.pack(fill = tkinter.BOTH, side = tkinter.TOP, expand = True)
        down.pack(fill = tkinter.X, side = tkinter.BOTTOM)
        line.pack(fill = tkinter.X, side = tkinter.LEFT, expand = True)
        send.pack(fill = tkinter.X, side = tkinter.RIGHT)
        file.pack(fill = tkinter.X, side = tkinter.RIGHT)
        fifo = queue.Queue()
        recv = threading.Thread(target = recvloop)
        recv.start()
        root.after(1, update)
        root.mainloop()
        recv.join()
def run(client, recv, send, chat, size, enc):
    C = TCPClientWrapper(client)
    if enc:
        C.genkey()
    if chat:
        C.chat()
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
    parser = argparse.ArgumentParser(description = "Chat and transfer files over TCP/IP")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--server', metavar = 'IP', nargs = '?', default = '', const = '', help = 'run as a server (default)')
    mode.add_argument('--client', metavar = 'IP', help = 'run as a client (server IP required)')
    parser.add_argument('--port', type = int, default = 4096, help = 'port number of the server (4096 by default)')
    action = parser.add_mutually_exclusive_group(required = True)
    action.add_argument('--send', metavar = 'FILENAME', nargs = '?', type = argparse.FileType('rb'), const = sys.stdin.buffer, help = 'send file')
    action.add_argument('--recv', metavar = 'FILENAME', nargs = '?', type = argparse.FileType('wb'), const = sys.stdout.buffer, help = 'receive file')
    action.add_argument('--chat', action = 'store_true', help = 'start a chat session')
    parser.add_argument('--size', type = int, help = 'set size limit (unlimited by default, ignored in the chat mode)')
    parser.add_argument('--enc', action = 'store_true', help = 'encrypt the connection with DHKE and AES-CTR (cannot be set on one side only)')
    args = parser.parse_args()
    if args.client:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((args.client, args.port))
        with client:
            run(client, args.recv, args.send, args.chat, args.size, args.enc)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((args.server, args.port))
        with server:
            server.listen(1)
            client, addr = server.accept()
            with client:
                run(client, args.recv, args.send, args.chat, args.size, args.enc)
if __name__ == '__main__':
    main()
