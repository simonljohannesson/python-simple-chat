#!/bin/usr/python
import subprocess
import typing
import database
import client
import os
import protocol
import socket


# PATH_TO_DATABASE = "./cl1db/client1.db"
PATH_TO_DATABASE = "./cl2db/client2.db"


class ClientSession:
    def __init__(self,
                 db_handler: client.DBHandler,
                 server_address: typing.Tuple[str, int]):
        self.db_handler = db_handler
        self.server_address = server_address
    
    def _log_in_user(self,  user_name: str):
        self.user_name = user_name
    
    def _add_other_user(self, other_user: str):
        self.other_user = other_user
    
    def _dispatch_background_update_thread(self, refresher_observer: client.RefresherObserver) -> client.ThreadKillFlag:
        
        kill_flag = client.ThreadKillFlag()
        bg_thread = client.BackgroundDatabaseRefresher(self.server_address,
                                                       self.db_handler,
                                                       self.user_name,
                                                       self.other_user,
                                                       kill_flag)
        bg_thread.add_observer(refresher_observer)
        bg_thread.start()
        return kill_flag
    
    def log_in(self, user_name: str):
        self._log_in_user(user_name)
    
    def open_chat(self, other_user: str, refresher_observer: client.RefresherObserver) -> client.ThreadKillFlag:
        self._test_connection()
        self._add_other_user(other_user)
        kill_flag = self._dispatch_background_update_thread(refresher_observer)
        return kill_flag
    
    def close_chat(self, bg_update_db_kill_flag: client.ThreadKillFlag):
        bg_update_db_kill_flag.kill = True
        # TODO: anything else?
    
    def _test_connection(self):
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
        message = protocol.Message(protocol.Message.CHAT_MESSAGE,
                                   text,
                                   self.user_name,
                                   self.other_user)
        serialized_message = protocol.serialize_message(message)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.server_address)
                s.sendall(serialized_message)
        
        finally:
            s.close()
    
    def fetch_new_messages(self, last_message: int):
        chat_identifier = database.create_chat_identifier(
            self.user_name, self.other_user)
        new_msgs = self.db_handler.new_messages(chat_identifier, last_message)
        return new_msgs


class ClientViewPrinter(client.RefresherObserver):
    def __init__(self, client_session: ClientSession):
        self.client_session = client_session
        self.chat_messages_of_session = []
    
    def _add_usernames(self, username, chat_with):
        self.username = username
        self.chat_with = chat_with
    
    def clear_terminal(self):
        cmd = ""
        if os.name == "posix":
            cmd = "clear"
        else:
            cmd = "clr"
        os.system(cmd)
    
    def print_welcome_message(self, username, chat_with):
        self._add_usernames(username, chat_with)
        welcome = "Welcome {}!\n You are now chatting with {}.".format(
            self.username, self.chat_with)
        print(welcome)
    
    def prompt_for_username(self):
        self.clear_terminal()
        user_name_prompt = "Enter username: (1-30 alpha numeric characters)"
        print(user_name_prompt)
    
    def prompt_who_to_chat_with(self):
        self.clear_terminal()
        chat_with_prompt = "Enter username of whoever you want to talk to: " \
                           "(1-30 alpha numeric characters)"
        print(chat_with_prompt)
    
    def print_username_invalid(self):
        print("Username invalid.")
    
    def print_chat_messages(self):
        self.clear_terminal()
        print("============= Messages in chat with: {} =============")
        # print("============= Messages in chat with: {} =============".format(
        #     self.chat_with))
        for msg in self.chat_messages_of_session:
            print("{} said: {}".format(msg.sender, msg.content))
        print("============= End of messages ============")
        self.print_enter_message_prompt()
    
    def print_help_message(self):
        self.clear_terminal()
        help_msg = "You have a few options:\n" \
                   "1. Send message: enter message and press return.\n" \
                   "2. Show this help message: enter 'help()' and press return" \
                   "3. Exit session: enter 'exit()' and press return"
        print(help_msg)
    
    def print_enter_message_prompt(self):
        message = "Enter your message and press return to send. " \
                  "(For help enter: 'help()' and press return)"
        print(message)
    
    def collect_new_messages(self):
        new_msgs = self.client_session.fetch_new_messages(
            len(self.chat_messages_of_session))
        for each in new_msgs:
            self.chat_messages_of_session.append(each)
    
    def print_newest_messages(self):
        self.new_messages_found()
    
    def new_messages_found(self):
        """
        When called will fetch all new messages and print them to the user.
        :return:
        """
        self.collect_new_messages()
        self.clear_terminal()
        self.print_chat_messages()


class UserInteraction:
    def __init__(self, client_session: ClientSession, view_printer: ClientViewPrinter):
        self.client_session = client_session
        self.view_printer = view_printer
    
    def validate_user_name(self, user_name: str):
        if user_name.isalnum() and len(user_name) < 31:
            # TODO: validate name against server
            return True
        else:
            return False
    
    def request_and_validate_user_name_input(self) -> str:
        user_name_valid = False
        user_name = ""
        while not user_name_valid:
            user_name = input()
            user_name_valid = self.validate_user_name(user_name)
            if not user_name_valid:
                self.view_printer.print_username_invalid()
        return user_name
    
    def run(self, refresher_observer: client.RefresherObserver):
        self.view_printer.prompt_for_username()
        username = self.request_and_validate_user_name_input()
        self.view_printer.prompt_who_to_chat_with()
        chat_with = self.request_and_validate_user_name_input()
        
        self.client_session.log_in(username)
        self.view_printer.print_welcome_message(username, chat_with)
        
        bg_thread_kill_flag = self.client_session.open_chat(chat_with, refresher_observer)
        
        chat_messages = []
        chat_open = True
        while chat_open:
            self.view_printer.print_enter_message_prompt()
            try:
                user_input = input()
            except KeyboardInterrupt:
                user_input = "exit()"
            if user_input == "help()":
                self.view_printer.print_help_message()
            elif user_input == "fetch()":
                self.view_printer.print_chat_messages()
            elif user_input == "exit()":
                # close chat and shutdown background refresh thread
                chat_open = False
                bg_thread_kill_flag.kill = True
            else:
                self.client_session.send_chat_message(user_input)


def main():
    hostname = "127.0.0.1"
    port_number = 55677
    server_address = (hostname, port_number)
    
    chat_db = client.DBHandler(PATH_TO_DATABASE)
    client_session = ClientSession(chat_db, server_address)
    view_printer = ClientViewPrinter(client_session)
    user_interaction = UserInteraction(client_session, view_printer)
    user_interaction.run(view_printer)


if __name__ == "__main__":
    print("client 1: {}".format(subprocess.run("pwd", stdout=subprocess.PIPE).stdout))
    main()
