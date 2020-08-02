#!/bin/usr/python3


import socket
from typing import Tuple
from server.client_message_handler import ClientMessageHandlerThread


def open_server_connection(address: Tuple[str, int]):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(address)
        server_socket.listen()
        
        while True:
            client_socket, client_addr = server_socket.accept()
            print("Connected to {}:{}".format(client_addr[0], client_addr[1]))
            client_thread = ClientMessageHandlerThread(client_socket)
            client_thread.run()


def main():
    # hostname = socket.gethostname()
    hostname = "127.0.0.1"
    port_number = 7896
    address = (hostname, port_number)
    open_server_connection(address)


if __name__ == "__main__":
    main()
