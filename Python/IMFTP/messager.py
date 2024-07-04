import io
import os
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
import PIL.Image as Image
import PIL.ImageTk as ImageTk
from datetime import datetime
class Messager(tk.Tk):
    def __init__(self, recv, send, sockname, peername):
        super().__init__()
        self.title('Chat - {}:{} <-> {}:{}'.format(*sockname, *peername))
        self.minsize(640, 480)
        TXTF = ('Consolas', 10)
        BTNF = ('Consolas', 10)
        URLF = ('Consolas', 10, 'underline')
        topf = tk.Frame(self)
        botf = tk.Frame(self)
        text = tk.Text(topf, font = TXTF, height = 10, bg = 'white')
        scrl = tk.Scrollbar(topf, command = text.yview)
        text.config(yscrollcommand = scrl.set)
        text.tag_config('Local', foreground = 'blue')
        text.tag_config('Remote', foreground = 'red')
        text.tag_config('Info', foreground = 'green')
        text.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Chat started'), 'Info')
        text.insert(tk.END, '\n')
        text.config(state = tk.DISABLED)
        opnb = tk.Button(botf, text = 'File', command = self.on_file, font = BTNF)
        imgb = tk.Button(botf, text = 'Image', command = self.on_image, font = BTNF)
        entb = tk.Button(botf, text = 'Enter', command = self.on_enter, font = BTNF)
        entr = tk.Entry(botf, font = TXTF)
        entr.bind('<Return>', self.on_enter)
        botf.bind('<Destroy>', self.on_quit)
        topf.pack(fill = tk.BOTH, side = tk.TOP, expand = True)
        botf.pack(fill = tk.X, side = tk.BOTTOM)
        text.pack(fill = tk.BOTH, side = tk.LEFT, expand = True)
        scrl.pack(fill = tk.Y, side = tk.RIGHT)
        opnb.pack(fill = tk.X, side = tk.RIGHT)
        imgb.pack(fill = tk.X, side = tk.RIGHT)
        entb.pack(fill = tk.X, side = tk.RIGHT)
        entr.pack(fill = tk.X, side = tk.LEFT, expand = True)
        self.text = text
        self.entr = entr
        self.recv = recv
        self.send = send
        self.imgs = [] # prevent garbage collections
        self.TXTF = TXTF
        self.URLF = URLF
        self.after(100, self.update)
    def on_quit(self, event = None):
        try:
            self.send(0, b'')
        except Exception as e:
            pass
    def on_enter(self, event = None):
        text = self.entr.get()
        try:
            data = text.encode('utf-8')
            self.send(1, data)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
        else:
            self.text.config(state = tk.NORMAL)
            self.text.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Local: '), 'Local')
            self.text.insert(tk.END, '\n')
            self.text.insert(tk.END, text)
            self.text.insert(tk.END, '\n')
            self.text.see(tk.END)
            self.text.config(state = tk.DISABLED)
            self.entr.delete(0, tk.END)
    def on_image(self, event = None):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            data = open(path, 'rb').read()
            image = Image.open(io.BytesIO(data))
            imgtk = ImageTk.PhotoImage(image)
            self.send(2, data)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
        else:
            self.text.config(state = tk.NORMAL)
            self.text.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Local: '), 'Local')
            self.text.insert(tk.END, '\n')
            self.text.image_create(tk.END, image = imgtk)
            self.text.insert(tk.END, '\n')
            self.text.see(tk.END)
            self.text.config(state = tk.DISABLED)
            self.imgs.append(imgtk)
    def on_file(self, event = None):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            data = os.path.basename(path).encode() + b'\0' + open(path, 'rb').read()
            self.send(3, data)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
        else:
            self.text.config(state = tk.NORMAL)
            self.text.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Sent file: '), 'Local')
            self.text.insert(tk.END, path, 'Local')
            self.text.insert(tk.END, '\n')
            self.text.see(tk.END)
            self.text.config(state = tk.DISABLED)
    def update(self):
        while cont := self.recv():
            mode, data = cont
            self.text.config(state = tk.NORMAL)
            if mode == -1:
                self.text.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Connection lost'), 'Info')
                self.text.insert(tk.END, '\n')
            elif mode == 0:
                self.text.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Remote left the chat'), 'Info')
                self.text.insert(tk.END, '\n')
            elif mode == 1:
                text = data.decode('utf-8')
                self.text.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Remote: '), 'Remote')
                self.text.insert(tk.END, '\n')
                self.text.insert(tk.END, text)
                self.text.insert(tk.END, '\n')
            elif mode == 2:
                image = Image.open(io.BytesIO(data))
                imgtk = ImageTk.PhotoImage(image)
                self.text.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Remote: '), 'Remote')
                self.text.insert(tk.END, '\n')
                self.text.image_create(tk.END, image = imgtk)
                self.text.insert(tk.END, '\n')
                self.imgs.append(imgtk)
            elif mode == 3:
                name, data = data.split(b'\0', 1)
                base = name.decode()
                def save(event, base = base, data = data):
                    path = filedialog.asksaveasfilename(initialfile = base)
                    if path:
                        open(path, 'wb').write(data)
                self.text.insert(tk.END, datetime.now().strftime('%Y-%m-%d %H:%M:%S - Received file: '), 'Remote')
                link = tk.Label(self.text, text = base, fg = 'blue', cursor = 'hand2', font = self.TXTF, bg = 'white')
                link.bind('<Enter>', lambda event, link = link: link.config(font = self.URLF))
                link.bind('<Leave>', lambda event, link = link: link.config(font = self.TXTF))
                link.bind('<Button-1>', save)
                self.text.window_create(tk.END, window = link)
                self.text.insert(tk.END, '\n')
            self.text.see(tk.END)
            self.text.config(state = tk.DISABLED)
            self.deiconify()
        self.after(100, self.update) # avoid busy waiting
