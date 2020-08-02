#client_thread.py


import threading
import socket
from chat_helper_lib.message import *
from chat_helper_lib import protocol_handler


# TODO: rename this class
class ClientThread(threading.Thread):
    """
    Class used to dispatch threads that handles client connections.

    Attributes:
        client_socket (socket): The socket used to connect to client.
    """
    def __init__(self, client_socket: socket.socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
    
    def run(self):
        received_message = self._receive_client_message()
        print(received_message)
        # if not received_message.check_message_structure_valid():
        #     return
        # self._act_on_message(received_message)
        
    def _receive_client_message(self) -> Message:
        """Handles the connection with the client socket.
        TODO: could send information by having a listener or reference to msg parser
        TODO: refactor to something slightly more clever
        """
        buffer_length = 0
        fix_header = 0
        json_header = None
        msg_content = None
        buffer = b''
        with self.client_socket as s:
            # get fixed header of message
            while buffer_length < 2:
                data = s.recv(2)
                if not data:
                    break                       # TODO: throw exception?
                buffer_length += len(data)
                buffer += data
            # TODO: message.deserialize_content should throw exception
            fix_header = protocol_handler.deserialize_two_byte_header(buffer[:2])
            buffer = buffer[2:]
            buffer_length = len(buffer)
            
            # get variable header of message
            json_header_length = fix_header
            while buffer_length < json_header_length:
                data = s.recv(32)
                if not data:
                    break                       # TODO: throw exception?
                buffer_length += len(data)
                buffer += data
            # TODO: message.deserialize_var_len_head throws exception
            json_header = protocol_handler.deserialize_json_object(buffer[:fix_header])
            buffer = buffer[fix_header:]
            buffer_length = len(buffer)
            
            # get message content
            msg_content_length = int(json_header["length"])
            while buffer_length < msg_content_length:
                data = s.recv(32)
                if not data:
                    break                       # TODO: throw exception?
                buffer_length += len(data)
                buffer += data
            # TODO: message.deserialize_content throws exception
            msg_content = protocol_handler.deserialize_json_object(buffer[:msg_content_length])
            # code will break here because Message now takes a msg msg_type and message not a dict.
            # raise NotImplementedError
            message = protocol_handler.reassemble_message(msg_content)
            return message
        # does this connection need to stay open in order to send back information?
        
    def _act_on_message(self, message: Message):
        # call database handler with the appropriate function
        raise NotImplementedError
