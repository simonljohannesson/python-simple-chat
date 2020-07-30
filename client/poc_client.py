#!/bin/usr/python


import socket
import sys

def main():
    # server_hostname = "computer"
    server_hostname = "127.0.0.1"
    server_port_no = 7896
    server_address = (server_hostname, server_port_no)
    # for i in range(1000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(server_address)
        send_bytes = b'\x00<{"length": "52", "byteorder": "little", "encoding": "UTF-8"}{"action": "announcement", "content": "working"}'
        client_socket.sendall(send_bytes)
        print("Data sent: {} to {}:{}".format(
            send_bytes, server_address[0], server_address[1]))
        

if __name__ == "__main__":
    main()

