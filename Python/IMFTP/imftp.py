#!/usr/bin/python3
import os, sys, io, socket, threading, queue, tkinter
import Crypto.PublicKey.ECC as ECC
import Crypto.Protocol.DH as DH
import Crypto.Cipher.AES as AES
import Crypto.Hash.SHA224 as SHA224
from tkinter import filedialog, messagebox
from datetime import datetime
from PIL import Image, ImageTk
class Recorder:
    def __init__(self, v):
        self.v = v
    def __iadd__(self, v):
        self.v += v
    def __isub__(self, v):
        self.v -= v
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
    def sendstream(self, istream, recd):
        self.sendall(b'SBDS')
        assert self.recvall(4) == b'RBDS', 'peer is not in receiving mode'
        while True:
            data = istream.read(recd.v if 0x0000 <= recd.v < 0x0ffe else 0x0ffe)
            size = len(data)
            self.sendall(size.to_bytes(2, 'big') + data)
            recd -= size
            if size < 0x0ffe:
                break
    def recvstream(self, ostream, recd):
        self.sendall(b'RBDS')
        assert self.recvall(4) == b'SBDS', 'peer is not in sending mode'
        size = int.from_bytes(self.recvall(2), 'big')
        while size == 0x0ffe:
            temp = self.recvall(0x1000)
            recd += ostream.write(temp[:0x0ffe])
            size = int.from_bytes(temp[0x0ffe:], 'big')
        data = self.recvall(size)
        recd += ostream.write(data)
    def chat(self):
        self.sendall(b'CHAT')
        assert self.recvall(4) == b'CHAT', 'peer is not in chat mode'
        def on_quit(event = None):
            self.sendall(b'\0\0\0\0')
            root.destroy()
        def on_enter(event = None):
            cont = entr.get()
            try:
                data = cont.encode()
            except:
                messagebox.showerror('Error', 'Encoding error, invalid character(s) in the message')
                return
            size = len(data)
            if size > 0xffffff:
                tkinter.messagebox.showerror('Error', 'Message too long')
                return
            self.sendall(b'\1' + size.to_bytes(3, 'big') + data)
            text.config(state = tkinter.NORMAL)
            text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Local: '), 'Local')
            text.insert(tkinter.END, '\n')
            text.insert(tkinter.END, cont)
            text.insert(tkinter.END, '\n')
            text.see(tkinter.END)
            text.config(state = tkinter.DISABLED)
            entr.delete(0, tkinter.END)
        def on_image(event = None):
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
            self.sendall(b'\2' + size.to_bytes(3, 'big') + data)
            text.config(state = tkinter.NORMAL)
            text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Local: '), 'Local')
            text.insert(tkinter.END, '\n')
            text.image_create(tkinter.END, image = imgtk)
            text.insert(tkinter.END, '\n')
            text.see(tkinter.END)
            text.config(state = tkinter.DISABLED)
            imgs.append(imgtk)
        def on_file(event = None):
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
            self.sendall(b'\3' + size.to_bytes(3, 'big') + data)
            text.config(state = tkinter.NORMAL)
            text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Sent file: ') + path, 'Local')
            text.insert(tkinter.END, '\n')
            text.see(tkinter.END)
            text.config(state = tkinter.DISABLED)
        def recvloop():
            while True:
                head = self.recvall(4)
                mode = head[0]
                data = self.recvall(int.from_bytes(head[1:], 'big'))
                rque.put((mode, data))
                if mode == 0:
                    break
        def update():
            while not rque.empty():
                mode, data = rque.get()
                text.config(state = tkinter.NORMAL)
                if mode == 0:
                    text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Remote left the chat'), 'Remote')
                    text.insert(tkinter.END, '\n')
                elif mode == 1:
                    cont = data.decode()
                    text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Remote:'), 'Remote')
                    text.insert(tkinter.END, '\n')
                    text.insert(tkinter.END, cont)
                    text.insert(tkinter.END, '\n')
                elif mode == 2:
                    image = Image.open(io.BytesIO(data))
                    imgtk = ImageTk.PhotoImage(image)
                    text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Remote:'), 'Remote')
                    text.insert(tkinter.END, '\n')
                    text.image_create(tkinter.END, image = imgtk)
                    text.insert(tkinter.END, '\n')
                    imgs.append(imgtk)
                elif mode == 3:
                    name, data = data.split(b'\0', 1)
                    base = name.decode()
                    def save(event, base = base, data = data):
                        path = filedialog.asksaveasfilename(initialfile = base)
                        if path:
                            open(path, 'wb').write(data)
                    text.insert(tkinter.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Received file: '), 'Remote')
                    link = tkinter.Label(text, text = base, fg = 'blue', cursor = 'hand2', font = TXTF, bg = 'white')
                    link.bind('<Enter>', lambda event, link = link: link.config(font = URLF))
                    link.bind('<Leave>', lambda event, link = link: link.config(font = TXTF))
                    link.bind('<Button-1>', save)
                    text.window_create(tkinter.END, window = link)
                    text.insert(tkinter.END, '\n')
                text.see(tkinter.END)
                text.config(state = tkinter.DISABLED)
                root.deiconify()
            root.after(1, update)
        TXTF = ('Consolas', 10)
        BTNF = ('Consolas', 10)
        URLF = ('Consolas', 10, 'underline')
        imgs = [] # prevent garbage collection
        root = tkinter.Tk()
        root.title('Chat - {}:{} <-> {}:{}'.format(*self.sockname(), *self.peername()))
        root.minsize(640, 480)
        root.protocol('WM_DELETE_WINDOW', on_quit)
        topf = tkinter.Frame(root)
        text = tkinter.Text(topf, state = tkinter.DISABLED, font = TXTF, height = 10, bg = 'white')
        scrl = tkinter.Scrollbar(topf, command = text.yview)
        text.tag_config('Local', foreground = 'blue')
        text.tag_config('Remote', foreground = 'red')
        text.config(yscrollcommand = scrl.set)
        botf = tkinter.Frame(root)
        entr = tkinter.Entry(botf, font = TXTF)
        entb = tkinter.Button(botf, text = 'Enter', command = on_enter, font = BTNF)
        imgb = tkinter.Button(botf, text = 'Image', command = on_image, font = BTNF)
        opnb = tkinter.Button(botf, text = 'File', command = on_file, font = BTNF)
        entr.bind('<Return>', on_enter)
        topf.pack(fill = tkinter.BOTH, side = tkinter.TOP, expand = True)
        text.pack(fill = tkinter.BOTH, side = tkinter.LEFT, expand = True)
        scrl.pack(fill = tkinter.Y, side = tkinter.RIGHT)
        botf.pack(fill = tkinter.X, side = tkinter.BOTTOM)
        entr.pack(fill = tkinter.X, side = tkinter.LEFT, expand = True)
        entb.pack(fill = tkinter.X, side = tkinter.LEFT)
        imgb.pack(fill = tkinter.X, side = tkinter.LEFT)
        opnb.pack(fill = tkinter.X, side = tkinter.LEFT)
        rque = queue.Queue()
        thrd = threading.Thread(target = recvloop)
        thrd.start()
        root.after(1, update)
        root.mainloop()
        thrd.join()
def run(client, recv, send, chat, size, enc):
    C = TCPClientWrapper(client)
    if enc:
        C.keyexchange()
    if chat:
        C.chat()
    elif recv:
        recd = Recorder(+0 if size == None else size)
        C.recvstream(recv, recd)
        print(recd.v)
    elif send:
        recd = Recorder(~0 if size == None else size)
        C.sendstream(send, recd)
        print(recd.v)
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
