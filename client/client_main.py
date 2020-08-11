#!/bin/usr/python


import socket
from chat_helper_lib.message import *
from chat_helper_lib import protocol_handler, database_handler
import json
import client.client_database_handler as client_database_handler
# test module
from server.test import dump_data_in_chat_messages_amount_table, dump_data_in_chat_messages_table
from client_database_update_thread import ClientDatabaseUpdateThread, ThreadKillFlag
import os
import time

class ClientSession:
    def __init__(self,
                 db_handler: client_database_handler.ClientDatabaseHandler):
        self.db_handler = db_handler
        
    def _server_config(self, server_hostname: str, server_port_no: int):
        self.server_hostname = server_hostname
        self.server_port_no = server_port_no
        self.server_address = (self.server_hostname, self.server_port_no)
    
    def _log_in_user(self,  user_name: str):
        self.user_name = user_name
    
    def _add_other_user(self, other_user: str):
        self.other_user = other_user
        
    def _dispatch_background_update_thread(self) -> ThreadKillFlag:
        
        kill_flag = ThreadKillFlag()
        bg_thread = ClientDatabaseUpdateThread(self.server_address,
                                               self.db_handler,
                                               self.user_name,
                                               self.other_user,
                                               kill_flag)
        bg_thread.start()
        # bg_thread.run()
        return kill_flag
    
    def log_in(self, user_name: str):
        self._log_in_user(user_name)

    def open_chat(self, other_user: str) -> ThreadKillFlag:
        self._server_config("127.0.0.1", 55678)
        self._establish_connection()
        self._add_other_user(other_user)
        kill_flag = self._dispatch_background_update_thread()
        return kill_flag
        
    def close_chat(self, bg_update_db_kill_flag: ThreadKillFlag):
        bg_update_db_kill_flag.kill = True
        # TODO: anything else?
        
    def _establish_connection(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect(self.server_address)
                s.close()
            print("Connection established with {}:{}".format(
                self.server_address[0], self.server_address[1]))
        except socket.timeout as timeout:
            print("Could not connect to {}:{}, connection timed out.".format(
                self.server_address[0], self.server_address[1]))
            raise timeout
        
    def send_chat_message(self, text: str):
        message = Message(Message.TYPE_CHAT_MESSAGE,
                          text,
                          self.user_name,
                          self.other_user)
        serialized_message = protocol_handler.serialize_message(message)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # print("sending: {}".format(serialized_message))
                s.connect(self.server_address)
                s.sendall(serialized_message)
                # print("sent: {}".format(serialized_message))
                
        finally:
            # s.shutdown(socket.SHUT_RDWR)
            s.close()
            
    def fetch_new_messages(self, last_message: int):
        chat_identifier = database_handler.create_chat_identifier(
            self.user_name, self.other_user)
        # last_message = self.db_handler.query_total_message_amount(chat_identifier)
        
        new_msgs = self.db_handler.fetch_new_messages(chat_identifier,
                                                      last_message)
        return new_msgs


class ClientView:
    def __init__(self, client_session: ClientSession):
        self.client_session = client_session
    
    def run(self):
        # self.clear_terminal()
        # user_name_prompt = "Enter username: (1-30 alpha numeric characters)"
        # user_name = self.request_and_validate_user_name_input(user_name_prompt)
        # chat_with_prompt = "Enter username of whoever you want to talk to: " \
        #     "(1-30 alpha numeric characters)"
        # chat_with = self.request_and_validate_user_name_input(chat_with_prompt)
        # print("Welcome {}!".format(user_name))
        # print("Now chatting with {}.".format(chat_with))
        user_name = "user1"
        chat_with = "user2"
        user_input = "hello"
        
        self.client_session.log_in(user_name)
        bg_thread_kill_flag = self.client_session.open_chat(chat_with)
        
        chat_messages = []
        # chat_open = True
        # help_msg = "You have a few options:\n" \
        #            "1. Send message: enter message and press return.\n" \
        #            "2. Fetch new messages: enter 'fetch()' and press return\n" \
        #            "3. Show this help message: enter 'help()' and press return"\
        #            "4. Exit session: enter 'exit()' and press return"
        # while chat_open:
        #     print("Enter your message and press return to send.",
        #           "(For help enter: 'help()' and press return)")
        #     user_input = input()
        #     if user_input == "help()":
        #         self.clear_terminal()
        #         print(help_msg)
        #     elif user_input == "fetch()":
        #         new_msgs = self.client_session.fetch_new_messages(
        #             len(chat_messages))
        #         for each in new_msgs:
        #             chat_messages.append(each)
        #         self.clear_terminal()
        #         for each in chat_messages:
        #             print(each)
        #     elif user_input == "exit()":
        #         chat_open = False
        #         bg_thread_kill_flag.kill = True
        #
            # self.client_session.send_chat_message(user_input)
        # self.client_session._dispatch_background_update_thread()

        self.client_session.send_chat_message("one")
        self.client_session.send_chat_message("two")
        self.client_session.send_chat_message("three")
        self.client_session.send_chat_message("four")
        time.sleep(4)
        self.client_session.send_chat_message("good day")
        self.client_session.send_chat_message("good day")
        self.client_session.send_chat_message("good day")
        self.client_session.send_chat_message("good day")
        
        # self.client_session._dispatch_background_update_thread()
        time.sleep(1)
        
        # dump_data_in_chat_messages_amount_table(self.client_session.db_handler)
        # dump_data_in_chat_messages_table(self.client_session.db_handler)
        
        chat_messages = self.client_session.fetch_new_messages(len(chat_messages))
        print("@@@@@@@@@@@@@@@@@@@ CHAT @@@@@@@@@@@@@@@@@@@")
        for msg in chat_messages:
            print(msg)
        print("@@@@@@@@@@@@@@@@@ END CHAT @@@@@@@@@@@@@@@@@")
        
        
            
    def request_and_validate_user_name_input(self, prompt: str) -> str:
        user_name_valid = False
        user_name = ""
        while not user_name_valid:
            print(prompt)
            user_name = input()
            user_name_valid = self.validate_user_name(user_name)
        return user_name
        
    def clear_terminal(self):
        cmd = ""
        if os.name == "posix":
            cmd = "clear"
        else:
            cmd = "clr"
        os.system(cmd)
    
    def validate_user_name(self, user_name: str):
        if user_name.isalnum() and len(user_name) < 31:
            # TODO: validate name against server
            return True
        else:
            return False
    
def main():
    chat_db = client_database_handler.ClientDatabaseHandler("./../database/client/clients.db")
    client_session = ClientSession(chat_db)
    client_view = ClientView(client_session)
    client_view.run()
    
    # # server_hostname = "computer"
    # server_hostname = "127.0.0.1"
    # server_port_no = 7897
    # server_address = (server_hostname, server_port_no)
    # # for i in range(1000):
    #
    # # setup database
    # client_db = client.client_database_handler.ClientDatabaseHandler()
    #
    # # create a message
    # # message = Message(Message.TYPE_CHAT_MESSAGE, "f", "Thor", "Freya")
    # message = Message(Message.TYPE_REQUEST_NEW_MESSAGES,
    #                   "0", "Thor", "Freya")
    # serialized_msg = protocol_handler.serialize_message(message)
    #
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    #     client_socket.connect(server_address)
    #     send_bytes = serialized_msg
    #     client_socket.sendall(send_bytes)
    #     print("Data sent: ->{}<- to {}:{}".format(
    #         send_bytes, server_address[0], server_address[1]))
    #     print("Message: {}".format(message))
    #     if message.msg_type == Message.TYPE_REQUEST_NEW_MESSAGES:
    #         buffer = b''
    #         while True:
    #             data = client_socket.recv(4096)
    #             if not data:
    #                 break
    #             buffer += data
    #         print("Received answer back:", buffer)
    #         des_msg = protocol_handler.reassemble_message(
    #             protocol_handler.deserialize_json_object(buffer[2:]))
    #
    #         list_of_msgs = json.loads(des_msg.content)
    #         for each in list_of_msgs:
    #             msg_cont = protocol_handler.deserialize_json_object(each)
    #             rec_msg = protocol_handler.reassemble_message(msg_cont)
    #             client_db.add_chat_message_to_database(rec_msg)
    #
    #         dump_data_in_chat_messages_table(client_db)
    #         dump_data_in_chat_messages_amount_table(client_db)


if __name__ == "__main__":
    main()
