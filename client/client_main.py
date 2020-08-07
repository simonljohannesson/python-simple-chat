#!/bin/usr/python


import socket
from chat_helper_lib.message import *
from chat_helper_lib import protocol_handler


def main():
    # server_hostname = "computer"
    server_hostname = "127.0.0.1"
    server_port_no = 7897
    server_address = (server_hostname, server_port_no)
    # for i in range(1000):
    
    # create a message
    message = Message(Message.TYPE_CHAT_MESSAGE, "Hi there!!!", "Thor", "Freya")
    serialized_msg = protocol_handler.serialize_message(message)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(server_address)
        send_bytes = serialized_msg
        client_socket.sendall(send_bytes)
        print("Data sent: {} to {}:{}".format(
            send_bytes, server_address[0], server_address[1]))
        print("Message: {}".format(message))
        

if __name__ == "__main__":
    main()

