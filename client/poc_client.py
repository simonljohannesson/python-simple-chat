#!/bin/usr/python


import socket


def main():
    server_hostname = "computer"
    server_port_no = 7896
    server_address = (server_hostname, server_port_no)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(server_address)
        client_socket.sendall(b'Hi there!')
        print("Data sent: 'Hi there!")
        

if __name__ == "__main__":
    main()
