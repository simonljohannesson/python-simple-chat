from threading import Lock

from chat_helper_lib import database_handler, protocol_handler, message
from chat_helper_lib.database_handler import DatabaseHandler
# import chat_helper_lib.database_handler as database_handler
import sqlite3
from typing import List


class ClientDatabaseHandler(DatabaseHandler):
    def __init__(self, db_path):
        super().__init__()
        # self.database_lock = Lock()
        self.db_path = db_path
        self._setup_sqlite_db()
        # self.db_path = "./../database/client/clients.db"
    
    def open_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        return connection
    
    def _setup_sqlite_db(self):
        """
        Creates an sqlite3 database in RAM with the specifications of the database in the database_handler module.
        
        :return: the connection to the created database
        """
        # create an sqlite database in ram
        connection = self.open_connection()
        # create a cursor to the database
        cursor = connection.cursor()
        with self.database_lock:
            if self._table_exists(connection, "chat_message_amount"):
                self.clean_up_chat_message_amount(connection)
                self._setup_chat_message_amount_table(cursor)
            else:
                self._setup_chat_message_amount_table(cursor)

            if self._table_exists(connection, "chat_messages"):
                self.clean_up_chat_messages(connection)
                self._setup_chat_messages_table(cursor)
            else:
                self._setup_chat_messages_table(cursor)
            connection.commit()
        connection.close()
    
    def fetch_new_messages(self, chat_identifier: str, last_message: int) -> List[message.Message]:
        con = self.open_connection()
        message_list = []
        msgs_avail_in_db = self.query_total_message_amount(con, chat_identifier)
        if not last_message < msgs_avail_in_db:
            return message_list
        for i in range(last_message + 1, msgs_avail_in_db + 1):
            msg_identifier = database_handler.create_message_identifier(
                chat_identifier, i)
            msg_row = self._request_specific_chat_message(con, msg_identifier)
            msg = database_handler.convert_chat_msgs_table_row_to_msg(msg_row)
            message_list.append(msg)
        return message_list

    def _table_exists(self,
                      connection: sqlite3.Connection,
                      table_name: str) -> bool:
        cmd = """
        SELECT name FROM sqlite_master
            WHERE type='table'
            AND name=(?)
        """
        cursor = connection.cursor()
        cursor.execute(cmd, (table_name,))
        status = cursor.fetchone()
        if status is None:
            return False
        else:
            return True
    
    def clean_up_chat_messages(self, connection: sqlite3.Connection,):
        cursor = connection.cursor()
        cursor.execute("DROP TABLE chat_messages")
        connection.commit()

    def clean_up_chat_message_amount(self, connection: sqlite3.Connection,):
        cursor = connection.cursor()
        cursor.execute("DROP TABLE chat_message_amount")
        connection.commit()
