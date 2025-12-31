from collections import deque

from Crypto.Hash import SHA224
from Crypto.Protocol import DH
from Crypto.PublicKey import ECC


def generate_key(
    sock_sec_key: ECC.EccKey | None,
    peer_pub_key: ECC.EccKey | None,
) -> bytes | None:
    if sock_sec_key is None or peer_pub_key is None:
        return None
    return DH.key_agreement(
        static_priv=sock_sec_key,
        static_pub=peer_pub_key,
        kdf=lambda x: SHA224.new(x).digest(),
    )


class OneWayKeyExchanger:
    def __init__(self):
        self.sock_sec_key: ECC.EccKey | None = None
        self.peer_pub_key: ECC.EccKey | None = None

    def set_sock_sec_key(self, sock_sec_key: ECC.EccKey | None):
        self.sock_sec_key = sock_sec_key

    def got_peer_pub_key(self, peer_pub_key: ECC.EccKey | None):
        self.peer_pub_key = peer_pub_key

    def get_key(self) -> bytes | None:
        return generate_key(
            sock_sec_key=self.sock_sec_key,
            peer_pub_key=self.peer_pub_key,
        )


class TwoWayKeyExchanger:
    def __init__(self):
        self.peer_pub_key: ECC.EccKey | None = None
        self.sock_sec_key_queue: deque[ECC.EccKey | None] = deque([None])

    def set_sock_sec_key(self, sock_sec_key: ECC.EccKey | None):
        self.sock_sec_key_queue.append(sock_sec_key)

    def got_peer_pub_key(self, peer_pub_key: ECC.EccKey | None):
        self.peer_pub_key = peer_pub_key

    def confirm_sock_sec_key(self):
        self.sock_sec_key_queue.popleft()

    def get_send_key(self) -> bytes | None:
        return generate_key(
            sock_sec_key=self.sock_sec_key_queue[-1],
            peer_pub_key=self.peer_pub_key,
        )

    def get_recv_key(self) -> bytes | None:
        return generate_key(
            sock_sec_key=self.sock_sec_key_queue[0],
            peer_pub_key=self.peer_pub_key,
        )


class AsymKeyExchanger:
    def __init__(self):
        self.send_exchanger = OneWayKeyExchanger()
        self.recv_exchanger = OneWayKeyExchanger()

    def set_sock_sec_send_key(self, ecc_key: ECC.EccKey | None):
        self.send_exchanger.set_sock_sec_key(ecc_key)

    def set_sock_sec_recv_key(self, ecc_key: ECC.EccKey | None):
        self.recv_exchanger.set_sock_sec_key(ecc_key)

    def got_peer_pub_send_key(self, ecc_key: ECC.EccKey | None):
        self.send_exchanger.got_peer_pub_key(ecc_key)

    def got_peer_pub_recv_key(self, ecc_key: ECC.EccKey | None):
        self.recv_exchanger.got_peer_pub_key(ecc_key)

    def get_send_key(self) -> bytes | None:
        return self.send_exchanger.get_key()

    def get_recv_key(self) -> bytes | None:
        return self.recv_exchanger.get_key()
