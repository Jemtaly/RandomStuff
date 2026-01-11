from abc import ABC, abstractmethod
from typing import ClassVar, TypeVar, Callable
from dataclasses import dataclass

from datetime import datetime
from pathlib import Path
from io import BytesIO

import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import PIL.Image as Image
import PIL.ImageTk as ImageTk

from Crypto.PublicKey import ECC
from Crypto.Cipher import AES
from Crypto.Protocol import DH
from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256

from .core import AbstractConnection, AbstractDataReceiver
from .cryption import TwoWayKeyExchanger


class ReceivedMessage(ABC):
    @abstractmethod
    def after_received(self, app: "Messager"): ...


T = TypeVar("T", bound="SerializableMessage")


class SerializableMessage(ReceivedMessage):
    tag: ClassVar[int]

    @classmethod
    @abstractmethod
    def deserialize(cls: type[T], data: bytes) -> T: ...

    @abstractmethod
    def serialize(self) -> bytes: ...


@dataclass
class NextEnableRegister:
    next_enable: Callable[[], None] | None = None


class KeyExchangeRequestMessage(SerializableMessage):
    tag = 0

    def __init__(self, pub: ECC.EccKey | None):
        self.pub = pub

    @classmethod
    def deserialize(cls, data: bytes) -> "KeyExchangeRequestMessage":
        if not data:
            return KeyExchangeRequestMessage(None)
        return KeyExchangeRequestMessage(ECC.import_key(data))

    def serialize(self) -> bytes:
        if self.pub is None:
            return b""
        return self.pub.export_key(format="DER")

    def after_received(self, app: "Messager"):
        app.after_key_exchange_request_received(self.pub)


class KeyExchangeResponseMessage(SerializableMessage):
    tag = 1

    def __init__(self):
        pass

    @classmethod
    def deserialize(cls, data: bytes) -> "KeyExchangeResponseMessage":
        return KeyExchangeResponseMessage()

    def serialize(self) -> bytes:
        return b""

    def after_received(self, app: "Messager"):
        app.after_key_exchange_response_received()


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

    def after_received(self, app: "Messager"):
        app.after_text_received(self.text)


class ImageMessage(SerializableMessage):
    tag = 3

    def __init__(self, data: bytes):
        self.data = data

    @classmethod
    def deserialize(cls, data: bytes) -> "ImageMessage":
        return ImageMessage(data)

    def serialize(self) -> bytes:
        return self.data

    def after_received(self, app: "Messager"):
        app.after_image_received(self.data)


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

    def after_received(self, app: "Messager"):
        app.after_file_received(self.name, self.data)


class UnknownMessage(ReceivedMessage):
    def __init__(self, tag: int, data: bytes):
        self.tag = tag
        self.data = data

    def after_received(self, app: "Messager"):
        app.after_unknown_received(self.tag, self.data)


class CorruptedMessage(ReceivedMessage):
    def __init__(self, error: Exception):
        self.error = error

    def after_received(self, app: "Messager"):
        app.after_corrupted_received(self.error)


class QuitNotification(ReceivedMessage):
    def after_received(self, app: "Messager"):
        app.after_quit_received()


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


class Messager(tk.Tk, AbstractDataReceiver):
    BTN_FONT = ("Consolas", 10)
    TXT_FONT = ("Consolas", 10)
    URL_FONT = ("Consolas", 10, "underline")

    SOCK_TAG = "Sock"
    PEER_TAG = "Peer"
    INFO_TAG = "Info"

    def __init__(self, connection: AbstractConnection):
        super().__init__()
        self.title(f"Chat - {connection.descriptor}")
        self.minsize(640, 480)
        topf = tk.Frame(self)
        botf = tk.Frame(self)
        text = tk.Text(topf, font=self.TXT_FONT, height=10, bg="white")
        scrl = tk.Scrollbar(topf, command=text.yview)
        text.config(yscrollcommand=scrl.set)
        text.tag_config(self.SOCK_TAG, foreground="blue")
        text.tag_config(self.PEER_TAG, foreground="red")
        text.tag_config(self.INFO_TAG, foreground="green")
        text.config(state=tk.DISABLED)
        keyx = tk.Button(botf, font=self.BTN_FONT, text="Key Exchange", command=self.on_key_exchange_request)
        opnb = tk.Button(botf, font=self.BTN_FONT, text="File", command=self.on_file)
        imgb = tk.Button(botf, font=self.BTN_FONT, text="Image", command=self.on_image)
        entb = tk.Button(botf, font=self.BTN_FONT, text="Enter", command=self.on_enter)
        entr = tk.Entry(botf, font=self.TXT_FONT)
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
        self.imgtk_storage: list[ImageTk.PhotoImage] = []
        self.last_register: NextEnableRegister | None = None
        self.self_quit = False

        self.sender = connection.start(self)
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
        self.send_key: bytes | None = self.key_exchanger.get_send_key()
        self.recv_key: bytes | None = self.key_exchanger.get_recv_key()

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
        self.sender.send(data)

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
            self.sender.send_quit()
        except Exception as e:
            pass

    def on_enter(self, event: tk.Event | None = None):
        try:
            text = self.entr.get()
            msg = TextMessage(text)
            self.send_message(msg)
            self.after_text_sent(text)
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
            self.after_image_sent(data)
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
            self.after_file_sent(name, data)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))

    def on_key_exchange_request(self, event: tk.Event | None = None):
        try:
            sec = ECC.generate(curve="P-224")
            pub = sec.public_key()
            msg = KeyExchangeRequestMessage(pub)
            self.send_message(msg)
            self.after_key_exchange_request_sent(sec)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))

    def on_key_exchange_response(self, event: tk.Event | None = None):
        try:
            msg = KeyExchangeResponseMessage()
            self.send_message(msg)
            self.after_key_exchange_response_sent()
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

    def after_key_exchange_request_sent(self, sec: ECC.EccKey | None):
        self.send_key = self.key_exchanger.after_sent_sec(sec)
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Key exchange request sent"), self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_key_exchange_request_received(self, pub: ECC.EccKey | None):
        self.recv_key = self.key_exchanger.after_received_pub(pub)
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Key exchange request received: "), self.INFO_TAG)
        link = tk.Label(self.text, font=self.TXT_FONT, bg="white", fg="gray", cursor="arrow", text="[pending]")
        register = NextEnableRegister()

        def response(event: tk.Event | None = None):
            self.on_key_exchange_response(event)
            link.config(font=self.TXT_FONT, bg="white", fg="green", cursor="arrow", text="[accepted]")
            link.unbind("<Enter>")
            link.unbind("<Leave>")
            link.unbind("<Button-1>")
            if register.next_enable is not None:
                register.next_enable()
            else:
                self.last_register = None

        def enable():
            link.config(font=self.TXT_FONT, bg="white", fg="blue", cursor="hand2", text="[accept]")
            link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_FONT))
            link.bind("<Leave>", lambda event, link=link: link.config(font=self.TXT_FONT))
            link.bind("<Button-1>", response)

        if self.last_register is None:
            enable()
        else:
            self.last_register.next_enable = enable
        self.last_register = register
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_key_exchange_response_sent(self):
        self.send_key = self.key_exchanger.after_sent_received_pub()
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Key exchange response sent"), self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_key_exchange_response_received(self):
        self.recv_key = self.key_exchanger.after_received_sent_sec()
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Key exchange response received"), self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_text_sent(self, text: str):
        self.entr.delete(0, tk.END)  # Clear input after sending
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Local: "), self.SOCK_TAG)
        self.text.insert(tk.END, "\n")
        self.text.insert(tk.END, text)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_text_received(self, text: str):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Remote: "), self.PEER_TAG)
        self.text.insert(tk.END, "\n")
        self.text.insert(tk.END, text)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_image_sent(self, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Local: "), self.SOCK_TAG)
        self.text.insert(tk.END, "\n")
        image = Image.open(BytesIO(data))
        imgtk = ImageTk.PhotoImage(image)
        self.text.image_create(tk.END, image=imgtk)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)
        self.imgtk_storage.append(imgtk)

    def after_image_received(self, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Remote: "), self.PEER_TAG)
        self.text.insert(tk.END, "\n")
        image = Image.open(BytesIO(data))
        imgtk = ImageTk.PhotoImage(image)
        self.text.image_create(tk.END, image=imgtk)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)
        self.imgtk_storage.append(imgtk)

    def after_file_sent(self, name: str, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Sent file: "), self.SOCK_TAG)
        link = tk.Label(self.text, font=self.TXT_FONT, bg="white", fg="blue", cursor="hand2", text=name)
        link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_FONT))
        link.bind("<Leave>", lambda event, link=link: link.config(font=self.TXT_FONT))

        def save(event: tk.Event | None = None):
            path = filedialog.asksaveasfilename(initialfile=name)
            if path:
                open(path, "wb").write(data)

        link.bind("<Button-1>", save)
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_file_received(self, name: str, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Received file: "), self.PEER_TAG)
        link = tk.Label(self.text, font=self.TXT_FONT, bg="white", fg="blue", cursor="hand2", text=name)
        link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_FONT))
        link.bind("<Leave>", lambda event, link=link: link.config(font=self.TXT_FONT))

        def save(event: tk.Event | None = None):
            path = filedialog.asksaveasfilename(initialfile=name)
            if path:
                open(path, "wb").write(data)

        link.bind("<Button-1>", save)
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_unknown_received(self, tag: int, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Received unknown message: "), self.PEER_TAG)
        link = tk.Label(self.text, font=self.TXT_FONT, bg="white", fg="blue", cursor="hand2", text=f"[tag = {tag}]")
        link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_FONT))
        link.bind("<Leave>", lambda event, link=link: link.config(font=self.TXT_FONT))

        def save(event: tk.Event | None = None):
            path = filedialog.asksaveasfilename(initialfile="unknown.bin")
            if path:
                open(path, "wb").write(data)

        link.bind("<Button-1>", save)
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_corrupted_received(self, error: Exception):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Received corrupted message: "), self.PEER_TAG)
        self.text.insert(tk.END, str(error))
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def after_quit_received(self):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, datetime.now().strftime("%Y-%m-%d %H:%M:%S - Remote has quit the chat"), self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)
