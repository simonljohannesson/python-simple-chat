#!/bin/usr/python3
import socket
import typing
import server


def open_connection(address: typing.Tuple[str, int],
                    db_handler: server.ServerDBHandler) -> None:
    """
    Opens the server to listen for incoming messages.
    
    :param address: the address that the server should open at.
    :param db_handler: the database handler for the server
    :return: None
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(address)
        server_socket.listen()
        while True:
            try:
                client_socket, client_addr = server_socket.accept()
                print("Connected to {}:{}".format(client_addr[0], client_addr[1]))
                msg_handler = server.ServerConnectionController(client_socket, db_handler)
                msg_handler.receive_process()
            except KeyboardInterrupt:
                break
        server_socket.close()


def main():
    """Starts the server."""
    # hostname = socket.gethostname()
    hostname = "127.0.0.1"
    port_number = 55678
    address = (hostname, port_number)
    db_handler = server.ServerDBHandler()
    open_connection(address, db_handler)


if __name__ == "__main__":
    main()
