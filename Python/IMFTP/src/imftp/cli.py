#!/usr/bin/env python3

from argparse import ArgumentParser

from .backend import ClientMessagerBackendFactory, ServerMessagerBackendFactory
from .frontend import MessagerFrontend

def main():
    parser = ArgumentParser(description="A simple chat application.")
    mode = parser.add_subparsers(dest="mode", required=True)

    server = mode.add_parser("server", help="Run as server.")
    server.add_argument("host", help="Host to bind.")
    server.add_argument("--port", type=int, default=12345, help="Port to bind.")

    client = mode.add_parser("client", help="Run as client.")
    client.add_argument("host", help="Server host to connect.")
    client.add_argument("--port", type=int, default=12345, help="Server port to connect.")

    args = parser.parse_args()

    match args.mode:
        case "server":
            factory = ServerMessagerBackendFactory(args.host, args.port)
        case "client":
            factory = ClientMessagerBackendFactory(args.host, args.port)

    app = MessagerFrontend(factory)
    app.mainloop()


if __name__ == "__main__":
    main()
