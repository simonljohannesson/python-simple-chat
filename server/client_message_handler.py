#client_message_handler.py


import threading
import socket
from chat_helper_lib.message import *
from chat_helper_lib import protocol_handler
from chat_helper_lib.protocol_handler import ProtocolViolationError
from server.database_handler import DatabaseHandler
# test module
from server.test import dump_data_in_chat_messages_amount_table, dump_data_in_chat_messages_table


class ClientMessageHandlerThread(threading.Thread):
    """
    Class used to dispatch threads that handles client connections.

    Attributes:
        client_socket (socket): The socket used to connect to client.
    """
    def __init__(self,
                 client_socket: socket.socket,
                 db_handler: DatabaseHandler):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.db_handler = db_handler
    
    def run(self):
        try:
            received_message = self._receive_client_message()
            print(received_message)
            self._determine_action(received_message)
            
        except ProtocolViolationError as error:
            print(error, ": ClientMessageHandlerThread tried to receive a message but it"
                  " was corrupt.")
        finally:
            self.client_socket.close()
        # test functions
        dump_data_in_chat_messages_table(self.db_handler)
        dump_data_in_chat_messages_amount_table(self.db_handler)

    def _receive_client_message(self) -> Message:
        try:
            with self.client_socket as s:
                # fetch fixed header
                fixed_header_size = 2
                buffer = self._receive_bytes(fixed_header_size, s)
                header = buffer[:fixed_header_size]
                msg_len = protocol_handler.deserialize_two_byte_header(header)
                # fetch rest of message
                buffer = buffer[fixed_header_size:]
                buffer = self._receive_bytes(msg_len, s, buffer)
                msg_content = protocol_handler.deserialize_json_object(buffer)
                message = protocol_handler.reassemble_message(msg_content)
                return message
        except ProtocolViolationError as error:
            # TODO: log
            print(error)
        finally:
            self.client_socket.close()
    
    def _receive_bytes(self, qty_bytes: int, s: socket.socket, buffer=b''):
        error_msg = "Did not receive expected number of bytes."
        buffer_length = len(buffer)
        while buffer_length < qty_bytes:
            data = s.recv(48)
            if not data:
                raise ProtocolViolationError(error_msg)
            buffer += data
            buffer_length = len(buffer)
        return buffer
    
    def _determine_action(self, message: Message):
        """
        Determines what action should be taken for a message.
        
        :param message:
        :return:
        """
        if message.msg_type == Message.TYPE_CHAT_MESSAGE:
            self.db_handler.add_chat_message_to_database(message)
        elif message.msg_type == Message.TYPE_REQUEST_NEW_MESSAGES:
            raise NotImplementedError("TYPE_REQUEST_NEW_MESSAGES not implemented")
        else:
            raise NotImplementedError(
                "Message type with value {} is not implemented".format(
                    message.msg_type))
