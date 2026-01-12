from abc import ABC, abstractmethod
from typing import ClassVar, TypeVar, Callable, ParamSpec
from dataclasses import dataclass
from contextlib import suppress

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

from queue import Queue
from threading import Thread

from .core import AbstractConnection, AbstractDataReceiver
from .cryption import TwoWayKeyExchanger


T = TypeVar("T", bound="DeserializableMessage")


class DeserializableMessage(ABC):
    tag: ClassVar[int]

    @classmethod
    @abstractmethod
    def deserialize(cls: type[T], data: bytes) -> T: ...

    @abstractmethod
    def after_received(self, app: "Messager"): ...


@dataclass
class NextEnableRegister:
    next_enable: Callable[[], None] | None = None


class KeyExchangeRequestMessage(DeserializableMessage):
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


class KeyExchangeResponseMessage(DeserializableMessage):
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


class TextMessage(DeserializableMessage):
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


class ImageMessage(DeserializableMessage):
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


class FileMessage(DeserializableMessage):
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


MESSAGE_KINDS: dict[int, type[DeserializableMessage]] = {
    cls.tag: cls
    for cls in (
        TextMessage,
        ImageMessage,
        FileMessage,
        KeyExchangeRequestMessage,
        KeyExchangeResponseMessage,
    )
}


P = ParamSpec("P")


class Crypter:
    def __init__(
        self,
        *,
        initial_sec: ECC.EccKey | None = None,
        initial_pub: ECC.EccKey | None = None,
    ):
        self._key_exchanger = TwoWayKeyExchanger[
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
            initial_sec=initial_sec,
            initial_pub=initial_pub,
        )
        self._send_key = self._key_exchanger.get_send_key()
        self._recv_key = self._key_exchanger.get_recv_key()

    def encrypt(self, data: bytes):
        if self._send_key:
            cipher = AES.new(self._send_key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            return cipher.nonce + tag + ciphertext
        return data

    def decrypt(self, data: bytes):
        if self._recv_key:
            nonce = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            cipher = AES.new(self._recv_key, AES.MODE_EAX, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        return data

    def after_sent_sec(self, sec: ECC.EccKey | None):
        self._send_key = self._key_exchanger.after_sent_sec(sec)

    def after_received_pub(self, pub: ECC.EccKey | None):
        self._recv_key = self._key_exchanger.after_received_pub(pub)

    def after_sent_received_pub(self):
        self._send_key = self._key_exchanger.after_sent_received_pub()

    def after_received_sent_sec(self):
        self._recv_key = self._key_exchanger.after_received_sent_sec()


class Messager(tk.Tk, AbstractDataReceiver):
    BTN_FONT = ("Consolas", 10)
    TXT_FONT = ("Consolas", 10)
    TLE_FONT = ("Consolas", 10, "bold")
    TAG_FONT = ("Consolas", 10)
    URL_FONT = ("Consolas", 10, "underline")

    INFO_TAG = "Info"

    def __init__(self, connection: AbstractConnection):
        super().__init__()
        self.title(f"Chat - {connection.descriptor}")
        self.minsize(640, 480)
        frame_top = tk.Frame(self)
        frame_bot = tk.Frame(self)
        text = tk.Text(frame_top, font=self.TXT_FONT, height=10, bg="white")
        scrollbar = tk.Scrollbar(frame_top, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        text.tag_config(self.INFO_TAG, font=self.TLE_FONT)  # Title tag
        text.config(state=tk.DISABLED)
        b_keyx = tk.Button(frame_bot, font=self.BTN_FONT, text="Key Exchange", command=self.on_key_exchange_request)
        b_file = tk.Button(frame_bot, font=self.BTN_FONT, text="File", command=self.on_file)
        b_pics = tk.Button(frame_bot, font=self.BTN_FONT, text="Image", command=self.on_image)
        b_text = tk.Button(frame_bot, font=self.BTN_FONT, text="Enter", command=self.on_enter)
        entry = tk.Entry(frame_bot, font=self.TXT_FONT)
        entry.bind("<Return>", self.on_enter)
        frame_bot.bind("<Destroy>", self.on_quit)
        frame_top.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        frame_bot.pack(fill=tk.X, side=tk.BOTTOM)
        text.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        b_keyx.pack(fill=tk.X, side=tk.RIGHT)
        b_file.pack(fill=tk.X, side=tk.RIGHT)
        b_pics.pack(fill=tk.X, side=tk.RIGHT)
        b_text.pack(fill=tk.X, side=tk.RIGHT)
        entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.text = text
        self.entry = entry
        self.imgtk_storage: list[ImageTk.PhotoImage] = []
        self.last_register: NextEnableRegister | None = None
        self.is_active = True

        self.sender = connection.start(self)
        self.crypter = Crypter()

        self.task_queue = Queue[Callable[[], None] | None]()

        def send_loop():
            while True:
                task = self.task_queue.get()
                if task is None:
                    break
                with suppress(Exception):
                    task()
            with suppress(Exception):
                self.sender.send_quit()

        Thread(target=send_loop, daemon=True).start()

    def process(self, data: bytes):
        try:
            data = self.crypter.decrypt(data)
        except Exception:
            return self.after_corrupted_received()
        try:
            tag, body = data[0], data[1:]
        except Exception:
            return self.after_empty_received()
        try:
            cls = MESSAGE_KINDS[tag]
        except Exception:
            return self.after_unknown_received(tag, body)
        try:
            msg = cls.deserialize(body)
        except Exception:
            return self.after_undeserialized_received(cls, body)
        return msg.after_received(self)

    def process_quit(self):
        return self.after_quit_received()

    def post(self, func: Callable[P, None], *args: P.args, **kwargs: P.kwargs):
        def handle():
            if not self.is_active:
                return
            with suppress(Exception):
                func(*args, **kwargs)

        self.after(0, handle)

    def create_received_label(self) -> tk.Label:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return tk.Label(self.text, font=self.TAG_FONT, bg="white", fg="blue", text=f"[received] {time}")

    def create_sending_label(self) -> tk.Label:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return tk.Label(self.text, font=self.TAG_FONT, bg="white", fg="gray", text=f"[sending] {time}")

    def update_sending_label(self, label: tk.Label, success: bool):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if success:
            label.config(font=self.TAG_FONT, bg="white", fg="green", text=f"[sent] {time}")
        else:
            label.config(font=self.TAG_FONT, bg="white", fg="red", text=f"[failed] {time}")

    def on_quit(self, event: tk.Event | None = None):
        self.is_active = False
        self.task_queue.put(None)

    def on_key_exchange_request(self, event: tk.Event | None = None):
        try:
            sec = ECC.generate(curve="P-224")
            pub = sec.public_key()
            msg = KeyExchangeRequestMessage(pub)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
            return

        def task():
            label = self.create_sending_label()
            try:
                self.post(self.show_key_exchange_request_sending, label, sec)
                self.sender.send(self.crypter.encrypt(bytes([msg.tag]) + msg.serialize()))
                self.crypter.after_sent_sec(sec)
            except Exception:
                self.post(self.update_sending_label, label, False)
            else:
                self.post(self.update_sending_label, label, True)

        self.task_queue.put(task)

    def on_key_exchange_response(self, event: tk.Event | None = None):
        try:
            msg = KeyExchangeResponseMessage()
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
            return

        def task():
            label = self.create_sending_label()
            try:
                self.post(self.show_key_exchange_response_message, label)
                self.sender.send(self.crypter.encrypt(bytes([msg.tag]) + msg.serialize()))
                self.crypter.after_sent_received_pub()
            except Exception:
                self.post(self.update_sending_label, label, False)
            else:
                self.post(self.update_sending_label, label, True)

        self.task_queue.put(task)

    def on_enter(self, event: tk.Event | None = None):
        try:
            text = self.entry.get()
            self.entry.delete(0, tk.END)
            msg = TextMessage(text)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
            return

        def task():
            label = self.create_sending_label()
            try:
                self.post(self.show_text_message, label, text)
                self.sender.send(self.crypter.encrypt(bytes([msg.tag]) + msg.serialize()))
            except Exception:
                self.post(self.update_sending_label, label, False)
            else:
                self.post(self.update_sending_label, label, True)

        self.task_queue.put(task)

    def on_image(self, event: tk.Event | None = None):
        try:
            filename = filedialog.askopenfilename()
            if not filename:
                return
            data = open(filename, "rb").read()
            msg = ImageMessage(data)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
            return

        def task():
            label = self.create_sending_label()
            try:
                self.post(self.show_image_message, label, data)
                self.sender.send(self.crypter.encrypt(bytes([msg.tag]) + msg.serialize()))
            except Exception:
                self.post(self.update_sending_label, label, False)
            else:
                self.post(self.update_sending_label, label, True)

        self.task_queue.put(task)

    def on_file(self, event: tk.Event | None = None):
        try:
            filename = filedialog.askopenfilename()
            if not filename:
                return
            name = Path(filename).name
            data = open(filename, "rb").read()
            msg = FileMessage(name, data)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
            return

        def task():
            label = self.create_sending_label()
            try:
                self.post(self.show_file_message, label, name, data)
                self.sender.send(self.crypter.encrypt(bytes([msg.tag]) + msg.serialize()))
            except Exception:
                self.post(self.update_sending_label, label, False)
            else:
                self.post(self.update_sending_label, label, True)

        self.task_queue.put(task)

    def after_key_exchange_request_received(self, pub: ECC.EccKey | None):
        label = self.create_received_label()
        self.crypter.after_received_pub(pub)
        self.post(self.show_key_exchange_request_received, label, pub)

    def after_key_exchange_response_received(self):
        label = self.create_received_label()
        self.crypter.after_received_sent_sec()
        self.post(self.show_key_exchange_response_message, label)

    def after_text_received(self, text: str):
        label = self.create_received_label()
        self.post(self.show_text_message, label, text)

    def after_image_received(self, data: bytes):
        label = self.create_received_label()
        self.post(self.show_image_message, label, data)

    def after_file_received(self, name: str, data: bytes):
        label = self.create_received_label()
        self.post(self.show_file_message, label, name, data)

    def after_corrupted_received(self):
        label = self.create_received_label()
        self.post(self.show_corrupted_message, label)

    def after_empty_received(self):
        label = self.create_received_label()
        self.post(self.show_empty_message, label)

    def after_unknown_received(self, tag: int, data: bytes):
        label = self.create_received_label()
        self.post(self.show_unknown_message, label, tag, data)

    def after_undeserialized_received(self, cls: type[DeserializableMessage], data: bytes):
        label = self.create_received_label()
        self.post(self.show_undeserialized_message, label, cls, data)

    def after_quit_received(self):
        label = self.create_received_label()
        self.post(self.show_quit_message, label)

    def show_key_exchange_request_sending(self, label: tk.Label, sec: ECC.EccKey | None):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Key exchange request", self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_key_exchange_request_received(self, label: tk.Label, pub: ECC.EccKey | None):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Key exchange request: ", self.INFO_TAG)
        link = tk.Label(self.text, font=self.TAG_FONT, bg="white", fg="gray", cursor="arrow", text="[pending]")
        register = NextEnableRegister()

        def accept(event: tk.Event | None = None):
            self.on_key_exchange_response(event)
            link.config(font=self.TAG_FONT, bg="white", fg="green", cursor="arrow", text="[accepted]")
            link.unbind("<Enter>")
            link.unbind("<Leave>")
            link.unbind("<Button-1>")
            if register.next_enable is not None:
                register.next_enable()
            else:
                self.last_register = None

        def enable():
            link.config(font=self.TAG_FONT, bg="white", fg="blue", cursor="hand2", text="[accept]")
            link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_FONT))
            link.bind("<Leave>", lambda event, link=link: link.config(font=self.TAG_FONT))
            link.bind("<Button-1>", accept)

        if self.last_register is None:
            enable()
        else:
            self.last_register.next_enable = enable
        self.last_register = register
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_key_exchange_response_message(self, label: tk.Label):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Key exchange response", self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_text_message(self, label: tk.Label, text: str):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Message: ", self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.insert(tk.END, text)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_image_message(self, label: tk.Label, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Image: ", self.INFO_TAG)
        try:
            image = Image.open(BytesIO(data))
            imgtk = ImageTk.PhotoImage(image)
            self.imgtk_storage.append(imgtk)
        except Exception:
            link = tk.Label(self.text, font=self.TAG_FONT, bg="white", fg="blue", cursor="hand2", text="[corrupted image]")
            link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_FONT))
            link.bind("<Leave>", lambda event, link=link: link.config(font=self.TAG_FONT))

            def save(event: tk.Event | None = None):
                path = filedialog.asksaveasfilename(initialfile="image.bin")
                if path:
                    open(path, "wb").write(data)

            link.bind("<Button-1>", save)
            self.text.window_create(tk.END, window=link)
        else:
            self.text.insert(tk.END, "\n")
            self.text.image_create(tk.END, image=imgtk)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_file_message(self, label: tk.Label, name: str, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "File: ", self.INFO_TAG)
        link = tk.Label(self.text, font=self.TAG_FONT, bg="white", fg="blue", cursor="hand2", text=name)
        link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_FONT))
        link.bind("<Leave>", lambda event, link=link: link.config(font=self.TAG_FONT))

        def save(event: tk.Event | None = None):
            path = filedialog.asksaveasfilename(initialfile=name)
            if path:
                open(path, "wb").write(data)

        link.bind("<Button-1>", save)
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_corrupted_message(self, label: tk.Label):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Corrupted message", self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_empty_message(self, label: tk.Label):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Empty message", self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_unknown_message(self, label: tk.Label, tag: int, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Unknown message: ", self.INFO_TAG)
        link = tk.Label(self.text, font=self.TAG_FONT, bg="white", fg="blue", cursor="hand2", text=f"[tag = {tag}]")
        link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_FONT))
        link.bind("<Leave>", lambda event, link=link: link.config(font=self.TAG_FONT))

        def save(event: tk.Event | None = None):
            path = filedialog.asksaveasfilename(initialfile="unknown.bin")
            if path:
                open(path, "wb").write(data)

        link.bind("<Button-1>", save)
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_undeserialized_message(self, label: tk.Label, cls: type[DeserializableMessage], data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Undeserializable message: ", self.INFO_TAG)
        link = tk.Label(self.text, font=self.TAG_FONT, bg="white", fg="blue", cursor="hand2", text=f"[class = {cls.__name__}]")
        link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_FONT))
        link.bind("<Leave>", lambda event, link=link: link.config(font=self.TAG_FONT))

        def save(event: tk.Event | None = None):
            path = filedialog.asksaveasfilename(initialfile="unknown.bin")
            if path:
                open(path, "wb").write(data)

        link.bind("<Button-1>", save)
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def show_quit_message(self, label: tk.Label):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=label)
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Connection closed", self.INFO_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)
