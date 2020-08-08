from threading import Lock
from chat_helper_lib.database_handler import DatabaseHandler
import chat_helper_lib.database_handler as database_handler
import sqlite3
from chat_helper_lib.message import Message
from chat_helper_lib import protocol_handler


class ServerDatabaseHandler(DatabaseHandler):
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
        # create an sqlite database in ram
        connection = sqlite3.connect(":memory:")
        # create a cursor to the database
        cursor = connection.cursor()
        with self.database_lock:
            self._setup_chat_message_amount_table(cursor)
            self._setup_chat_messages_table(cursor)
            connection.commit()
        return connection
    
    def get_new_messages(self, message: Message) -> Message:
        protocol_handler.validate_request_message_format(message)
        clients_last_message = int(message.content)
        chat_identifier = database_handler.create_chat_identifier(
            message.sender,
            message.receiver)
        messages_available_in_db = self._query_total_message_amount(
            chat_identifier)
        
        message_list = []
        
        # send maximum of 50 messages per request message
        if clients_last_message + 50 + 1 < messages_available_in_db:
            messages_available_in_db = clients_last_message + 50 + 1
            
        for i in range(clients_last_message + 1, messages_available_in_db + 1):
            message_identifier = database_handler.create_message_identifier(
                chat_identifier, i)
            msg_row = self._request_specific_chat_message(message_identifier)
            msg = database_handler.convert_chat_msgs_table_row_to_msg(msg_row)
            msg_serialized = protocol_handler.serialize_message_content(msg)
            message_list.append(msg_serialized)
            
        return_message = Message(Message.TYPE_NEW_MESSAGES,
                                 message_list)
        return return_message

# if __name__ == '__main__':
#     for each in range(1, 10):
#         print(each)