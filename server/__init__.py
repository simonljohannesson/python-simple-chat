# server.py
import socket
import threading
import database
import sqlite3
import protocol
import json


class ServerDBHandler(database.Handler):
    """
    Class that handles the servers database.
    """
    def __init__(self):
        super().__init__()
        self.database_lock = threading.Lock()
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
    
    def get_new_messages(self, message: protocol.Message) -> protocol.Message:
        """
        Returns any messages in the database newer than the message specified.
        :raises database.NotPresentInDatabase: when no newer messages exist.
        :param message: message with type REQUEST_NEW_MESSAGES and its content
                        contains the number of the last message it has
        :return: a message containing serialized messages in its content
        """
        protocol.validate_request_message_format(message)
        clients_last_message = int(message.content)
        chat_identifier = database.create_chat_identifier(
            message.sender,
            message.receiver)
        messages_available_in_db = self.total_message_amount(
            self.connection,
            chat_identifier)
        
        message_list = []
        
        if clients_last_message >= messages_available_in_db:
            raise database.NotPresentInDatabase(
                "There are no new messages in the database.")
        
        # send maximum of 50 messages per request message
        if clients_last_message + 50 + 1 < messages_available_in_db:
            messages_available_in_db = clients_last_message + 50 + 1
        
        for i in range(clients_last_message + 1, messages_available_in_db + 1):
            message_identifier = database.create_message_identifier(
                chat_identifier, i)
            msg_row = self._get_chat_message(self.connection, message_identifier)
            msg = database.table_row_to_msg(msg_row)
            msg_serialized = protocol.serialize_message_content(msg)
            message_list.append(msg_serialized)
        
        ser_msg_list = json.dumps(message_list)
        return_message = protocol.Message(
            protocol.Message.NEW_MESSAGES,
            ser_msg_list)
        return return_message


class ServerConnectionController():
    """
    Class that controlls the connections being made to the server.
    """
    def __init__(self, s: socket.socket, db_handler: ServerDBHandler):
        self.current_socket = s
        self.db_handler = db_handler

    def receive_process(self):
        """
        Receives and processes a message.
        
        If the message protocol is not followed the message will be dropped.
        :return:
        """
        try:
            with self.current_socket:
                received_message = self._receive_client_message()
                self._determine_action(received_message)
    
        except protocol.ProtocolViolationError as error:
            print("Dropped a message due to violation of protocol.")

    def _receive_client_message(self) -> protocol.Message:
        """
        Receives an incoming message and turns it into a protocol.Message.
        
        :raises protocol.ProtocolViolationError: if the received message does
                not follow protocol
        :return:
        """
        # fetch fixed header
        fixed_header_size = 2
        buffer = self._receive_bytes(fixed_header_size)
        if len(buffer) < 2:
            raise protocol.ProtocolViolationError(
                "Message received not correct length.")
    
        header = buffer[:fixed_header_size]
        msg_len = protocol.deserialize_two_byte_header(header)
        # fetch rest of message
        buffer = buffer[fixed_header_size:]
        buffer = self._receive_bytes(msg_len, buffer)
        if len(buffer) < msg_len:
            raise protocol.ProtocolViolationError(
                "Message received not correct length.")
    
        msg_content = protocol.deserialize_json_object(buffer)
        message = protocol.reassemble_message(msg_content)
        return message

    def _receive_bytes(self, qty_bytes: int, buffer=b''):
        """
        Receives at least the specified amount of bytes.
        
        The bytes will be added to the buffer, if any is passed otherwise a new
        buffer, and then returned.
        :param qty_bytes: amount of bytes to receive at minimum
        :param buffer: buffer that will be appended with the received bytes
        :return: buffer containing at least the specified amount of bytes
        """
        buffer_length = len(buffer)
        while buffer_length < qty_bytes:
            data = self.current_socket.recv(4096)
            if not data:
                break
            buffer += data
            buffer_length = len(buffer)
        return buffer

    def _determine_action(self, message: protocol.Message):
        """
        Determines what action should be taken for a message.
        
        :param message:
        :return:
        """
        if message.msg_type == protocol.Message.CHAT_MESSAGE:
            connection = self.db_handler.connection
            self.db_handler.add_chat_message_to_database(connection, message)
            
        elif message.msg_type == protocol.Message.REQUEST_NEW_MESSAGES:
            try:
                new_msgs = self.db_handler.get_new_messages(message)
                serialized_new_msgs = protocol.serialize_message(new_msgs)
                self.current_socket.sendall(serialized_new_msgs)
            except database.NotPresentInDatabase:
                self.current_socket.close()
        else:
            raise NotImplementedError(
                "Message type with value {} is not implemented".format(
                    message.msg_type))
