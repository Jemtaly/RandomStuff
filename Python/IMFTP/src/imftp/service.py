import socket
import threading

from .core import AbstractDataReceiver, AbstractDataSender, AbstractConnection


class Connection(AbstractConnection):
    def __init__(self, client: socket.socket, mode: str):
        self.client = client
        self.mode = mode

    @property
    def descriptor(self) -> str:
        sock_host, sock_port = self.client.getpeername()
        peer_host, peer_port = self.client.getsockname()
        return f"{sock_host}:{sock_port} <-> {peer_host}:{peer_port} ({self.mode})"

    def sendall(self, data: bytes):
        self.client.sendall(data)

    def recvall(self, size: int) -> bytes:
        return self.client.recv(size, socket.MSG_WAITALL)

    def start(self, receiver: AbstractDataReceiver) -> AbstractDataSender:
        self.sendall(b"CHAT")  # Handshake
        if self.recvall(4) != b"CHAT":
            raise ConnectionError("Handshake failed")

        connection = self

        def recv_loop():
            while True:
                try:
                    head = connection.recvall(4)
                    size = int.from_bytes(head, "big")
                    data = connection.recvall(size)
                    receiver.process(data)
                except Exception as e:
                    receiver.process_quit()
                    return

        threading.Thread(target=recv_loop, daemon=True).start()

        class DataSender(AbstractDataSender):
            def send(self, data: bytes):
                if len(data) >= 1 << 4 * 8:
                    raise OverflowError("data too large")
                size = len(data)
                head = size.to_bytes(4, "big")
                connection.sendall(head)
                connection.sendall(data)

            def send_quit(self):
                connection.client.close()

        return DataSender()


def establish_client_connection(host: str, port: int) -> AbstractConnection:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    return Connection(client, "client")


def establish_server_connection(host: str, port: int) -> AbstractConnection:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    client, _ = server.accept()
    server.close()
    return Connection(client, "server")
