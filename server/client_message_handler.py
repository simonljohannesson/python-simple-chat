#client_message_handler.py


import threading
import socket
from chat_helper_lib.message import *
from chat_helper_lib import protocol_handler
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
        received_message = self._receive_client_message()
        print(received_message)
        self._determine_action(received_message)
        # test functions
        # dump_data_in_chat_messages_table(self.db_handler)
        # dump_data_in_chat_messages_amount_table(self.db_handler)
        
    def _receive_client_message(self) -> Message:
        """Handles the connection with the client socket.
        TODO: refactor, there is a more clever solution
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
            fix_header = protocol_handler.deserialize_two_byte_header(buffer[:2])
            buffer = buffer[2:]
            buffer_length = len(buffer)
            
            # get variable header of message
            json_header_length = fix_header
            while buffer_length < json_header_length:
                data = s.recv(32)
                if not data:
                    break
                    # TODO: throw exception?
                buffer_length += len(data)
                buffer += data
            # TODO: handle the MessageCorruptError
            json_header = protocol_handler.deserialize_json_object(buffer[:fix_header])
            buffer = buffer[fix_header:]
            buffer_length = len(buffer)
            
            # get message content
            msg_content_length = int(json_header["length"])
            while buffer_length < msg_content_length:
                data = s.recv(32)
                if not data:
                    break
                    # TODO: throw exception?
                buffer_length += len(data)
                buffer += data
            # TODO: handle the MessageCorruptError
            msg_content = protocol_handler.deserialize_json_object(buffer[:msg_content_length])
            # TODO: handle the ProtocolViolationError
            message = protocol_handler.reassemble_message(msg_content)
            return message
        # does this connection need to stay open in order to send back information?
        
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
