import socket
import threading

from .interfaces import AbstractMessagerFrontend, AbstractMessagerBackend, AbstractMessagerBackendFactory


class MessagerBackend(AbstractMessagerBackend):
    def __init__(self, frontend: AbstractMessagerFrontend, client: socket.socket, mode: str):
        self.frontend = frontend
        self.client = client
        self.mode = mode
        self.sendall(b"CHAT")
        assert self.recvall(4) == b"CHAT", "peer is not in chat mode"
        threading.Thread(target=self.recv_loop, daemon=True).start()

    @property
    def descriptor(self) -> str:
        sock_host, sock_port = self.client.getpeername()
        peer_host, peer_port = self.client.getsockname()
        return f"{sock_host}:{sock_port} <-> {peer_host}:{peer_port} ({self.mode})"

    def sendall(self, data: bytes):
        self.client.sendall(data)

    def recvall(self, size: int) -> bytes:
        return self.client.recv(size, socket.MSG_WAITALL)

    def send(self, data: bytes):
        if len(data) >= 1 << 4 * 8:
            raise OverflowError("data too large")
        size = len(data)
        head = size.to_bytes(4, "big")
        self.sendall(head)
        self.sendall(data)

    def send_quit(self):
        self.client.close()

    def recv_loop(self):
        while True:
            try:
                head = self.recvall(4)
                size = int.from_bytes(head, "big")
                data = self.recvall(size)
                self.frontend.process(data)
            except Exception as e:
                self.frontend.process_quit()
                return


class ServerMessagerBackendFactory(AbstractMessagerBackendFactory):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def create(self, frontend: AbstractMessagerFrontend) -> MessagerBackend:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(1)
        client, _ = server.accept()
        server.close()
        return MessagerBackend(frontend, client, "server")


class ClientMessagerBackendFactory(AbstractMessagerBackendFactory):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def create(self, frontend: AbstractMessagerFrontend) -> MessagerBackend:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, self.port))
        return MessagerBackend(frontend, client, "client")
