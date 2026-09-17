import argparse
import socket
import sys
import re

import struct

from _thread import start_new_thread

def input_args_handler() -> tuple:
    # Input Argument Handling
    parser = argparse.ArgumentParser(
        description="Simple TCP Messaging Client (1024 Bytes)."
    )
    parser.add_argument(
        "-i", "--hostname", "--ip",
        help="Hostname of the server to connect to.",
        default="127.0.0.1"
    )
    parser.add_argument(
        "-p", "--port",
        help="Port to connect to the server.",
        default=None
    )
    parser.add_argument(
        "-s", "--source",
        help="Source port to use in the client",
        default=None
    )
    args = parser.parse_args()
    
    port = args.port
    source_port = args.source

    if not port:
        sys.exit("Missing port number input.")

    try:
        port = int(port)
        if port < 1 or port > 65535:
            raise ValueError
        
        source_port = int(source_port)
        if source_port < 1 or source_port > 65535:
            raise ValueError

    except ValueError:
        sys.exit("Invalid port. Please input proper port number.")
    
    host = args.hostname
    try:
        pattern = re.compile(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
        pattern2 = re.compile(r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
        if not pattern.match(host) or not pattern2.match(host):
            raise ValueError
    except ValueError:
        sys.exit("Invalid hostname. Please input valid hostname or IP address.")

    return host, port, source_port
    
def init_socket(port: int, host: str = "127.0.0.1", source_port: int = 9000):
    """Initializes the socket program.

    Args:
        host (str, optional): Hostname / IP Address. Defaults to "127.0.0.1".
        port (int): Port Number.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(("0.0.0.0", source_port))
    
    try:
        message = input("Message to send: ")
        length = 264
        checksum = 1
        data = struct.pack(">HHHH256s", source_port, port, length, checksum, message.encode())
        
        client_socket.sendto(data, (host, port))
        
        # wait for reply
        msg = client_socket.recv(1024)
        print(msg.decode())
    except Exception as e:
        print(e)
        sys.exit("Message failed to send or no reply. Terminating...")

def main():
    hostname, port, source = input_args_handler()
    init_socket(host=hostname, port=port, source_port=source)
    sys.exit(0)

if __name__ == "__main__":
    main()