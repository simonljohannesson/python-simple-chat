from threading import Lock

from chat_helper_lib import database_handler, protocol_handler
from chat_helper_lib.database_handler import DatabaseHandler
# import chat_helper_lib.database_handler as database_handler
import sqlite3


class ClientDatabaseHandler(DatabaseHandler):
    def __init__(self):
        super().__init__()
        self.database_lock = Lock()
        self.connection = self._setup_ram_sqlite_db()
    
    def _setup_ram_sqlite_db(self) -> sqlite3.Connection:
        """
        Creates an sqlite3 database in RAM with the specifications of the database in the database_handler module.
        
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
    
    def fetch_new_messages(self, chat_identifier: str, last_message: int):
        message_list = []
        msgs_avail_in_db = self.query_total_message_amount(chat_identifier)
        if not last_message < msgs_avail_in_db:
            return message_list
        for i in range(last_message + 1, msgs_avail_in_db + 1):
            msg_identifier = database_handler.create_message_identifier(
                chat_identifier, i)
            msg_row = self._request_specific_chat_message(msg_identifier)
            msg = database_handler.convert_chat_msgs_table_row_to_msg(msg_row)
            message_list.append(str(msg))
        return message_list
