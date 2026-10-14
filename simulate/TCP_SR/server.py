import argparse
import socket
import sys

from _thread import start_new_thread
import threading

DEFAULT_PORT = 5757
MAX_CLIENTS = 20

clients_lock = threading.Lock()
active_clients = {}

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
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(MAX_CLIENTS) # only accept up to MAX_CLIENTS amount of connections
        
        print(f"[system]: Server accepting connections on host {host} and port {port}.")

        server_loop(server_socket)
    except OSError as e:
        print(f"OS Error: {e}")
    except KeyboardInterrupt:
        print(f"Keyboard Interrupt detected. Closing...")
    
    close_all(server_socket)
    
def server_loop(sock: socket.socket):
    while True:
        client_socket, addr = sock.accept()
        name = client_socket.recv(1024).decode(encoding="utf-8")
        if name in active_clients.keys():
            msg = f"[system] Username \'{name}\' has already been taken. This request has been noted and sent to the admin."
            client_socket.send(msg.encode(encoding="utf-8"))
            print(f"[system] {addr} tried to connect with duplicate username of {name}.")
            client_socket.close()
            continue
        start_new_thread(client_handler, (client_socket, name,))

def client_handler(sock: socket.socket, name: str):
    msg = f"[system]: {name} joined the chat."
    with clients_lock:
        active_clients[name] = sock
    broadcast(msg)
    while True:
        message = sock.recv(1024)
        if not message:
            # something about them leaving, send it to everyone too
            msg = f"[system]: {name} left the chat."
            with clients_lock:
                active_clients.pop(name)
            broadcast(msg)
            break
        message = f"{name}: {message.decode(encoding="utf-8")}"
        broadcast(message=message)
    sock.close()

def broadcast(message:str):
    with clients_lock:
        print(message) # print to console first
        for client in active_clients.values():
            client.send(message.encode(encoding="utf-8"))

def close_all(sock: socket.socket):
    for client in active_clients.values():
        msg = f"[system] Server shutting down..."
        client.send(msg.encode(encoding="utf-8"))
        client.send(''.encode(encoding="utf-8"))
        client.close()
    sock.close()
    sys.exit("Shutting down...")

def main():
    port = input_args_handler()
    init_socket(port)


if __name__ == "__main__":
    main()