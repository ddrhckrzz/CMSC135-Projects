import argparse
import socket
import sys

from _thread import start_new_thread
import threading

DEFAULT_PORT = 5757
MAX_CLIENTS = 20

print_lock = threading.Lock
active_clients = {}

def input_args_handler() -> int:
    # Input Argument Handling
    parser = argparse.ArgumentParser(
        description="Simple TCP Message Server (1024 Bytes)."
    )
    parser.add_argument(
        "port", "-p", "--port",
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

def init_socket(host: str = "127.0.0.1", port: int = DEFAULT_PORT):
    """Initializes the socket program.

    Args:
        host (str, optional): Hostname / IP Address. Defaults to "127.0.0.1".
        port (int, optional): Port Number. Defaults to DEFAULT_PORT.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(host, port)
    server_socket.listen(MAX_CLIENTS) # only accept up to MAX_CLIENTS amount of connections
    
    print(f"[system]: Server accepting connections on host {host} and port {port}.")
    server_loop(server_socket)
    
def server_loop(sock: socket.socket):
    while True:
        client_socket, _ = sock.accept()
        name = sock.recv(1024).decode(encoding="utf-8")
        start_new_thread(client_handler, (client_socket, name,))

def client_handler(sock: socket.socket, name: str):
    msg = f"[system]: {name} joined the chat."
    active_clients[name] = sock
    broadcast(msg)
    while True:
        message = sock.recv(1024)
        if not message:
            # something about them leaving, send it to everyone too
            msg = f"[system]: {name} left the chat."
            active_clients.pop(name)
            broadcast(msg)
            break
        message = f"{name}: {message}"
        broadcast(message=message)
    sock.close()

def broadcast(message:str):
    with print_lock:
        print(message) # print to console first
        for client in active_clients.keys():
            client.send(message.encode(encoding="utf-8"))

# def safe_print(*args, **kwargs):
#     with print_lock:
#         print(*args, **kwargs)

def main():
    port = input_args_handler()
    init_socket(port=port)
    sys.exit(0)

if __name__ == "__main__":
    main()