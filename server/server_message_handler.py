#server_message_handler.py


from chat_helper_lib.message import *
from chat_helper_lib import message_handler, protocol_handler
import socket
from server.server_database_handler import ServerDatabaseHandler



# test module
from server.test import dump_data_in_chat_messages_amount_table, dump_data_in_chat_messages_table


class ServerMessageHandlerThread(message_handler.MessageHandlerThread):
    def __init__(self, s: socket.socket, db_handler: ServerDatabaseHandler):
        super().__init__(s)
        self.db_handler = db_handler
        
    def _determine_action(self, message: Message):
        """
        Determines what action should be taken for a message.
        
        :param message:
        :return:
        """
        if message.msg_type == Message.TYPE_CHAT_MESSAGE:
            self.db_handler.add_chat_message_to_database(message)
            
        elif message.msg_type == Message.TYPE_REQUEST_NEW_MESSAGES:
            new_msgs = self.db_handler.get_new_messages(message)
            serialized_new_msgs = protocol_handler.serialize_message(new_msgs)
            self.current_socket.sendall(serialized_new_msgs)
        else:
            raise NotImplementedError(
                "Message type with value {} is not implemented".format(
                    message.msg_type))
        
        dump_data_in_chat_messages_table(self.db_handler)
        dump_data_in_chat_messages_amount_table(self.db_handler)