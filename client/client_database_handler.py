from threading import Lock
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
