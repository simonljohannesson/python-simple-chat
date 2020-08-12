#!/bin/usr/python
import socket
from chat_helper_lib.message import *
from chat_helper_lib import protocol_handler, database
import client.client_database_handler as client_database_handler
# test module
from server.test import dump_data_in_chat_messages_amount_table, dump_data_in_chat_messages_table
from client_database_update_thread import ClientDatabaseUpdateThread, ThreadKillFlag
import os


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
        return kill_flag
    
    def log_in(self, user_name: str):
        self._log_in_user(user_name)

    def open_chat(self, other_user: str) -> ThreadKillFlag:
        self._server_config("127.0.0.1", 55679)
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
                s.connect(self.server_address)
                s.sendall(serialized_message)
                
        finally:
            s.close()
            
    def fetch_new_messages(self, last_message: int):
        chat_identifier = database.create_chat_identifier(
            self.user_name, self.other_user)
        
        new_msgs = self.db_handler.fetch_new_messages(chat_identifier,
                                                      last_message)
        return new_msgs


class ClientView:
    def __init__(self, client_session: ClientSession):
        self.client_session = client_session
    
    def run(self):
        self.clear_terminal()
        user_name_prompt = "Enter username: (1-30 alpha numeric characters)"
        user_name = self.request_and_validate_user_name_input(user_name_prompt)
        chat_with_prompt = "Enter username of whoever you want to talk to: " \
            "(1-30 alpha numeric characters)"
        chat_with = self.request_and_validate_user_name_input(chat_with_prompt)
        print("Welcome {}!".format(user_name))
        print("Now chatting with {}.".format(chat_with))
        # user_name = "user1"
        # chat_with = "user2"
        # user_input = "hello"
        
        self.client_session.log_in(user_name)
        bg_thread_kill_flag = self.client_session.open_chat(chat_with)
        
        chat_messages = []
        chat_open = True
        help_msg = "You have a few options:\n" \
                   "1. Send message: enter message and press return.\n" \
                   "2. Fetch new messages: enter 'fetch()' and press return\n" \
                   "3. Show this help message: enter 'help()' and press return"\
                   "4. Exit session: enter 'exit()' and press return"
        while chat_open:
            print("Enter your message and press return to send.",
                  "(For help enter: 'help()' and press return)")
            try:
                user_input = input()
            except KeyboardInterrupt:
                user_input = "exit()"
            if user_input == "help()":
                self.clear_terminal()
                print(help_msg)
            elif user_input == "fetch()":
                new_msgs = self.client_session.fetch_new_messages(
                    len(chat_messages))
                for each in new_msgs:
                    chat_messages.append(each)
                self.clear_terminal()
                print("============= Messages in chat with: {} =============".format(chat_with))
                for msg in chat_messages:
                    print("{} said: {}".format(msg.sender, msg.content))
                print("============= End of messages ============")
            elif user_input == "exit()":
                chat_open = False
                bg_thread_kill_flag.kill = True
            else:
                self.client_session.send_chat_message(user_input)

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
    

if __name__ == "__main__":
    main()
