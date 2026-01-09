from abc import ABC, abstractmethod
from typing import ClassVar, TypeVar

import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from datetime import datetime
from pathlib import Path
from io import BytesIO

import PIL.Image as Image
import PIL.ImageTk as ImageTk

from Crypto.PublicKey import ECC
from Crypto.Cipher import AES
from Crypto.Protocol import DH
from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256

from .interfaces import AbstractMessagerBackendFactory, AbstractMessagerFrontend
from .cryption import TwoWayKeyExchanger


class QuitNotification:
    def after_received(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Peer has quit the chat"), "Info")
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)


class ReceivedMessage(ABC):
    @abstractmethod
    def after_received(self, app: "MessagerFrontend"): ...


T = TypeVar("T", bound="SerializableMessage")


class SerializableMessage(ReceivedMessage):
    tag: ClassVar[int]

    @classmethod
    @abstractmethod
    def deserialize(cls: type[T], data: bytes) -> T: ...

    @abstractmethod
    def serialize(self) -> bytes: ...


class KeyExchangeRequestMessage(SerializableMessage):
    tag = 0

    def __init__(self, pub_key: ECC.EccKey):
        self.pub_key = pub_key

    @classmethod
    def deserialize(cls, data: bytes) -> "KeyExchangeRequestMessage":
        return KeyExchangeRequestMessage(ECC.import_key(data))

    def serialize(self) -> bytes:
        return self.pub_key.export_key(format="DER")

    def after_sent(self, app: "MessagerFrontend", sec_key: ECC.EccKey):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Sent key exchange request"), "Info")
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)
        app.send_key = app.key_exchanger.after_sent_sec(sec_key)

    def after_received(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Received key exchange request: "), "Info")
        link = tk.Label(app.text, text="[accept]", fg="blue", cursor="hand2", font=app.URLF, bg="white")

        def response(event: tk.Event | None = None):
            app.on_key_exchange_response(event)
            link.config(fg="gray", cursor="arrow")
            link.unbind("<Enter>")
            link.unbind("<Leave>")
            link.unbind("<Button-1>")

        link.bind("<Enter>", lambda event, link=link: link.config(font=app.URLF + ("underline",)))
        link.bind("<Leave>", lambda event, link=link: link.config(font=app.URLF))
        link.bind("<Button-1>", response)
        app.text.window_create(tk.END, window=link)
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)
        app.recv_key = app.key_exchanger.after_received_pub(self.pub_key)


class KeyExchangeResponseMessage(SerializableMessage):
    tag = 1

    def __init__(self):
        pass

    @classmethod
    def deserialize(cls, data: bytes) -> "KeyExchangeResponseMessage":
        return KeyExchangeResponseMessage()

    def serialize(self) -> bytes:
        return b""

    def after_sent(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Sent key exchange response"), "Info")
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)
        app.send_key = app.key_exchanger.after_sent_received_pub()

    def after_received(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Received key exchange response"), "Info")
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)
        app.recv_key = app.key_exchanger.after_received_sent_sec()


class TextMessage(SerializableMessage):
    tag = 2

    def __init__(self, text: str, *, data: bytes | None = None):
        self.text = text
        if data is not None:
            self.data = data
        else:
            self.data = text.encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes) -> "TextMessage":
        return TextMessage(data.decode("utf-8"), data=data)

    def serialize(self) -> bytes:
        return self.data

    def after_sent(self, app: "MessagerFrontend"):
        app.entr.delete(0, tk.END)  # Clear input after sending
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Local: "), "Local")
        app.text.insert(tk.END, "\n")
        app.text.insert(tk.END, self.text)
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)

    def after_received(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Remote: "), "Remote")
        app.text.insert(tk.END, "\n")
        app.text.insert(tk.END, self.text)
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)


class ImageMessage(SerializableMessage):
    tag = 3

    def __init__(self, data: bytes):
        self.data = data
        self.image = Image.open(BytesIO(data))
        self.imgtk = ImageTk.PhotoImage(self.image)

    @classmethod
    def deserialize(cls, data: bytes) -> "ImageMessage":
        return ImageMessage(data)

    def serialize(self) -> bytes:
        return self.data

    def after_sent(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Local: "), "Local")
        app.text.insert(tk.END, "\n")
        app.text.image_create(tk.END, image=self.imgtk)
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)
        app.cache.append(self.imgtk)

    def after_received(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Remote: "), "Remote")
        app.text.insert(tk.END, "\n")
        app.text.image_create(tk.END, image=self.imgtk)
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)
        app.cache.append(self.imgtk)


class FileMessage(SerializableMessage):
    tag = 4

    def __init__(self, name: str, data: bytes):
        self.name = name
        self.data = data

    @classmethod
    def deserialize(cls, data: bytes) -> "FileMessage":
        name, data = data.split(b"\0", 1)
        return FileMessage(name.decode(), data)

    def serialize(self) -> bytes:
        return self.name.encode() + b"\0" + self.data

    def save(self, event: tk.Event | None = None):
        path = filedialog.asksaveasfilename(initialfile=self.name)
        if path:
            open(path, "wb").write(self.data)

    def after_sent(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Sent file: "), "Local")
        link = tk.Label(app.text, text=self.name, fg="blue", cursor="hand2", font=("Consolas", 10), bg="white")
        link.bind("<Enter>", lambda event, link=link: link.config(font=("Consolas", 10, "underline")))
        link.bind("<Leave>", lambda event, link=link: link.config(font=("Consolas", 10)))
        link.bind("<Button-1>", self.save)
        app.text.window_create(tk.END, window=link)
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)

    def after_received(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Received file: "), "Remote")
        link = tk.Label(app.text, text=self.name, fg="blue", cursor="hand2", font=("Consolas", 10), bg="white")
        link.bind("<Enter>", lambda event, link=link: link.config(font=("Consolas", 10, "underline")))
        link.bind("<Leave>", lambda event, link=link: link.config(font=("Consolas", 10)))
        link.bind("<Button-1>", self.save)
        app.text.window_create(tk.END, window=link)
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)


class UnknownMessage(ReceivedMessage):
    def __init__(self, tag: int, data: bytes):
        self.tag = tag
        self.data = data

    def save(self, app: "MessagerFrontend"):
        path = filedialog.asksaveasfilename(initialfile="unknown.bin")
        if path:
            open(path, "wb").write(self.data)

    def after_received(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Received unknown message: "), "Remote")
        link = tk.Label(app.text, text=f"[tag = {self.tag}]", fg="blue", cursor="hand2", font=("Consolas", 10), bg="white")
        link.bind("<Enter>", lambda event, link=link: link.config(font=("Consolas", 10, "underline")))
        link.bind("<Leave>", lambda event, link=link: link.config(font=("Consolas", 10)))
        link.bind("<Button-1>", lambda event: self.save(app))
        app.text.window_create(tk.END, window=link)
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)


class CorruptedMessage(ReceivedMessage):
    def __init__(self, error: Exception):
        self.error = error

    def after_received(self, app: "MessagerFrontend"):
        app.text.config(state=tk.NORMAL)
        app.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Received corrupted message: "), "Remote")
        app.text.insert(tk.END, str(self.error))
        app.text.insert(tk.END, "\n")
        app.text.see(tk.END)
        app.text.config(state=tk.DISABLED)


MESSAGE_KINDS: dict[int, type[SerializableMessage]] = {
    cls.tag: cls
    for cls in (
        TextMessage,
        ImageMessage,
        FileMessage,
        KeyExchangeRequestMessage,
        KeyExchangeResponseMessage,
    )
}


class MessagerFrontend(tk.Tk, AbstractMessagerFrontend):
    def __init__(self, factory: AbstractMessagerBackendFactory):
        super().__init__()
        self.backend = factory.create(self)
        self.key_exchanger = TwoWayKeyExchanger[
            ECC.EccKey | None,
            ECC.EccKey | None,
            bytes | None,
        ](
            lambda sec, pub: None
            if sec is None or pub is None
            else DH.key_agreement(
                static_priv=sec,
                static_pub=pub,
                kdf=lambda key: HKDF(key, 16, None, hashmod=SHA256),
            ),
            initial_sec=None,
            initial_pub=None,
        )
        self.send_key = self.key_exchanger.get_send_key()
        self.recv_key = self.key_exchanger.get_recv_key()
        self.self_quit = False

        self.title(f"Chat - {self.backend.descriptor}")
        self.minsize(640, 480)
        TXTF = ("Consolas", 10)
        BTNF = ("Consolas", 10)
        URLF = ("Consolas", 10, "underline")
        topf = tk.Frame(self)
        botf = tk.Frame(self)
        text = tk.Text(topf, font=TXTF, height=10, bg="white")
        scrl = tk.Scrollbar(topf, command=text.yview)
        text.config(yscrollcommand=scrl.set)
        text.tag_config("Local", foreground="blue")
        text.tag_config("Remote", foreground="red")
        text.tag_config("Info", foreground="green")
        text.config(state=tk.DISABLED)
        keyx = tk.Button(botf, text="Key Exchange", command=self.on_key_exchange_request, font=BTNF)
        opnb = tk.Button(botf, text="File", command=self.on_file, font=BTNF)
        imgb = tk.Button(botf, text="Image", command=self.on_image, font=BTNF)
        entb = tk.Button(botf, text="Enter", command=self.on_enter, font=BTNF)
        entr = tk.Entry(botf, font=TXTF)
        entr.bind("<Return>", self.on_enter)
        botf.bind("<Destroy>", self.on_quit)
        topf.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        botf.pack(fill=tk.X, side=tk.BOTTOM)
        text.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        scrl.pack(fill=tk.Y, side=tk.RIGHT)
        keyx.pack(fill=tk.X, side=tk.RIGHT)
        opnb.pack(fill=tk.X, side=tk.RIGHT)
        imgb.pack(fill=tk.X, side=tk.RIGHT)
        entb.pack(fill=tk.X, side=tk.RIGHT)
        entr.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.text = text
        self.entr = entr
        self.cache = []
        self.TXTF = TXTF
        self.URLF = URLF

    def encrypt(self, data: bytes):
        if self.send_key:
            cipher = AES.new(self.send_key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            return cipher.nonce + tag + ciphertext
        return data

    def decrypt(self, data: bytes):
        if self.recv_key:
            nonce = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            cipher = AES.new(self.recv_key, AES.MODE_EAX, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        return data

    def send_message(self, msg: SerializableMessage):
        data = bytes([msg.tag]) + msg.serialize()
        data = self.encrypt(data)
        self.backend.send(data)

    def decode_message(self, data: bytes) -> ReceivedMessage:
        try:
            data = self.decrypt(data)
        except Exception as e:
            return CorruptedMessage(e)
        tag = data[0]
        body = data[1:]
        cls = MESSAGE_KINDS.get(tag)
        if cls:
            return cls.deserialize(body)
        else:
            return UnknownMessage(tag, body)

    def on_quit(self, event: tk.Event | None = None):
        self.self_quit = True
        try:
            self.backend.send_quit()
        except Exception as e:
            pass

    def on_enter(self, event: tk.Event | None = None):
        try:
            text = self.entr.get()
            msg = TextMessage(text)
            self.send_message(msg)
            msg.after_sent(self)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))

    def on_image(self, event: tk.Event | None = None):
        try:
            filename = filedialog.askopenfilename()
            if not filename:
                return
            data = open(filename, "rb").read()
            msg = ImageMessage(data)
            self.send_message(msg)
            msg.after_sent(self)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))

    def on_file(self, event: tk.Event | None = None):
        try:
            filename = filedialog.askopenfilename()
            if not filename:
                return
            name = Path(filename).name
            data = open(filename, "rb").read()
            msg = FileMessage(name, data)
            self.send_message(msg)
            msg.after_sent(self)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))

    def on_key_exchange_request(self, event: tk.Event | None = None):
        try:
            sec_key = ECC.generate(curve="P-224")
            pub_key = sec_key.public_key()
            msg = KeyExchangeRequestMessage(pub_key)
            self.send_message(msg)
            msg.after_sent(self, sec_key)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))

    def on_key_exchange_response(self, event: tk.Event | None = None):
        try:
            msg = KeyExchangeResponseMessage()
            self.send_message(msg)
            msg.after_sent(self)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))

    def process(self, data: bytes):
        def handle():
            if self.self_quit:
                return
            try:
                msg = self.decode_message(data)
                msg.after_received(self)
            except Exception as e:
                messagebox.showerror(e.__class__.__name__, str(e))

        self.after(0, handle)

    def process_quit(self):
        def handle():
            if self.self_quit:
                return
            try:
                msg = QuitNotification()
                msg.after_received(self)
            except Exception as e:
                messagebox.showerror(e.__class__.__name__, str(e))

        self.after(0, handle)
