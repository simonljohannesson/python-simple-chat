# database_handler.py
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
from typing import Tuple
from threading import Lock
from chat_helper_lib.message import Message

#TODO: add documentation for: database configuration/function, functions and the lock

class DatabaseHandler:
    # TODO: make sure that this works as intended
    database_lock = Lock()


class NotPresentInDatabase(Exception):
    pass


def setup_ram_sqlite_db() -> sqlite3.Connection:
    """
    Creates an sqlite3 database in RAM with the specifications of the database in the database_handler module.
    :return: the connection to the created database
    """
    # create an sqlite database in ram
    connection = sqlite3.connect(":memory:")
    # create a cursor to the database
    cursor = connection.cursor()
    with DatabaseHandler.database_lock:
        # create a new chat message amount table with chat_identifier as primary key
        cursor.execute(
            """CREATE TABLE chat_message_amount
            (chat_identifier VARCHAR PRIMARY KEY NOT NULL,
            total_message_amount INTEGER)""")
        # create a new message table with message_identifier as primary key
        cursor.execute(
            """CREATE TABLE chat_messages
            (message_identifier VARCHAR PRIMARY KEY NOT NULL ,
            message VARCHAR,
            sender VARCHAR)""")
        connection.commit()
    return connection


def _insert_new_row_in_chat_messages_tbl(connection: sqlite3.Connection,
                                         message_identifier: str,
                                         message: str,
                                         sender: str) -> None:
    """
    Inserts a new row in the chat_messages table.
    
    :param connection: connection to the sqlite3 database
    :param message_identifier: the message identifier in the database
    :param message: message that should be added to the database
    :param sender: sender of the message
    :return: None
    """
    cursor = connection.cursor()
    with DatabaseHandler.database_lock:
        cursor.execute(
            "INSERT INTO chat_messages values (?, ?, ?)",
            (message_identifier, message, sender))
        connection.commit()


def _request_specific_chat_message(connection: sqlite3.Connection,
                                   first_user: str,
                                   second_user: str,
                                   total_messages: int) -> Tuple[str, str, str]:
    """
    Queries the database for a specific chat message.
    
    :raises NotPresentInDatabase: Raised when the specified message does not
                                  exist in the database.
    :param connection: connection to the database
    :param first_user: user name of first user
    :param second_user: user name of second user
    :param total_messages: the number of the requested message
    :return: a tuple of the row containing the specific chat message
    """
    chat_id = _create_chat_identifier(first_user, second_user)
    msg_id = _create_message_identifier(chat_id, total_messages)
    cursor = connection.cursor()
    row = None
    with DatabaseHandler.database_lock:
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
            (msg_id,))
        row = cursor.fetchone()
    if row is None:
        raise NotPresentInDatabase
    return row


def _query_total_message_amount(connection: sqlite3.Connection,
                                chat_identifier: str) -> int:
    """
    Queries the database how many messages are saved to the chat_identifiers chat.
    
    If the chat_identifier is not found in the database the return value will be 0.
    :param connection: connection to the database
    :param chat_identifier: the chats identifier
    :return: the number of messages that are in the chat
    """
    total_message_amount = 0
    with DatabaseHandler.database_lock:
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
    

def _increment_total_message_amount(connection: sqlite3.Connection,
                                    chat_identifier: str) -> None:
    """
    Increments the total message amount in the database for the chat with the chat identifier.
    :param connection: the connection to the database
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
    with DatabaseHandler.database_lock:
        cursor.execute(sql_cmd, (chat_identifier,))


def _create_chat_identifier(first_user: str, second_user: str) -> str:
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


def add_chat_message_to_database(connection: sqlite3.Connection,
                                 message: Message) -> None:
    """
    Stores a chat message in the database.
    
    :param connection: the connection to the database
    :param message: the message that should be saved
    :return: None
    """
    msg = message.content
    sender = message.sender
    receiver = message.receiver
    
    chat_id = _create_chat_identifier(sender, receiver)
    msg_number = _query_total_message_amount(connection, chat_id)
    msg_id = _create_message_identifier(chat_id, msg_number)
    _insert_new_row_in_chat_messages_tbl(connection, msg_id, msg, sender)
    _increment_total_message_amount(connection, chat_id)


def _create_message_identifier(chat_identifier: str,
                               message_number: int) -> str:
    """
    Creates a message identifier.
    
    :param chat_identifier: the chats identifier
    :param message_number: the message number
    :return: a message identifier
    """
    msg_id = "{}:{}".format(chat_identifier, message_number)
    return msg_id
