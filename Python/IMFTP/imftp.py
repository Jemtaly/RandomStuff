#!/usr/bin/python3
from tkinter import filedialog, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import Crypto.PublicKey.ECC as ECC
import Crypto.Protocol.DH as DH
import Crypto.Cipher.AES as AES
import Crypto.Hash.SHA224 as SHA224
import os, sys, io, socket, threading, queue, tkinter
import argparse
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
    def keyexchange(self):
        self.sendall(b'KEYX')
        assert self.recvall(4) == b'KEYX', 'peer is not in key generation mode'
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
    def sendstream(self, istream, buff = sys.stderr):
        self.sendall(b'SBDS')
        assert self.recvall(4) == b'RBDS', 'peer is not in receiving mode'
        recd = 0
        while True:
            data = istream.read(0x0ffe)
            size = len(data)
            self.sendall(size.to_bytes(2, 'big') + data)
            buff.write('\r{} bytes sent'.format(recd := recd + size))
            if size < 0x0ffe:
                break
        buff.write('\n')
    def recvstream(self, ostream, buff = sys.stderr):
        self.sendall(b'RBDS')
        assert self.recvall(4) == b'SBDS', 'peer is not in sending mode'
        recd = 0
        size = int.from_bytes(self.recvall(2), 'big')
        while size == 0x0ffe:
            temp = self.recvall(0x1000)
            ostream.write(temp[:0x0ffe])
            buff.write('\r{} bytes received'.format(recd := recd + size))
            size = int.from_bytes(temp[0x0ffe:], 'big')
        data = self.recvall(size)
        ostream.write(data)
        buff.write('\r{} bytes received'.format(recd := recd + size))
        buff.write('\n')
    def chat(self):
        self.sendall(b'CHAT')
        assert self.recvall(4) == b'CHAT', 'peer is not in chat mode'
        rque = queue.Queue()
        sque = queue.Queue()
        def recvloop():
            while True:
                head = self.recvall(4)
                mode = head[0]
                data = self.recvall(int.from_bytes(head[1:], 'big'))
                rque.put((mode, data))
                if mode == 0:
                    break
        def sendloop():
            while True:
                mode, data = sque.get()
                size = len(data)
                self.sendall(bytes([mode]) + size.to_bytes(3, 'big') + data)
                if mode == 0:
                    break
        rthr = threading.Thread(target = recvloop)
        sthr = threading.Thread(target = sendloop)
        rthr.start()
        sthr.start()
        root = Messager(rque, sque, self.sockname(), self.peername())
        root.mainloop()
        rthr.join()
        sthr.join()
class Messager(tkinter.Tk):
    def __init__(self, rque, sque, sockname, peername):
        super().__init__()
        self.title('Chat - {}:{} <-> {}:{}'.format(*sockname, *peername))
        self.minsize(640, 480)
        TXTF = ('Consolas', 10)
        BTNF = ('Consolas', 10)
        URLF = ('Consolas', 10, 'underline')
        topf = tkinter.Frame(self)
        botf = tkinter.Frame(self)
        text = tkinter.Text(topf, font = TXTF, height = 10, bg = 'white')
        scrl = tkinter.Scrollbar(topf, command = text.yview)
        text.config(yscrollcommand = scrl.set)
        text.tag_config('Local', foreground = 'blue')
        text.tag_config('Remote', foreground = 'red')
        text.tag_config('Info', foreground = 'green')
        text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Chat started'), 'Info')
        text.insert(tkinter.END, '\n')
        text.config(state = tkinter.DISABLED)
        opnb = tkinter.Button(botf, text = 'File', command = self.on_file, font = BTNF)
        imgb = tkinter.Button(botf, text = 'Image', command = self.on_image, font = BTNF)
        entb = tkinter.Button(botf, text = 'Enter', command = self.on_enter, font = BTNF)
        entr = tkinter.Entry(botf, font = TXTF)
        entr.bind('<Return>', self.on_enter)
        botf.bind('<Destroy>', self.on_quit)
        topf.pack(fill = tkinter.BOTH, side = tkinter.TOP, expand = True)
        botf.pack(fill = tkinter.X, side = tkinter.BOTTOM)
        text.pack(fill = tkinter.BOTH, side = tkinter.LEFT, expand = True)
        scrl.pack(fill = tkinter.Y, side = tkinter.RIGHT)
        opnb.pack(fill = tkinter.X, side = tkinter.RIGHT)
        imgb.pack(fill = tkinter.X, side = tkinter.RIGHT)
        entb.pack(fill = tkinter.X, side = tkinter.RIGHT)
        entr.pack(fill = tkinter.X, side = tkinter.LEFT, expand = True)
        self.text = text
        self.entr = entr
        self.rque = rque
        self.sque = sque
        self.imgs = [] # prevent garbage collections
        self.TXTF = TXTF
        self.URLF = URLF
        self.after(1, self.update)
    def on_quit(self, event = None):
        self.sque.put((0, b''))
    def on_enter(self, event = None):
        cont = self.entr.get()
        try:
            data = cont.encode()
        except:
            messagebox.showerror('Error', 'Encoding error, invalid character(s) in the message')
            return
        size = len(data)
        if size > 0xffffff:
            tkinter.messagebox.showerror('Error', 'Message too long')
            return
        self.sque.put((1, data))
        self.text.config(state = tkinter.NORMAL)
        self.text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Local: '), 'Local')
        self.text.insert(tkinter.END, '\n')
        self.text.insert(tkinter.END, cont)
        self.text.insert(tkinter.END, '\n')
        self.text.see(tkinter.END)
        self.text.config(state = tkinter.DISABLED)
        self.entr.delete(0, tkinter.END)
    def on_image(self, event = None):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            data = open(path, 'rb').read()
            image = Image.open(io.BytesIO(data))
            imgtk = ImageTk.PhotoImage(image)
        except:
            messagebox.showerror('Error', 'Invalid image')
            return
        size = len(data)
        if size > 0xffffff:
            messagebox.showerror('Error', 'Image too large, should be less than 16 MiB')
            return
        self.sque.put((2, data))
        self.text.config(state = tkinter.NORMAL)
        self.text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Local: '), 'Local')
        self.text.insert(tkinter.END, '\n')
        self.text.image_create(tkinter.END, image = imgtk)
        self.text.insert(tkinter.END, '\n')
        self.text.see(tkinter.END)
        self.text.config(state = tkinter.DISABLED)
        self.imgs.append(imgtk)
    def on_file(self, event = None):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            data = os.path.basename(path).encode() + b'\0' + open(path, 'rb').read()
        except:
            messagebox.showerror('Error', 'Invalid file')
            return
        size = len(data)
        if size > 0xffffff:
            messagebox.showerror('Error', 'File too large, should be less than 16 MiB')
            return
        self.sque.put((3, data))
        self.text.config(state = tkinter.NORMAL)
        self.text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Sent file: '), 'Local')
        self.text.insert(tkinter.END, path, 'Local')
        self.text.insert(tkinter.END, '\n')
        self.text.see(tkinter.END)
        self.text.config(state = tkinter.DISABLED)
    def update(self):
        while not self.rque.empty():
            mode, data = self.rque.get()
            self.text.config(state = tkinter.NORMAL)
            if mode == 0:
                self.text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Remote left the chat'), 'Info')
                self.text.insert(tkinter.END, '\n')
            elif mode == 1:
                cont = data.decode()
                self.text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Remote: '), 'Remote')
                self.text.insert(tkinter.END, '\n')
                self.text.insert(tkinter.END, cont)
                self.text.insert(tkinter.END, '\n')
            elif mode == 2:
                image = Image.open(io.BytesIO(data))
                imgtk = ImageTk.PhotoImage(image)
                self.text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Remote: '), 'Remote')
                self.text.insert(tkinter.END, '\n')
                self.text.image_create(tkinter.END, image = imgtk)
                self.text.insert(tkinter.END, '\n')
                self.imgs.append(imgtk)
            elif mode == 3:
                name, data = data.split(b'\0', 1)
                base = name.decode()
                def save(event, base = base, data = data):
                    path = filedialog.asksaveasfilename(initialfile = base)
                    if path:
                        open(path, 'wb').write(data)
                self.text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Received file: '), 'Remote')
                link = tkinter.Label(self.text, text = base, fg = 'blue', cursor = 'hand2', font = self.TXTF, bg = 'white')
                link.bind('<Enter>', lambda event, link = link: link.config(font = self.URLF))
                link.bind('<Leave>', lambda event, link = link: link.config(font = self.TXTF))
                link.bind('<Button-1>', save)
                self.text.window_create(tkinter.END, window = link)
                self.text.insert(tkinter.END, '\n')
            self.text.see(tkinter.END)
            self.text.config(state = tkinter.DISABLED)
            self.deiconify()
        self.after(1, self.update)
def run(client, recv, send, chat, enc, buff):
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
    parser = argparse.ArgumentParser(description = "Chat and transfer files over TCP/IP")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--server', metavar = 'IP', nargs = '?', default = '', const = '', help = 'run as a server (default)')
    mode.add_argument('--client', metavar = 'IP', help = 'run as a client (server IP required)')
    parser.add_argument('--port', type = int, default = 4096, help = 'port number of the server (4096 by default)')
    action = parser.add_mutually_exclusive_group(required = True)
    action.add_argument('--send', metavar = 'FILENAME', nargs = '?', type = argparse.FileType('rb'), const = sys.stdin.buffer, help = 'send file')
    action.add_argument('--recv', metavar = 'FILENAME', nargs = '?', type = argparse.FileType('wb'), const = sys.stdout.buffer, help = 'receive file')
    action.add_argument('--chat', action = 'store_true', help = 'start a chat session')
    parser.add_argument('--enc', action = 'store_true', help = 'encrypt the connection with DHKE and AES-CTR (cannot be set on one side only)')
    parser.add_argument('--log', action = 'store_true', help = 'show sending/receiving progress')
    args = parser.parse_args()
    buff = sys.stderr if args.log else open(os.devnull, 'w')
    if args.client:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((args.client, args.port))
        with client:
            run(client, args.recv, args.send, args.chat, args.enc, buff)
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((args.server, args.port))
        with server:
            server.listen(1)
            client, addr = server.accept()
            with client:
                run(client, args.recv, args.send, args.chat, args.enc, buff)
if __name__ == '__main__':
    main()
