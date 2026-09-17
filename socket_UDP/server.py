import argparse
import socket
import sys

import struct

from _thread import start_new_thread
import threading

DEFAULT_PORT = 5757

clients_lock = threading.Lock()

def input_args_handler() -> int:
    # Input Argument Handling
    parser = argparse.ArgumentParser(
        description="Simple TCP Message Server (1024 Bytes)."
    )
    parser.add_argument(
        "-p", "--port",
        help="Port to serve incoming connections.",
        default=DEFAULT_PORT
    )
    args = parser.parse_args()
    
    port = args.port
    
    # error handling
    try:
        port = int(port)
        if port < 1 or port > 65535:
            raise ValueError
    except ValueError:
        sys.exit("Invalid input. Please input proper port number.")
    
    return port

def init_socket( port: int = DEFAULT_PORT, host: str = "127.0.0.1"):
    """Initializes the socket program.

    Args:
        host (str, optional): Hostname / IP Address. Defaults to "127.0.0.1".
        port (int, optional): Port Number. Defaults to DEFAULT_PORT.
    """
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((host, port))
        
        print(f"Server listening at {host}:{port}")

        listener(server_socket)
    except OSError as e:
        print(f"OS Error: {e}")
    except KeyboardInterrupt:
        print(f"Keyboard Interrupt detected. Closing...")
    
    close_all(server_socket)
    
def listener(sock: socket.socket):
    while True:
        data, addr = sock.recvfrom(1024)
        
        # segmentize the data
        source_port, dest_port, length, checksum, payload = struct.unpack(">HHHH256s", data)
        message = payload.decode()
        
        # check checksum idk
        
        # reply
        reply = f"ACK|{message}"
        sock.sendto(reply.encode(), addr)
        
        print(f"[received from host src ={addr}:{source_port}]")
        print(f"[udp header src={source_port} dst={dest_port} len={length} checksum={checksum}]")
        print(f"[demultiplexing dst={dest_port} socket=server]")
        print(f"[checksum valid]")
        print(f"[message] {message}")

# def client_handler(sock: socket.socket, name: str):
#     msg = f"[system]: {name} joined the chat."
#     with clients_lock:
#         active_clients[name] = sock
#     broadcast(msg)
#     while True:
#         message = sock.recv(1024)
#         if not message:
#             # something about them leaving, send it to everyone too
#             msg = f"[system]: {name} left the chat."
#             with clients_lock:
#                 active_clients.pop(name)
#             broadcast(msg)
#             break
#         message = f"{name}: {message.decode(encoding="utf-8")}"
#         broadcast(message=message)
#     sock.close()

# def broadcast(message:str):
#     with clients_lock:
#         print(message) # print to console first
#         for client in active_clients.values():
#             client.send(message.encode(encoding="utf-8"))

def close_all(sock: socket.socket):
    # for client in active_clients.values():
    #     msg = f"[system] Server shutting down..."
    #     client.send(msg.encode(encoding="utf-8"))
    #     client.send(''.encode(encoding="utf-8"))
    #     client.close()
    sock.close()
    sys.exit("Shutting down...")

def main():
    port = input_args_handler()
    init_socket(port)


if __name__ == "__main__":
    main()