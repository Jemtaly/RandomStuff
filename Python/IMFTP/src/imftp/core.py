from abc import ABC, abstractmethod


class AbstractDataSender(ABC):
    @abstractmethod
    def send(self, data: bytes): ...

    @abstractmethod
    def send_quit(self): ...


class AbstractDataReceiver(ABC):
    @abstractmethod
    def process(self, data: bytes): ...

    @abstractmethod
    def process_quit(self): ...


class AbstractConnection(ABC):
    @property
    @abstractmethod
    def descriptor(self) -> str: ...

    @abstractmethod
    def start(self, receiver: AbstractDataReceiver) -> AbstractDataSender: ...
