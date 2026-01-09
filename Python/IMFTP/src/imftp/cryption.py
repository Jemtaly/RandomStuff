from collections import deque
from typing import Callable, TypeVar, Generic


Sec = TypeVar("Sec")
Pub = TypeVar("Pub")
Key = TypeVar("Key")


GenerateKey = Callable[[Sec, Pub], Key]


class OneWayKeyExchanger(Generic[Sec, Pub, Key]):
    def __init__(
        self,
        generate_key: GenerateKey[Sec, Pub, Key],
        *,
        initial_sec: Sec,
        initial_pub: Pub,
    ):
        self._sec = initial_sec
        self._pub = initial_pub
        self._generate_key = generate_key

    def after_sent_sec(self, sec: Sec) -> Key:
        """Call this method after sending your secret component.

        :param sec: Your secret component that you just sent.
        :return: The updated shared key.
        """
        self._sec = sec
        return self.get_key()

    def after_received_pub(self, pub: Pub) -> Key:
        """Call this method after receiving the peer's public component.

        :param pub: The peer's public component that you just received.
        :return: The updated shared key.
        """
        self._pub = pub
        return self.get_key()

    def get_key(self) -> Key:
        """Get the current shared key.

        :return: The current shared key.
        """
        return self._generate_key(self._sec, self._pub)


class TwoWayKeyExchanger(Generic[Sec, Pub, Key]):
    def __init__(
        self,
        generate_key: GenerateKey[Sec, Pub, Key],
        *,
        initial_sec: Sec,
        initial_pub: Pub,
    ):
        self._sec_queue: deque[Sec] = deque([initial_sec])
        self._pub_queue: deque[Pub] = deque([initial_pub])
        self._generate_key = generate_key

    def after_sent_sec(self, sec: Sec) -> Key:
        """Call this method after sending your secret component.

        :param sec: Your secret component that you just sent.
        :return: The updated shared key for sending.
        """
        self._sec_queue.append(sec)
        return self.get_send_key()

    def after_received_pub(self, pub: Pub) -> Key:
        """Call this method after receiving the peer's public component.

        :param pub: The peer's public component that you just received.
        :return: The updated shared key for receiving.
        """
        self._pub_queue.append(pub)
        return self.get_recv_key()

    def after_sent_received_pub(self) -> Key:
        """Call this method after sending the arrival of your public component.

        :return: The updated shared key for sending.
        """
        self._pub_queue.popleft()
        return self.get_send_key()

    def after_received_sent_sec(self) -> Key:
        """Call this method after receiving the arrival of your secret component.

        :return: The updated shared key for receiving.
        """
        self._sec_queue.popleft()
        return self.get_recv_key()

    def get_send_key(self) -> Key:
        """Get the current shared key for sending.

        :return: The current shared key for sending.
        """
        return self._generate_key(self._sec_queue[-1], self._pub_queue[0])

    def get_recv_key(self) -> Key:
        """Get the current shared key for receiving.

        :return: The current shared key for receiving.
        """
        return self._generate_key(self._sec_queue[0], self._pub_queue[-1])
