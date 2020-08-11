import threading
from typing import Tuple
from client_database_handler import ClientDatabaseHandler
from chat_helper_lib.database_handler import create_chat_identifier
from chat_helper_lib.message import Message
from chat_helper_lib import protocol_handler
import time
import socket
import json


class ThreadKillFlag:
    def __init__(self):
        self.kill = False


class ClientDatabaseUpdateThread(threading.Thread):
    def __init__(self,
                 server_address: Tuple[str, int],
                 db_handler: ClientDatabaseHandler,
                 user_name: str,
                 other_user: str,
                 kill_flag: ThreadKillFlag):
        threading.Thread.__init__(self)
        self.server_address = server_address
        self.db_handler = db_handler
        self.user_name = user_name
        self.other_user = other_user
        self.kill_flag = kill_flag

    def run(self):
        chat_identifier = create_chat_identifier(self.user_name,
                                                 self.other_user)
        while not self.kill_flag.kill:
            con = self.db_handler.open_connection()
            last_message = self.db_handler.query_total_message_amount(
                con,
                chat_identifier)
            query_msg = Message(Message.TYPE_REQUEST_NEW_MESSAGES,
                                last_message,
                                self.user_name,
                                self.other_user)
            con.close()
            ser_msg = protocol_handler.serialize_message(query_msg)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.server_address)
                s.sendall(ser_msg)
                buffer = b''
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    buffer += data
                des_msg = protocol_handler.reassemble_message(
                    protocol_handler.deserialize_json_object(buffer[2:]))

                if len(buffer) > 0:
                    con = self.db_handler.open_connection()
                    list_of_msgs = json.loads(des_msg.content)
                    for each in list_of_msgs:
                        msg_cont = protocol_handler.deserialize_json_object(each)
                        rec_msg = protocol_handler.reassemble_message(msg_cont)
                        self.db_handler.add_chat_message_to_database(con, rec_msg)
                    con.close()
                s.close()
            time.sleep(2)
            # self.kill_flag.kill = True
