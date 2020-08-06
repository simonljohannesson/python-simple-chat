#client_message_handler.py


import threading
import socket
from chat_helper_lib.message import *
from chat_helper_lib import protocol_handler
from chat_helper_lib.protocol_handler import ProtocolViolationError
from server.database_handler import DatabaseHandler,NotPresentInDatabase
# test module
# from server.test import dump_data_in_chat_messages_amount_table, dump_data_in_chat_messages_table


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
            print("ClientMessageHandlerThread tried to receive a message but it"
                  " was corrupt.")
        finally:
            self.client_socket.close()
        # test functions
        # dump_data_in_chat_messages_table(self.db_handler)
        # dump_data_in_chat_messages_amount_table(self.db_handler)
        
    def _receive_client_message(self) -> Message:
        """
        :raises ProtocolViolationError: If the agreed protocol is not followed
        the exception will be thrown.
        :return:
        """
        error_msg = "Did not receive expected number of bytes."
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
                    raise ProtocolViolationError(error_msg)
                buffer_length += len(data)
                buffer += data
            fix_header = protocol_handler.deserialize_two_byte_header(buffer[:2])
            buffer = buffer[2:]
            buffer_length = len(buffer)
            
            # get variable header of message
            json_header_length = fix_header
            while buffer_length < json_header_length:
                data = s.recv(32)
                if not data:
                    raise ProtocolViolationError(error_msg)
                buffer_length += len(data)
                buffer += data
            json_header = protocol_handler.deserialize_json_object(buffer[:fix_header])
            buffer = buffer[fix_header:]
            buffer_length = len(buffer)
            
            # get message content
            msg_content_length = int(json_header["length"])
            while buffer_length < msg_content_length:
                data = s.recv(32)
                if not data:
                    raise ProtocolViolationError(error_msg)
                buffer_length += len(data)
                buffer += data
            msg_content = protocol_handler.deserialize_json_object(buffer[:msg_content_length])
            message = protocol_handler.reassemble_message(msg_content)
            return message
            
            
        
    def _determine_action(self, message: Message):
        """
        Determines what action should be taken for a message.
        
        :param message:
        :return:
        """
        # TODO: validate message type with message structure before doing anything
        if message.msg_type == Message.TYPE_CHAT_MESSAGE:
            self.db_handler.add_chat_message_to_database(message)
        elif message.msg_type == Message.TYPE_REQUEST_NEW_MESSAGES:
            raise NotImplementedError("TYPE_REQUEST_NEW_MESSAGES not implemented")
        else:
            raise NotImplementedError(
                "Message type with value {} is not implemented".format(
                    message.msg_type))
