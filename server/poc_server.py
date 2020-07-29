#!/bin/usr/python3


import socket
import threading
from typing import Tuple


class ClientThread(threading.Thread):
    """
    Class used to dispatch threads that handles client connections.

    Attributes:
        self.client_socket (socket): The socket used to connect to client.
    """
    def __init__(self, client_socket: socket.socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
    
    def run(self):
        self._handle_client_connection()
    
    def _handle_client_connection(self) -> None:
        """Handles the connection with the client socket."""
        with self.client_socket as s:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                print(data)


def open_server_connection(address: Tuple[str, int]):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(address)
        server_socket.listen()
        
        while True:
            client_socket, client_addr = server_socket.accept()
            print("Connected to {}:{}".format(client_addr[0], client_addr[1]))
            client_thread = ClientThread(client_socket)
            client_thread.run()


def main():
    hostname = socket.gethostname()
    port_number = 7896
    address = (hostname, port_number)
    open_server_connection(address)


if __name__ == "__main__":
    main()
