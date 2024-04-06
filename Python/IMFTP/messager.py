import io
import os
import tkinter
from tkinter import filedialog, messagebox
from datetime import datetime
from PIL import Image, ImageTk
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
        self.after(100, self.update)
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
        self.after(100, self.update) # avoid busy waiting
