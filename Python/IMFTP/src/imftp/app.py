from abc import ABC, abstractmethod
from typing import ClassVar, TypeVar, ParamSpec, Callable
from dataclasses import dataclass, field

from contextlib import suppress
from threading import Thread
from queue import Queue

from pathlib import Path
from io import BytesIO

from datetime import datetime

import PIL.Image as Image
import PIL.ImageTk as ImageTk

import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

from Crypto.PublicKey import ECC
from Crypto.Cipher import AES
from Crypto.Protocol import DH
from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256

from .core import AbstractConnection, AbstractDataReceiver
from .cryption import TwoWayKeyExchanger


D = TypeVar("D", bound="DeserializableMessage")


class DeserializableMessage(ABC):
    tag: ClassVar[int]

    @classmethod
    @abstractmethod
    def deserialize(cls: type[D], data: bytes) -> D: ...

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


def generate_key(sec: ECC.EccKey | None, pub: ECC.EccKey | None) -> bytes | None:
    if sec is None or pub is None:
        return None
    return DH.key_agreement(
        static_priv=sec,
        static_pub=pub,
        kdf=lambda key: HKDF(key, 16, None, hashmod=SHA256),
    )


T = TypeVar("T")
S = TypeVar("S", bound="State")


class State(ABC):
    @property
    @abstractmethod
    def last_time(self) -> datetime: ...

    @property
    @abstractmethod
    def icon(self) -> str: ...

    @property
    @abstractmethod
    def info(self) -> dict[str, str]: ...


@dataclass(frozen=True)
class QuitState(State):
    quit_time: datetime = field(default_factory=datetime.now)

    @property
    def icon(self) -> str:
        return "🚪"

    @property
    def last_time(self) -> datetime:
        return self.quit_time

    @property
    def info(self) -> dict[str, str]:
        return {
            "Quit Time": self.quit_time.isoformat(),
        }


@dataclass(frozen=True)
class CorruptedState(State):
    received_time: datetime = field(default_factory=datetime.now)

    @property
    def icon(self) -> str:
        return "❗"

    @property
    def last_time(self) -> datetime:
        return self.received_time

    @property
    def info(self) -> dict[str, str]:
        return {
            "Received Time": self.received_time.isoformat(),
        }


@dataclass(frozen=True)
class ReceivedState(State):
    key: bytes | None
    received_time: datetime = field(default_factory=datetime.now)

    @property
    def icon(self) -> str:
        return "📥"

    @property
    def last_time(self) -> datetime:
        return self.received_time

    @property
    def info(self) -> dict[str, str]:
        return {
            "Received Time": self.received_time.isoformat(),
            "Reception Status": "secured" if self.key is not None else "unsecured",
        }


@dataclass(frozen=True)
class PendingState(State):
    posted_time: datetime = field(default_factory=datetime.now)

    @property
    def icon(self) -> str:
        return "⏳"

    @property
    def last_time(self) -> datetime:
        return self.posted_time

    @property
    def info(self) -> dict[str, str]:
        return {
            "Posted Time": self.posted_time.isoformat(),
        }


@dataclass(frozen=True)
class SendingState(State):
    pending_state: PendingState
    key: bytes | None
    started_time: datetime = field(default_factory=datetime.now)

    @property
    def icon(self) -> str:
        return "📤"

    @property
    def last_time(self) -> datetime:
        return self.started_time

    @property
    def info(self) -> dict[str, str]:
        return self.pending_state.info | {
            "Started Time": self.started_time.isoformat(),
            "Sending Status": "secured" if self.key is not None else "unsecured",
        }


@dataclass(frozen=True)
class SentSuccessState(State):
    sending_state: SendingState
    finished_time: datetime = field(default_factory=datetime.now)

    @property
    def icon(self) -> str:
        return "✅"

    @property
    def last_time(self) -> datetime:
        return self.finished_time

    @property
    def info(self) -> dict[str, str]:
        return self.sending_state.info | {
            "Finished Time": self.finished_time.isoformat(),
        }


@dataclass(frozen=True)
class SentFailureState(State):
    sending_state: SendingState
    finished_time: datetime = field(default_factory=datetime.now)

    @property
    def icon(self) -> str:
        return "❌"

    @property
    def last_time(self) -> datetime:
        return self.finished_time

    @property
    def info(self) -> dict[str, str]:
        return self.sending_state.info | {
            "Finished Time": self.finished_time.isoformat(),
        }


P = ParamSpec("P")
R = TypeVar("R")


class Messager(tk.Tk, AbstractDataReceiver):
    BTN_FONT = ("Segoe UI", 10)
    TAG_FONT = ("Segoe UI", 10, "bold")
    LBL_NORM = ("Segoe UI", 10, "bold")
    LBL_HIGH = ("Segoe UI", 10, "bold", "underline")
    TXT_FONT = ("Segoe UI", 10)
    URL_NORM = ("Segoe UI", 10)
    URL_HIGH = ("Segoe UI", 10, "underline")

    TXT_HEIGHT = 10

    BG_COLOR = "white"
    FG_COLOR = "black"

    URL_PENDING_COLOR = "gray"
    URL_HOVERED_COLOR = "blue"
    URL_APLLIED_COLOR = "purple"

    KIND_TAG = "Info"

    def __init__(self, connection: AbstractConnection):
        # key exchange
        self._sockname = connection.sockname
        self._peername = connection.peername
        self._key_exchanger = TwoWayKeyExchanger[
            ECC.EccKey | None,
            ECC.EccKey | None,
            bytes | None,
        ](
            generate_key,
            initial_sec=None,
            initial_pub=None,
        )
        self._send_key = self._key_exchanger.get_send_key()
        self._recv_key = self._key_exchanger.get_recv_key()

        # connection and threading setup
        def send_loop():
            while True:
                task = self._task_queue.get()
                if task is None:
                    break
                with suppress(Exception):
                    task()
            with suppress(Exception):
                self._sender.send_quit()

        self._task_queue = Queue[Callable[[], None] | None]()
        self._sender = connection.start(self)
        Thread(target=send_loop, daemon=True).start()

        # tkinter setup
        super().__init__()
        self._update_title()
        self.minsize(640, 480)
        frame_top = tk.Frame(self)
        frame_bot = tk.Frame(self)
        text = tk.Text(frame_top, font=self.TXT_FONT, bg=self.BG_COLOR, fg=self.FG_COLOR, height=self.TXT_HEIGHT)
        scrollbar = tk.Scrollbar(frame_top, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        text.tag_config(self.KIND_TAG, font=self.TAG_FONT)
        text.config(state=tk.DISABLED)
        b_keyx = tk.Button(frame_bot, font=self.BTN_FONT, text="Key Exchange", command=self.on_key_exchange_request)
        b_file = tk.Button(frame_bot, font=self.BTN_FONT, text="File", command=self.on_file)
        b_pics = tk.Button(frame_bot, font=self.BTN_FONT, text="Image", command=self.on_image)
        b_text = tk.Button(frame_bot, font=self.BTN_FONT, text="Enter", command=self.on_enter)
        entry = tk.Entry(frame_bot, font=self.TXT_FONT, bg=self.BG_COLOR, fg=self.FG_COLOR)
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

    def _update_send_key(self, send_key: bytes | None):
        self._send_key = send_key
        self._update_title()

    def _update_recv_key(self, recv_key: bytes | None):
        self._recv_key = recv_key
        self._update_title()

    def _update_title(self):
        send_status = "secured" if self._send_key is not None else "unsecured"
        recv_status = "secured" if self._recv_key is not None else "unsecured"
        self.title(f"Chat - {self._sockname} ({send_status}) <-> {self._peername} ({recv_status})")

    def _after_sent_sec(self, sec: ECC.EccKey | None):
        self._update_send_key(self._key_exchanger.after_sent_sec(sec))

    def _after_received_pub(self, pub: ECC.EccKey | None):
        self._update_recv_key(self._key_exchanger.after_received_pub(pub))

    def _after_sent_received_pub(self):
        self._update_send_key(self._key_exchanger.after_sent_received_pub())

    def _after_received_sent_sec(self):
        self._update_recv_key(self._key_exchanger.after_received_sent_sec())

    def _encrypt(self, data: bytes):
        if self._send_key:
            cipher = AES.new(self._send_key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            return cipher.nonce + tag + ciphertext
        return data

    def _decrypt(self, data: bytes):
        if self._recv_key:
            nonce = data[:16]
            tag = data[16:32]
            ciphertext = data[32:]
            cipher = AES.new(self._recv_key, AES.MODE_EAX, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        return data

    def _post(self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs):
        def handle():
            if not self.is_active:
                return
            func(*args, **kwargs)

        self.after(0, handle)

    def _create_stateful_label(self, state: S) -> tuple[tk.Label, S]:
        label = tk.Label(self.text, font=self.LBL_NORM, bg=self.BG_COLOR, fg=self.FG_COLOR, cursor="hand2", text=f"[{state.icon} {state.last_time:%Y-%m-%d %H:%M:%S}]")
        label.bind("<Enter>", lambda event, label=label: label.config(font=self.LBL_HIGH))
        label.bind("<Leave>", lambda event, label=label: label.config(font=self.LBL_NORM))

        def show_tooltip(event: tk.Event | None = None):
            messagebox.showinfo("Info", "\n".join(f"{k}: {v}" for k, v in state.info.items()))

        label.bind("<Button-1>", show_tooltip)
        return label, state

    def _update_stateful_label(self, tranform: Callable[[T], S], stateful_label: tuple[tk.Label, T]) -> tuple[tk.Label, S]:
        label, state = stateful_label
        state = tranform(state)
        label.config(text=f"[{state.icon} {state.last_time:%Y-%m-%d %H:%M:%S}]")

        def show_tooltip(event: tk.Event | None = None):
            messagebox.showinfo("Info", "\n".join(f"{k}: {v}" for k, v in state.info.items()))

        label.bind("<Button-1>", show_tooltip)
        return label, state

    def _show_key_exchange_request_message(self, stateful_label: tuple[tk.Label, State], sec: ECC.EccKey | None):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        spec = "on" if sec is not None else "off"
        self.text.insert(tk.END, f"Key exchange request ({spec})", self.KIND_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def _show_key_exchange_request_replyable(self, stateful_label: tuple[tk.Label, State], pub: ECC.EccKey | None):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        spec = "on" if pub is not None else "off"
        self.text.insert(tk.END, f"Key exchange request ({spec}): ", self.KIND_TAG)
        link = tk.Label(self.text, font=self.URL_NORM, bg=self.BG_COLOR, fg=self.URL_PENDING_COLOR, cursor="arrow", text="[pending]")
        register = NextEnableRegister()

        def accept(event: tk.Event | None = None):
            self.on_key_exchange_response(event)
            link.config(font=self.URL_NORM, bg=self.BG_COLOR, fg=self.URL_APLLIED_COLOR, cursor="arrow", text="[accepted]")
            link.unbind("<Enter>")
            link.unbind("<Leave>")
            link.unbind("<Button-1>")
            if register.next_enable is not None:
                register.next_enable()
            else:
                self.last_register = None

        def enable():
            link.config(font=self.URL_NORM, bg=self.BG_COLOR, fg=self.URL_HOVERED_COLOR, cursor="hand2", text="[accept]")
            link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_HIGH))
            link.bind("<Leave>", lambda event, link=link: link.config(font=self.URL_NORM))
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

    def _show_key_exchange_response_message(self, stateful_label: tuple[tk.Label, State]):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Key exchange response", self.KIND_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def _show_text_message(self, stateful_label: tuple[tk.Label, State], text: str):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Message: ", self.KIND_TAG)
        self.text.insert(tk.END, "\n")
        self.text.insert(tk.END, text)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def _show_image_message(self, stateful_label: tuple[tk.Label, State], data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Image: ", self.KIND_TAG)
        try:
            image = Image.open(BytesIO(data))
            imgtk = ImageTk.PhotoImage(image)
            self.imgtk_storage.append(imgtk)
        except Exception:
            link = tk.Label(self.text, font=self.URL_NORM, bg=self.BG_COLOR, fg=self.URL_HOVERED_COLOR, cursor="hand2", text="[corrupted image]")
            link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_HIGH))
            link.bind("<Leave>", lambda event, link=link: link.config(font=self.URL_NORM))

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

    def _show_file_message(self, stateful_label: tuple[tk.Label, State], name: str, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "File: ", self.KIND_TAG)
        link = tk.Label(self.text, font=self.URL_NORM, bg=self.BG_COLOR, fg=self.URL_HOVERED_COLOR, cursor="hand2", text=name)
        link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_HIGH))
        link.bind("<Leave>", lambda event, link=link: link.config(font=self.URL_NORM))

        def save(event: tk.Event | None = None):
            path = filedialog.asksaveasfilename(initialfile=name)
            if path:
                open(path, "wb").write(data)

        link.bind("<Button-1>", save)
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def _show_corrupted_message(self, stateful_label: tuple[tk.Label, State]):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Corrupted message", self.KIND_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def _show_empty_message(self, stateful_label: tuple[tk.Label, State]):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Empty message", self.KIND_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def _show_unknown_message(self, stateful_label: tuple[tk.Label, State], tag: int, data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Unknown message: ", self.KIND_TAG)
        link = tk.Label(self.text, font=self.URL_NORM, bg=self.BG_COLOR, fg=self.URL_HOVERED_COLOR, cursor="hand2", text=f"[tag = {tag}]")
        link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_HIGH))
        link.bind("<Leave>", lambda event, link=link: link.config(font=self.URL_NORM))

        def save(event: tk.Event | None = None):
            path = filedialog.asksaveasfilename(initialfile="unknown.bin")
            if path:
                open(path, "wb").write(data)

        link.bind("<Button-1>", save)
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def _show_undeserialized_message(self, stateful_label: tuple[tk.Label, State], cls: type[DeserializableMessage], data: bytes):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Undeserializable message: ", self.KIND_TAG)
        link = tk.Label(self.text, font=self.URL_NORM, bg=self.BG_COLOR, fg=self.URL_HOVERED_COLOR, cursor="hand2", text=f"[class = {cls.__name__}]")
        link.bind("<Enter>", lambda event, link=link: link.config(font=self.URL_HIGH))
        link.bind("<Leave>", lambda event, link=link: link.config(font=self.URL_NORM))

        def save(event: tk.Event | None = None):
            path = filedialog.asksaveasfilename(initialfile="unknown.bin")
            if path:
                open(path, "wb").write(data)

        link.bind("<Button-1>", save)
        self.text.window_create(tk.END, window=link)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def _show_quit_message(self, stateful_label: tuple[tk.Label, State]):
        self.text.config(state=tk.NORMAL)
        self.text.window_create(tk.END, window=stateful_label[0])
        self.text.insert(tk.END, " ")
        self.text.insert(tk.END, "Connection closed", self.KIND_TAG)
        self.text.insert(tk.END, "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)

    def process(self, data: bytes):
        try:
            data = self._decrypt(data)
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

    def on_quit(self, event: tk.Event | None = None):
        self.is_active = False
        self._task_queue.put(None)

    def on_key_exchange_request(self, event: tk.Event | None = None):
        try:
            sec = ECC.generate(curve="P-224")
            pub = sec.public_key()
            msg = KeyExchangeRequestMessage(pub)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
            return

        def task():
            sending_stateful_label = self._update_stateful_label(lambda pending_state: SendingState(pending_state, self._send_key), pending_stateful_label)
            try:
                self._sender.send(self._encrypt(bytes([msg.tag]) + msg.serialize()))
                self._after_sent_sec(sec)
            except Exception:
                self._update_stateful_label(lambda sending_state: SentFailureState(sending_state), sending_stateful_label)
            else:
                self._update_stateful_label(lambda sending_state: SentSuccessState(sending_state), sending_stateful_label)

        pending_stateful_label = self._create_stateful_label(PendingState())
        self._task_queue.put(task)
        self._show_key_exchange_request_message(pending_stateful_label, sec)

    def on_key_exchange_response(self, event: tk.Event | None = None):
        try:
            msg = KeyExchangeResponseMessage()
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
            return

        def task():
            sending_stateful_label = self._update_stateful_label(lambda pending_state: SendingState(pending_state, self._send_key), pending_stateful_label)
            try:
                self._sender.send(self._encrypt(bytes([msg.tag]) + msg.serialize()))
                self._after_sent_received_pub()
            except Exception:
                self._update_stateful_label(lambda sending_state: SentFailureState(sending_state), sending_stateful_label)
            else:
                self._update_stateful_label(lambda sending_state: SentSuccessState(sending_state), sending_stateful_label)

        pending_stateful_label = self._create_stateful_label(PendingState())
        self._task_queue.put(task)
        self._show_key_exchange_response_message(pending_stateful_label)

    def on_enter(self, event: tk.Event | None = None):
        try:
            text = self.entry.get()
            self.entry.delete(0, tk.END)
            msg = TextMessage(text)
        except Exception as e:
            messagebox.showerror(e.__class__.__name__, str(e))
            return

        def task():
            sending_stateful_label = self._update_stateful_label(lambda pending_state: SendingState(pending_state, self._send_key), pending_stateful_label)
            try:
                self._sender.send(self._encrypt(bytes([msg.tag]) + msg.serialize()))
            except Exception:
                self._update_stateful_label(lambda sending_state: SentFailureState(sending_state), sending_stateful_label)
            else:
                self._update_stateful_label(lambda sending_state: SentSuccessState(sending_state), sending_stateful_label)

        pending_stateful_label = self._create_stateful_label(PendingState())
        self._task_queue.put(task)
        self._show_text_message(pending_stateful_label, text)

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
            sending_stateful_label = self._update_stateful_label(lambda pending_state: SendingState(pending_state, self._send_key), pending_stateful_label)
            try:
                self._sender.send(self._encrypt(bytes([msg.tag]) + msg.serialize()))
            except Exception:
                self._update_stateful_label(lambda sending_state: SentFailureState(sending_state), sending_stateful_label)
            else:
                self._update_stateful_label(lambda sending_state: SentSuccessState(sending_state), sending_stateful_label)

        pending_stateful_label = self._create_stateful_label(PendingState())
        self._task_queue.put(task)
        self._show_image_message(pending_stateful_label, data)

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
            sending_stateful_label = self._update_stateful_label(lambda pending_state: SendingState(pending_state, self._send_key), pending_stateful_label)
            try:
                self._sender.send(self._encrypt(bytes([msg.tag]) + msg.serialize()))
            except Exception:
                self._update_stateful_label(lambda sending_state: SentFailureState(sending_state), sending_stateful_label)
            else:
                self._update_stateful_label(lambda sending_state: SentSuccessState(sending_state), sending_stateful_label)

        pending_stateful_label = self._create_stateful_label(PendingState())
        self._task_queue.put(task)
        self._show_file_message(pending_stateful_label, name, data)

    def after_quit_received(self):
        received_stateful_label = self._create_stateful_label(QuitState())
        self._post(self._show_quit_message, received_stateful_label)

    def after_corrupted_received(self):
        received_stateful_label = self._create_stateful_label(CorruptedState())
        self._post(self._show_corrupted_message, received_stateful_label)

    def after_empty_received(self):
        received_stateful_label = self._create_stateful_label(ReceivedState(self._recv_key))
        self._post(self._show_empty_message, received_stateful_label)

    def after_unknown_received(self, tag: int, data: bytes):
        received_stateful_label = self._create_stateful_label(ReceivedState(self._recv_key))
        self._post(self._show_unknown_message, received_stateful_label, tag, data)

    def after_undeserialized_received(self, cls: type[DeserializableMessage], data: bytes):
        received_stateful_label = self._create_stateful_label(ReceivedState(self._recv_key))
        self._post(self._show_undeserialized_message, received_stateful_label, cls, data)

    def after_key_exchange_request_received(self, pub: ECC.EccKey | None):
        received_stateful_label = self._create_stateful_label(ReceivedState(self._recv_key))
        self._post(self._show_key_exchange_request_replyable, received_stateful_label, pub)
        self._after_received_pub(pub)

    def after_key_exchange_response_received(self):
        received_stateful_label = self._create_stateful_label(ReceivedState(self._recv_key))
        self._post(self._show_key_exchange_response_message, received_stateful_label)
        self._after_received_sent_sec()

    def after_text_received(self, text: str):
        received_stateful_label = self._create_stateful_label(ReceivedState(self._recv_key))
        self._post(self._show_text_message, received_stateful_label, text)

    def after_image_received(self, data: bytes):
        received_stateful_label = self._create_stateful_label(ReceivedState(self._recv_key))
        self._post(self._show_image_message, received_stateful_label, data)

    def after_file_received(self, name: str, data: bytes):
        received_stateful_label = self._create_stateful_label(ReceivedState(self._recv_key))
        self._post(self._show_file_message, received_stateful_label, name, data)
