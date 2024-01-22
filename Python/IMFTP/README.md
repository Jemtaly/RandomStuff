# IMFTP

A file transfer tool and an instant messager, supporting Diffie-Hellman Key Exchange Protocol and AES-CTR encryption.

## Requirements

- Python 3.6+
- PyCryptodome

## Usage

```
usage: imftp.py [-h] [--server [IP] | --client IP] [--port PORT]
                (--send [FILENAME] | --recv [FILENAME] | --talk) [--size SIZE] [--enc]

Instant Messager and File Transfer

options:
  -h, --help         show this help message and exit
  --server [IP]      run as a server (default)
  --client IP        run as a client (server IP required)
  --port PORT        port number of the server (4096 by default)
  --send [FILENAME]  send file
  --recv [FILENAME]  receive file
  --talk             instant messager
  --size SIZE        set size limit (unlimited by default, ignored in the instant messager mode)
  --enc              encrypt the connection with DHKE and AES-CTR (cannot be set on one side only)
```

## Example

### File Transfer

```shell
# Server
$ python3 imftp.py --server --send server_test.txt --size 1024 --enc

# Client
$ python3 imftp.py --client $SERVER_IP --recv client_test.txt --enc
```

Send the first 1024 bytes of `server_test.txt` from the server to the client and save it as `client_test.txt`, encrypting the connection with DHKE and AES-CTR.

### Instant Messager

```shell
# Server
$ python3 imftp.py --server --talk --enc

# Client
$ python3 imftp.py --client $SERVER_IP --talk --enc
```

Start an instant messager between the server and the client, encrypting the connection with DHKE and AES-CTR.
