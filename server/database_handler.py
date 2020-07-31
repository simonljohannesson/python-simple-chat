# database_handler.py
import sqlite3
from string import ascii_letters
from random import randint
from typing import Tuple
from threading import Lock


class DatabaseHandler:
    database_lock = Lock()


def setup_ram_sqlite_db() -> sqlite3.Connection:
    # create an sqlite database in ram
    conn = sqlite3.connect(":memory:")
    # create a cursor to the database
    cursor = conn.cursor()
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
        conn.commit()
    return conn


def store_chat_message(connection: sqlite3.Connection,
                       message_identifier: str,
                       message: str, sender: str):
    cursor = connection.cursor()
    with DatabaseHandler.database_lock:
        cursor.execute(
            "INSERT INTO chat_messages values (?, ?, ?)",
            (message_identifier, message, sender))
        connection.commit()


def query_chat_message(connection: sqlite3.Connection,
                            first_user: str,
                            second_user: str,
                            total_messages: int) -> Tuple[str, str, str]:
    chat_identifier = sort_and_combine_users(first_user, second_user) + ":" + str(total_messages)
    
    cursor = connection.cursor()
    row = ()
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
            (chat_identifier,))
        row = cursor.fetchone()
    return row


def query_total_message_amount(connection: sqlite3.Connection,
                               first_user: str,
                               second_user: str) -> int():
    chat_name = sort_and_combine_users(first_user, second_user)
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
            """, (chat_name,))
        stored_amount = cursor.fetchone()
        # if the query returns None then the value was not found in the column
        if stored_amount is not None:
            total_message_amount = stored_amount[0]  # returns a 1-tuple
    return total_message_amount
    

def increment_total_message_amount(connection: sqlite3.Connection,
                                   first_user: str,
                                   second_user: str):
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
    chat_name = sort_and_combine_users(first_user, second_user)
    cursor = connection.cursor()
    with DatabaseHandler.database_lock:
        cursor.execute(sql_cmd, (chat_name,))


def sort_and_combine_users(first_user: str, second_user: str) -> str:
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


















# ============================== TESTING =======================================


def add_stuff_to_chat_messages_table_to_test(connection: sqlite3.Connection):
    # create some strings to add
    col_1 = "user1:user2:"
    col_2 = ""
    col_3 = "user"
    alphabet_length = len(ascii_letters)
    
    for i in range(1000):
        col_1 = col_1[:12] + str(i)
        col_2 = ascii_letters[randint(0, alphabet_length - 1)] \
                + ascii_letters[randint(0, alphabet_length - 1)] \
                + ascii_letters[randint(0, alphabet_length - 1)] \
                + ascii_letters[randint(0, alphabet_length - 1)]
        col_3 = col_3[:4] + str(randint(1,2))
        store_chat_message(connection, col_1, col_2, col_3)


def dump_data_in_chat_messages_table(connection: sqlite3.Connection):
    cursor = connection.cursor()
    rows = []
    with DatabaseHandler.database_lock:
        cursor.execute("SELECT * FROM chat_messages")
        rows = cursor.fetchall()
    print("Data in 'chat_messages':")
    for row in rows:
        print(row)
    print("EO data in 'chat_messages'")
    a = 0
    for i in range(1000):
        a = i


def dump_data_in_chat_messages_amount_table(connection: sqlite3.Connection):
    cursor = connection.cursor()
    rows = []
    with DatabaseHandler.database_lock:
        cursor.execute("SELECT * FROM chat_message_amount")
        rows = cursor.fetchall()
    print("Data in 'chat_message_amount':")
    for row in rows:
        print(row)
    print("EO data in 'chat_message_amount'")
    a = 0
    for i in range(1000):
        a = i







if __name__ == '__main__':
    connection = setup_ram_sqlite_db()
    
    add_stuff_to_chat_messages_table_to_test(connection)
    dump_data_in_chat_messages_table(connection)
    dump_data_in_chat_messages_amount_table(connection)

    
    
    
    roww = query_chat_message(connection, "user2", "user1", 921)
    print("Found row: {}".format(roww))
    
    print("new round of testing")
    print("Number of messages: {}".format(query_total_message_amount(connection, "user3", "user1")))
    
    increment_total_message_amount(connection, "user1", "user3")
    increment_total_message_amount(connection, "user1", "user3")
    increment_total_message_amount(connection, "user1", "user3")
    increment_total_message_amount(connection, "user1", "user3")
    dump_data_in_chat_messages_amount_table(connection)
    print("Number of messages: {}".format(query_total_message_amount(connection, "user3", "user1")))

    
    connection.close()