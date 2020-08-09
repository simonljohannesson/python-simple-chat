#!/bin/usr/python3


import socket
from typing import Tuple
from server.server_message_handler import ServerMessageHandlerThread
from server.server_database_handler import ServerDatabaseHandler
from chat_helper_lib.message import Message


def open_server_connection(address: Tuple[str, int],
                           db_handler: ServerDatabaseHandler):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(address)
        server_socket.listen()
        
        while True:
            client_socket, client_addr = server_socket.accept()
            print("Connected to {}:{}".format(client_addr[0], client_addr[1]))
            client_thread = \
                ServerMessageHandlerThread(client_socket, db_handler)
            client_thread.run()
            

def main():
    # hostname = socket.gethostname()
    hostname = "127.0.0.1"
    port_number = 7899
    address = (hostname, port_number)
    db_handler = ServerDatabaseHandler()
    open_server_connection(address, db_handler)


if __name__ == "__main__":
    main()
