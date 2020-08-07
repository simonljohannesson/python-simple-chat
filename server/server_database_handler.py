from threading import Lock
from chat_helper_lib.database_handler import DatabaseHandler


class ServerDatabaseHandler(DatabaseHandler):
    def __init__(self):
        super().__init__()
        self.database_lock = Lock()
        self.connection = self._setup_ram_sqlite_db()
