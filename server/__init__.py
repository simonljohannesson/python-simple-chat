# server.py
import socket
# test module
from test import dump_data_in_chat_messages_amount_table, dump_data_in_chat_messages_table
from threading import Lock
from database import Handler
import database as database_handler
import sqlite3
from protocol import Message
import protocol
import json


class ServerDBHandler(Handler):
    def __init__(self):
        super().__init__()
        self.database_lock = Lock()
        self.connection = self._setup_ram_sqlite_db()
    
    def _setup_ram_sqlite_db(self) -> sqlite3.Connection:
        """
        Creates an sqlite3 database in RAM with the specifications of the
        database in the database_handler module.
        
        :return: the connection to the created database
        """
        connection = sqlite3.connect(":memory:")
        cursor = connection.cursor()
        with self.database_lock:
            self._setup_chat_message_amount_table(cursor)
            self._setup_chat_messages_table(cursor)
            connection.commit()
        return connection
    
    def get_new_messages(self, message: Message) -> Message:
        protocol.validate_request_message_format(message)
        clients_last_message = int(message.content)
        chat_identifier = database_handler.create_chat_identifier(
            message.sender,
            message.receiver)
        messages_available_in_db = self.total_message_amount(
            self.connection,
            chat_identifier)
        
        message_list = []
        
        # send maximum of 50 messages per request message
        if clients_last_message + 50 + 1 < messages_available_in_db:
            messages_available_in_db = clients_last_message + 50 + 1
        
        for i in range(clients_last_message + 1, messages_available_in_db + 1):
            message_identifier = database_handler.create_message_identifier(
                chat_identifier, i)
            msg_row = self._get_chat_message(self.connection, message_identifier)
            msg = database_handler.table_row_to_msg(msg_row)
            msg_serialized = protocol.serialize_message_content(msg)
            message_list.append(msg_serialized)
        
        ser_msg_list = json.dumps(message_list)
        return_message = Message(Message.NEW_MESSAGES,
                                 ser_msg_list)
        return return_message


class ServerConnectionController(protocol.ConnectionController):
    def __init__(self, s: socket.socket, db_handler: ServerDBHandler):
        super().__init__(s)
        self.db_handler = db_handler

    def _determine_action(self, message: Message):
        """
        Determines what action should be taken for a message.
        
        :param message:
        :return:
        """
        if message.msg_type == Message.CHAT_MESSAGE:
            connection = self.db_handler.connection
            self.db_handler.add_chat_message_to_database(connection, message)
            dump_data_in_chat_messages_table(self.db_handler)
            dump_data_in_chat_messages_amount_table(self.db_handler)
            
        elif message.msg_type == Message.REQUEST_NEW_MESSAGES:
            new_msgs = self.db_handler.get_new_messages(message)
            serialized_new_msgs = protocol.serialize_message(new_msgs)
            self.current_socket.sendall(serialized_new_msgs)
        else:
            raise NotImplementedError(
                "Message type with value {} is not implemented".format(
                    message.msg_type))
