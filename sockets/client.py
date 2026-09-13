import argparse
import socket
import sys
import re

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
        "port", "-p", "--port",
        help="Port to connect to the server.",
        default=None
    )
    args = parser.parse_args()
    
    port = args.port

    if not port:
        sys.exit("Missing port number input.")

    try:
        port = int(port)
        if port < 1 or port > 65535:
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

    return host, port
    
def init_socket(port: int, host: str = "127.0.0.1"):
    """Initializes the socket program.

    Args:
        host (str, optional): Hostname / IP Address. Defaults to "127.0.0.1".
        port (int): Port Number.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(host, port)
        # Enter client loop
        client_loop(client_socket)
    except TimeoutError:
        sys.exit("Connection timed out. Terminating...")
    except InterruptedError:
        sys.exit("Connection interrupted. Terminating...")
    except:
        sys.exit("Connection error. Terminating...")

def listen_for_msg(sock: socket.socket):
    while True:
        msg = sock.recv(1024)
        
        # check if no message received: aka disconnected
        if not msg:
            sys.exit("Client disconnected from server. Exiting...")

        # Source - https://stackoverflow.com/a/71087379
        # Posted by Carson Thompson, modified by community. See post 'Timeline' for change history
        # Retrieved 2026-09-13, License - CC BY-SA 4.0
        print("\u001B[s", end="")     # Save current cursor position
        print("\u001B[A", end="")     # Move cursor up one line
        print("\u001B[999D", end="")  # Move cursor to beginning of line
        print("\u001B[S", end="")     # Scroll up/pan window down 1 line
        print("\u001B[L", end="")     # Insert new line
        print(msg.decode(encoding="utf-8"), end="")     # Print msg
        print("\u001B[u", end="")     # Jump back to saved cursor position


def client_loop(sock: socket.socket):
    name = input("Enter username: ")
    # TODO: Add error handling
    # Send username to server
    sock.send(name.encode(encoding="utf-8"))
    
    # start listener as thread
    start_new_thread(listen_for_msg, (sock,))
    
    message = input("Chat: ")
    while(message != "/quit"):
        pattern = re.compile(r"\/.*") # don't send anything that starts with a slash.
        if pattern.match(message):
            print("[CLIENT_ERR] Invalid command. Type /quit to quit the program.")
        sock.send(message.encode(encoding="utf-8"))
        message = input("Chat: ")
    
    print("Disconnecting from server...")
    sock.close()
    print("Quitting program...")

def main():
    hostname, port = input_args_handler()
    init_socket(host=hostname, port=port)
    sys.exit(0)

if __name__ == "__main__":
    main()