#server_message_handler.py


import threading
import socket
from chat_helper_lib.message import *
from chat_helper_lib import protocol_handler, message_handler
from chat_helper_lib.protocol_handler import ProtocolViolationError
from server.database_handler import DatabaseHandler
# test module
# from server.test import dump_data_in_chat_messages_amount_table, dump_data_in_chat_messages_table


class ServerMessageHandlerThread(message_handler.MessageHandlerThread):
    def _determine_action(self, message: Message):
        """
        Determines what action should be taken for a message.
        
        :param message:
        :return:
        """
        if message.msg_type == Message.TYPE_CHAT_MESSAGE:
            self.db_handler.add_chat_message_to_database(message)
        elif message.msg_type == Message.TYPE_REQUEST_NEW_MESSAGES:
            raise NotImplementedError("TYPE_REQUEST_NEW_MESSAGES not implemented")
        else:
            raise NotImplementedError(
                "Message type with value {} is not implemented".format(
                    message.msg_type))
