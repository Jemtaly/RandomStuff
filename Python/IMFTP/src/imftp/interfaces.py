from abc import ABC, abstractmethod


class AbstractMessagerBackend(ABC):
    @property
    @abstractmethod
    def descriptor(self) -> str: ...

    @abstractmethod
    def send(self, data: bytes): ...

    @abstractmethod
    def send_quit(self): ...


class AbstractMessagerFrontend(ABC):
    @abstractmethod
    def process(self, data: bytes): ...

    @abstractmethod
    def process_quit(self): ...


class AbstractMessagerBackendFactory(ABC):
    @abstractmethod
    def create(self, frontend: AbstractMessagerFrontend) -> AbstractMessagerBackend: ...
