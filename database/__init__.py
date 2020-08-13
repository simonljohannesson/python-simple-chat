# client.py
"""
This module is designed to create and operate on an sqlite3 database with the
specifications described further down.


Database specification:

The database consist of two tables. The first (1) is named 'chat_message_amount'
and the second (2) is named 'chat_messages'.

Table 1
    Consist of three columns, the first named 'message_identifier' consists of a
    concatenation of the senders name, the receivers name and the number of the
    message in the chat. The number is received from the 'total_message_amount'
    table. The concatenation is in the format '<user-name>:<user-name>:number',
    and the order of the senders and the receivers name is the name with the
    smaller string value first and then the name with the larger string value.
    The first column 'message_identifier' is also a primary key. The second
    column contains the message. The third column contains the user name of the
    sender.\n
    
    Table layout: \n
    .. table:: total_message_amount
    :widths: 20 15 15
    
    +-------------------+------------+--------+
    |message_identifier | message    | sender |
    +-------------------+------------+--------+
    |user1:user2:1      | hello!     | user2  |
    +-------------------+------------+--------+
    |user1:user2:2      | hi there!  | user1  |
    +-------------------+------------+--------+
    |user3:user5:1      | good day   | user3  |
    +-------------------+------------+--------+

    
Table 2
    Consist of two columns, the first named 'chat_identifier' consist of a
    concatenation of the senders name and the receivers name, where the name
    with the smallest string value comes first and in the format
    '<user-name>:<user-name>'. The column is also a primary key. The second
    column named 'total_message_amount' holds the amount of messages that are in
    the database in the chat.\n
    
    Table layout: \n
    .. table:: total_message_amount
    :widths: 20 25
    
    +----------------+----------------------+
    |chat_identifier | total_message_amount |
    +----------------+----------------------+
    |user1:user2     | 2                    |
    +----------------+----------------------+
    |user3:user5     | 1                    |
    +----------------+----------------------+

"""
import sqlite3
import typing
import threading
import protocol


class Handler:
    def __init__(self):
        self.database_lock = threading.Lock()

    def _add_chat_message_row(self,
                              connection: sqlite3.Connection,
                              message_identifier: str,
                              message: str,
                              sender: str) -> None:
        """
        Inserts a new row in the chat_messages table.
        
        :param message_identifier: the message identifier in the database
        :param message: message that should be added to the database
        :param sender: sender of the message
        :return: None
        """
        cursor = connection.cursor()
        with self.database_lock:
            cursor.execute(
                "INSERT INTO chat_messages values (?, ?, ?)",
                (message_identifier, message, sender))
            connection.commit()

    def _get_chat_message(self,
                          connection: sqlite3.Connection,
                          message_identifier: str
                          ) -> typing.Tuple[str, str, str]:
        """
        Queries the database for a specific chat message.
        
        :raises NotPresentInDatabase: Raised when the specified message does not
                                      exist in the database.
        :param message_identifier: the message identifier
        :return: a tuple of the row containing the specific chat message
        """
        cursor = connection.cursor()
        row = None
        with self.database_lock:
            cursor.execute(
                """
                SELECT
                    message_identifier,
                    message,
                    sender
                FROM
                    chat_messages
                WHERE
                    message_identifier =(?)
                """,
                (message_identifier,))
            row = cursor.fetchone()
        if row is None:
            raise NotPresentInDatabase
        return row

    def total_message_amount(self,
                             connection: sqlite3.Connection,
                             chat_identifier: str) -> int:
        """
        Queries the database how many messages are saved to the chat_identifiers chat.
        
        If the chat_identifier is not found in the database the return value will be 0.
        :param connection:
        :param chat_identifier: the chats identifier
        :return: the number of messages that are in the chat
        """
        total_message_amount = 0
        with self.database_lock:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    total_message_amount
                FROM
                    chat_message_amount
                WHERE
                    chat_identifier =(?)
                """, (chat_identifier,))
            stored_amount = cursor.fetchone()
            # if the query returns None then the value was not found in the column
            if stored_amount is not None:
                total_message_amount = stored_amount[0]  # returns a 1-tuple
        return total_message_amount
    
    def _increment_total_message_amount(self,
                                        connection: sqlite3.Connection,
                                        chat_identifier: str) -> None:
        """
        Increments the total message amount in the database for the chat with the chat identifier.
        :param chat_identifier: the chat identifier
        :return: None
        """
        sql_cmd = """
                INSERT
                    INTO chat_message_amount
                        (chat_identifier, total_message_amount)
                    VALUES
                        ((?), 1)
                ON CONFLICT
                    (chat_identifier)
                DO UPDATE SET
                    total_message_amount=total_message_amount+1
        """
        cursor = connection.cursor()
        with self.database_lock:
            cursor.execute(sql_cmd, (chat_identifier,))
        connection.commit()

    def add_chat_message_to_database(self,
                                     connection: sqlite3.Connection,
                                     message: protocol.Message) -> None:
        """
        Stores a chat message in the database.
        
        :param connection:
        :param message: the message that should be saved
        :return: None
        """
        if not protocol.valid_content_format(message) or \
                not protocol.valid_receiver_format(message) or\
                not protocol.valid_sender_format(message):
            # TODO: log error
            print("Message not added to database, incorrect format, message:",
                  message)
            return
        
        msg = message.content
        sender = message.sender
        receiver = message.receiver
        
        chat_id = create_chat_identifier(sender, receiver)
        # + 1 so that messages identifier match the queries
        msg_number = self.total_message_amount(connection, chat_id) + 1
        msg_id = create_message_identifier(chat_id, msg_number)
        self._add_chat_message_row(connection, msg_id, msg, sender)
        self._increment_total_message_amount(connection, chat_id)


    def _setup_chat_message_amount_table(self, cursor: sqlite3.Cursor) -> None:
        """
        Create a new chat message amount table with chat_identifier as primary key
        
        Does not commit the change to the database.
        Is not thread safe.
        :param cursor: cursor from the connection of sqlite3 database
        :return: None
        """
        # with self.database_lock:
        cursor.execute(
            """CREATE TABLE chat_message_amount
            (chat_identifier VARCHAR PRIMARY KEY NOT NULL,
            total_message_amount INTEGER)""")
        return
    
    def _setup_chat_messages_table(self, cursor: sqlite3.Cursor) -> None:
        """
        Create a new message table with message_identifier as primary key
        
        Does not commit the change to the database.
        Is not thread safe.
        :param cursor: cursor from the connection of sqlite3 database
        :return: None
        """
        # with self.database_lock:
        cursor.execute(
            """CREATE TABLE chat_messages
            (message_identifier VARCHAR PRIMARY KEY NOT NULL ,
            message VARCHAR,
            sender VARCHAR)""")
        return


def create_chat_identifier(first_user: str, second_user: str) -> str:
    """
    Creates chat identifier by sorting the users according to the value of the string and concatenating.
    
    Returns a string in the format '<smaller_user_name>:<bigger_user_name>'.
    
    :param first_user: user name of first user
    :param second_user: user name of second user
    :return: the chat identifier for the users chat
    """
    (smaller, bigger) = (first_user, second_user) \
        if first_user < second_user \
        else (second_user, first_user)
    combined = "{}:{}".format(smaller, bigger)
    return combined


def create_message_identifier(chat_identifier: str,
                              message_number: int) -> str:
    """
    Creates a message identifier.
    
    :param chat_identifier: the chats identifier
    :param message_number: the message number
    :return: a message identifier
    """
    msg_id = "{}:{}".format(chat_identifier, message_number)
    return msg_id


def table_row_to_msg(row: typing.Tuple[str, str, str]) -> protocol.Message:
    message_identifier = row[0]
    content = row[1]
    sender = row[2]
    first_user, second_user = message_identifier.split(":")[:2]
    if first_user != sender:
        receiver = first_user
    else:
        receiver = second_user
    
    message = protocol.Message(protocol.Message.CHAT_MESSAGE,
                      content,
                      sender,
                      receiver)
    return message


class NotPresentInDatabase(Exception):
    pass
