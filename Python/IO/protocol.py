from .pipe import Readable, Writable


def sendstream(
    base_writable: Writable,
    temp_readable: Readable,
    dlen: int = 0x1000,
):
    hlen = (dlen.bit_length() + 7) // 8
    flen = dlen + hlen

    while True:
        data = temp_readable.read(dlen)
        size = len(data)
        head = size.to_bytes(hlen, "big")
        full = head + data
        base_writable.write(full)
        if size < dlen:
            break


def recvstream(
    base_readable: Readable,
    temp_writable: Writable,
    dlen: int = 0x1000,
):
    hlen = (dlen.bit_length() + 7) // 8
    flen = dlen + hlen

    head = base_readable.read(hlen)
    size = int.from_bytes(head, "big")
    while size == dlen:
        full = base_readable.read(flen)
        data = full[:dlen]
        head = full[dlen:]
        temp_writable.write(data)
        size = int.from_bytes(head, "big")
    data = base_readable.read(size)
    temp_writable.write(data)
