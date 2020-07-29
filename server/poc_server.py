#!/bin/usr/python3


import socket


def main():
    hostname = socket.gethostname()
    port_number = 7896
    address = (hostname, port_number)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(address)
        server_socket.listen()
        
        client_socket, client_addr = server_socket.accept()
        with client_socket:
            print("Connected to {}", client_addr)
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(data)


if __name__ == "__main__":
    print(socket.gethostname())
    main()
