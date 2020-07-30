# message.py
from __future__ import annotations
from typing import Dict
import json
import sys


class Message:
    """
    Representation of a message with three parts.
    
    1. Fixed length header
        - Contains an integer the size of two bytes, that denotes the size of
          the variable length header.
        - Has network/big-endian byteorder
    
    2. Variable length header
        - Is made up of a dictionary containing the following key value pairs:
            * "length" : str
            * "type" : str
            * "encoding" : str
            * "byteorder" : str
        - Is encoded in UTF-8
    
    3. Message content
        - Dictionary containing key value pairs in format str : str.
    """
    def __init__(self, msg_content):
        self.json_header = dict()
        # self.json_header["type"] = msg_type
        self.msg_content = msg_content

    def serialize_message(self, encoding) -> bytes:
        # message content
        msg_content_serialized = json.dumps(self.msg_content).encode(encoding)
        # json header
        self.json_header["byteorder"] = sys.byteorder
        self.json_header["encoding"] = encoding
        self.json_header["length"] = str(len(msg_content_serialized))
        json_header_serialized = json.dumps(self.json_header).encode("UTF-8")
        # fixed length header
        msg_length = len(msg_content_serialized + json_header_serialized)
        serialized_message = \
            msg_length.to_bytes(2, byteorder=sys.byteorder)\
            + json_header_serialized \
            + msg_content_serialized
        return serialized_message

    def deserialize(self, serialized_msg: str) -> Message:
        raise NotImplementedError

    def check_message_structure_valid(self) -> bool:
        raise NotImplementedError
        

def deserialize_fix_len_head(serialized_fix_len_head: bytes) -> int:
    """
    Deserialize a fixed length header in big endian byteorder.
    
    Caller should make sure that the length of the header is correct when
    calling the function.
    
    TODO: break out to a message handler class?
    TODO: error handling, perhaps if incorrect format just ignore
          and flush and close socket?
    :param serialized_fix_len_head:
    :return:
    """
    length = int.from_bytes(serialized_fix_len_head, "big")
    return length


def deserialize_var_len_head(serialized_var_len_head: bytes):
    """
    Deserialize a variable length header encoded in UTF-8
    
    Caller should make sure that the length of the header is correct when
    calling the function.
    
    TODO: error handling loads, perhaps if incorrect format just ignore?
    :param serialized_var_len_head:
    :return:
    """
    json_header = json.loads(serialized_var_len_head)
    return json_header


def deserialize_content(serialized_content: bytes):
    msg_content = json.loads(serialized_content)
    return msg_content


