#message_handler.py
import threading
import socket
from chat_helper_lib.message import *
from chat_helper_lib import protocol_handler
from chat_helper_lib.protocol_handler import ProtocolViolationError


class MessageHandlerThread(threading.Thread):
    """
    Class used to dispatch threads that handles connections.

    Attributes:
        s (socket): The socket that a message should be received from.
    """
    def __init__(self, s: socket.socket):
        threading.Thread.__init__(self)
        self.current_socket = s
    
    def run(self):
        try:
            with self.current_socket:
                received_message = self._receive_client_message()
                self._determine_action(received_message)
        
        except ProtocolViolationError as error:
            print("Dropped a message due to violation of protocol.")

    def _receive_client_message(self) -> Message:
        # fetch fixed header
        fixed_header_size = 2
        buffer = self._receive_bytes(fixed_header_size, self.current_socket)
        if len(buffer) < 2:
            raise ProtocolViolationError("Message received not correct length.")
        
        header = buffer[:fixed_header_size]
        msg_len = protocol_handler.deserialize_two_byte_header(header)
        # fetch rest of message
        buffer = buffer[fixed_header_size:]
        buffer = self._receive_bytes(msg_len, self.current_socket, buffer)
        if len(buffer) < msg_len:
            raise ProtocolViolationError("Message received not correct length.")
        
        msg_content = protocol_handler.deserialize_json_object(buffer)
        message = protocol_handler.reassemble_message(msg_content)
        return message
        # except ProtocolViolationError as error:
        #     TODO: log
            # print(error)
            # self.current_socket.close()
 
    
    def _receive_bytes(self, qty_bytes: int, s: socket.socket, buffer=b''):
        error_msg = "Did not receive expected number of bytes. (message handler)"
        buffer_length = len(buffer)
        while buffer_length < qty_bytes:
            data = s.recv(4096)
            if not data:
                break
            buffer += data
            buffer_length = len(buffer)
        return buffer
    
    def _determine_action(self, message: Message):
        """
        Determines what action should be taken for a message.
        
        :param message:
        :return:
        """
        raise NotImplementedError
