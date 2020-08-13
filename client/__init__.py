import json
import socket
import threading
import time
import database
import protocol
import sqlite3
import subprocess
import typing


class DBHandler(database.Handler):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self._setup_sqlite_db()
    
    def open_connection(self) -> sqlite3.Connection:
        pwd = subprocess.run("pwd", stdout=subprocess.PIPE).stdout.decode().strip()
        # print(pwd + self.db_path)
        connection = sqlite3.connect(self.db_path)
        return connection
    
    def _setup_sqlite_db(self):
        """
        Creates an sqlite3 database with the specifications of the database in the database_handler module.
        
        :return: the connection to the created database
        """
        connection = self.open_connection()
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
    
    def new_messages(self,
                     chat_identifier: str,
                     last_message: int) -> typing.List[protocol.Message]:
        con = self.open_connection()
        message_list = []
        msgs_avail_in_db = self.total_message_amount(con, chat_identifier)
        if not last_message < msgs_avail_in_db:
            return message_list
        for i in range(last_message + 1, msgs_avail_in_db + 1):
            msg_identifier = database.create_message_identifier(
                chat_identifier, i)
            msg_row = self._get_chat_message(con, msg_identifier)
            msg = database.table_row_to_msg(msg_row)
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


class ThreadKillFlag:
    def __init__(self):
        self.kill = False


class RefresherObserver:
    """
    Class that observes to the BackgroundDatabaseRefresher.
    """
    def new_messages_found(self):
        raise NotImplementedError
    
class NoMessageReceived(Exception):
    pass

class BackgroundDatabaseRefresher(threading.Thread):
    def __init__(self,
                 server_address: typing.Tuple[str, int],
                 db_handler: DBHandler,
                 user_name: str,
                 other_user: str,
                 kill_flag: ThreadKillFlag):
        threading.Thread.__init__(self)
        self.server_address = server_address
        self.db_handler = db_handler
        self.user_name = user_name
        self.other_user = other_user
        self.kill_flag = kill_flag
        self.refresher_observers = []
    
    def run(self):
        chat_identifier = database.create_chat_identifier(self.user_name,
                                                 self.other_user)
        while not self.kill_flag.kill:
            con = self.db_handler.open_connection()
            last_message = self.db_handler.total_message_amount(
                con,
                chat_identifier)
            query_msg = protocol.Message(protocol.Message.REQUEST_NEW_MESSAGES,
                                last_message,
                                self.user_name,
                                self.other_user)
            con.close()
            ser_msg = protocol.serialize_message(query_msg)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect(self.server_address)
                    s.sendall(ser_msg)
                    buffer = b''
                    while True:
                        data = s.recv(4096)
                        if not data:
                            if len(buffer) == 0:
                                raise NoMessageReceived
                            break
                        buffer += data
                    des_msg = protocol.reassemble_message(
                        protocol.deserialize_json_object(buffer[2:]))
                    
                    if len(buffer) > 0:
                        con = self.db_handler.open_connection()
                        list_of_msgs = json.loads(des_msg.content)
                        for each in list_of_msgs:
                            msg_cont = protocol.deserialize_json_object(each)
                            rec_msg = protocol.reassemble_message(msg_cont)
                            self.db_handler.add_chat_message_to_database(con, rec_msg)
                        # tell observers that new messages have been fetched and added
                        self.update_observers()
                        con.close()
                except NoMessageReceived:
                    pass
                finally:
                    s.close()
            time.sleep(2)
            # self.kill_flag.kill = True
            
    def add_observer(self, refresher_observer: RefresherObserver):
        self.refresher_observers.append(refresher_observer)
    
    def update_observers(self):
        for observer in self.refresher_observers:
            observer.new_messages_found()

