# database_handler.py
import sqlite3
from string import ascii_letters
from random import randint
from typing import Tuple
from threading import Lock

#TODO: add documentation for: database configuration/function, functions and the lock

class DatabaseHandler:
    # TODO: make sure that this works as intended
    database_lock = Lock()


class NotPresentInDatabase(Exception):
    pass


def setup_ram_sqlite_db() -> sqlite3.Connection:
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


def insert_new_row_in_chat_messages_tbl(connection: sqlite3.Connection,
                                        message_identifier: str,
                                        message: str,
                                        sender: str):
    cursor = connection.cursor()
    with DatabaseHandler.database_lock:
        cursor.execute(
            "INSERT INTO chat_messages values (?, ?, ?)",
            (message_identifier, message, sender))
        connection.commit()


def request_specific_chat_message(connection: sqlite3.Connection,
                                  first_user: str,
                                  second_user: str,
                                  total_messages: int) -> Tuple[str, str, str]:
    """
    Throws NotPresentInDatabase exception.
    
    :raises NotPresentInDatabase: Raised when the specified message does not
                                  exist in the database.
    :param connection:
    :param first_user:
    :param second_user:
    :param total_messages:
    :return:
    """
    chat_id = create_chat_identifier(first_user, second_user)
    msg_id = create_message_identifier(chat_id, total_messages)
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


def query_total_message_amount(connection: sqlite3.Connection,
                               chat_identifier: str) -> int():
    # chat_name = create_chat_identifier(first_user, second_user)
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
    

def increment_total_message_amount(connection: sqlite3.Connection,
                                   chat_identifier: str):
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


def create_chat_identifier(first_user: str, second_user: str) -> str:
    """
    Sorts the users according to the value of the string.
    
    Returns a string in the format '<smaller_user_name>:<bigger_user_name>'.
    
    :param first_user:
    :param second_user:
    :return:
    """
    (smaller, bigger) = (first_user, second_user) \
        if first_user < second_user \
        else (second_user, first_user)
    combined = "{}:{}".format(smaller, bigger)
    return combined


def store_message(connection: sqlite3.Connection,
                  sender: str,
                  receiver: str,
                  message: str):
    chat_id = create_chat_identifier(sender, receiver)
    msg_number = query_total_message_amount(connection, chat_id)
    msg_id = create_message_identifier(chat_id, msg_number)
    insert_new_row_in_chat_messages_tbl(connection, msg_id, message, sender)
    increment_total_message_amount(connection, chat_id)


def create_message_identifier(chat_identifier: str, message_number: int) -> str:
    msg_id = "{}:{}".format(chat_identifier, message_number)
    return msg_id


# ============================== TESTING =======================================
def add_stuff_to_chat_messages_table_to_test(connection: sqlite3.Connection):
    # create some strings to add
    col_1 = "user1:user2:"
    col_2 = ""
    col_3 = "user"
    alphabet_length = len(ascii_letters)
    
    for i in range(50):
        col_1 = col_1[:12] + str(i)
        col_2 = ascii_letters[randint(0, alphabet_length - 1)] \
                + ascii_letters[randint(0, alphabet_length - 1)] \
                + ascii_letters[randint(0, alphabet_length - 1)] \
                + ascii_letters[randint(0, alphabet_length - 1)]
        col_3 = col_3[:4] + str(randint(1,2))
        insert_new_row_in_chat_messages_tbl(connection, col_1, col_2, col_3)


def dump_data_in_chat_messages_table(connection: sqlite3.Connection):
    cursor = connection.cursor()
    rows = []
    with DatabaseHandler.database_lock:
        cursor.execute("SELECT * FROM chat_messages")
        rows = cursor.fetchall()
    print("-----------\t\tData in 'chat_messages':\t\t\t-----------")
    for row in rows:
        print(row)
    print("-----------\t\tEO data in 'chat_messages'\t\t\t-----------")
    a = 0
    for i in range(1000):
        a = i


def dump_data_in_chat_messages_amount_table(connection: sqlite3.Connection):
    cursor = connection.cursor()
    rows = []
    with DatabaseHandler.database_lock:
        cursor.execute("SELECT * FROM chat_message_amount")
        rows = cursor.fetchall()
    print("-----------\t\tData in 'chat_message_amount':\t\t-----------")
    for row in rows:
        print(row)
    print("-----------\t\tEO data in 'chat_message_amount'\t-----------")
    a = 0
    for i in range(1000):
        a = i


def test_suite_1(connection: sqlite3.Connection):
    a = "mickey mouse"
    b = "donald duck"
    
    message1 = "hi there buddy! -mm"
    message2 = "hello there friend! -dd"
    message3 = "whats up?! -mm"
    message4 = "not much you????! --dd"
    message5 = "nm either, gonna see what minnie is doing, bye!! --mm"
    message6 = "cool, yeah ill go bother my uncle i guess, see ya!! --dd"
    
    dump_data_in_chat_messages_amount_table(connection)
    dump_data_in_chat_messages_table(connection)

    store_message(connection, a, b, message1)
    store_message(connection, b, a, message2)
    store_message(connection, a, b, message3)
    store_message(connection, b, a, message4)
    store_message(connection, a, b, message5)
    store_message(connection, b, a, message6)

    dump_data_in_chat_messages_table(connection)
    dump_data_in_chat_messages_amount_table(connection)
    
    
if __name__ == '__main__':
    conn = setup_ram_sqlite_db()
    test_suite_1(conn)
    # add_stuff_to_chat_messages_table_to_test(conn)
    # dump_data_in_chat_messages_table(conn)
    # dump_data_in_chat_messages_amount_table(conn)
    #
    #
    #
    #
    # roww = request_specific_chat_message(conn, "user2", "user1", 21)
    # print("Found row: {}".format(roww))
    #
    # print("new round of testing")
    # print("Number of messages: {}".format(query_total_message_amount(
    #     conn,
    #     create_chat_identifier("user3", "user1"))))
    #
    # chat_id_outer_scope = create_chat_identifier("user1", "user3")
    # increment_total_message_amount(conn, chat_id_outer_scope)
    # increment_total_message_amount(conn, chat_id_outer_scope)
    # increment_total_message_amount(conn, chat_id_outer_scope)
    #
    # dump_data_in_chat_messages_amount_table(conn)
    # print("Number of messages: {}".format(query_total_message_amount(
    #     conn,
    #     create_chat_identifier("user3", "user1"))))
    #
    # print(create_message_identifier(create_chat_identifier("user1", "user3"), 6))
    
    conn.close()
