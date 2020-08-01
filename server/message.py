# message.py
from __future__ import annotations
from typing import Dict
import json
import sys
from enum import Enum, unique


class InvalidMessageFormatError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class Message:
    # TODO: clean me up a bit!
    """
    A message that can be serialized and that will conform to the application
    message protocol.
    
    
    Representation of a message with three parts.
    
    1. Fixed length header
        - Contains an integer the size of two bytes, that denotes the size of
          the variable length header.
        - Has network/big-endian byteorder
    
    2. JSON header
        - Is made up of a dictionary containing the following key value pairs:
            * "length" : str
            * "encoding" : str  TODO: or not?
            * "byteorder" : str
        - Is encoded in UTF-8
        - Is of variable length, as defined by the fixed length header.
    
    3. Message content
        - Dictionary containing key value pairs in format str : str.
        - Is of variable length, as defined by the "length" parameter in JSON
          header
        - Must contain the key "type".
          * The types available are enumerated in the inner class MessageType.
        - Must contain the key "content"
    """
    # @unique
    # class Type(Enum):
    #     CHAT_MESSAGE = 0
    #     REQUEST_NEW_MESSAGES = 1  # would need to send a "last i have is"
    #
    #     # def
    TYPE_CHAT_MESSAGE = 0
    TYPE_REQUEST_NEW_MESSAGES = 1
    
    def __init__(self, msg_type: Message.Type,
                 chat_message="",
                 sender="",
                 receiver=""):
        self.json_header = dict()
        self.msg_content = dict()
        
        if msg_type is Message.TYPE_CHAT_MESSAGE and chat_message == "":
            raise InvalidMessageFormatError("Chat message text is missing.")
        
        self.msg_content["type"] = str(msg_type)
        self.msg_content["content"] = chat_message
        self.msg_content["sender"] = sender
        self.msg_content["receiver"] = receiver

    # def serialize_message(self, encoding: str) -> bytes:
    #     # message content
    #     msg_content_serialized = json.dumps(self.msg_content).encode(encoding)
    #     # json header
    #     self.json_header["byteorder"] = sys.byteorder
    #     self.json_header["encoding"] = encoding
    #     self.json_header["length"] = str(len(msg_content_serialized))
    #     json_header_serialized = json.dumps(self.json_header).encode("UTF-8")
    #     # fixed length header
    #     msg_length = len(msg_content_serialized + json_header_serialized)
    #     serialized_message = \
    #         msg_length.to_bytes(2, byteorder=sys.byteorder)\
    #         + json_header_serialized \
    #         + msg_content_serialized
    #     return serialized_message

    # def deserialize(self, serialized_msg: str) -> Message:
    #     raise NotImplementedError

    # def check_message_structure_valid(self) -> bool:
    #     raise NotImplementedError
        

# def deserialize_two_byte_header(serialized_fixed_header: bytes) -> int:
#     """
#     Deserialize a two byte long header in big endian byteorder.
#
#     Caller should make sure that the length of the header is correct when
#     calling the function.
#
#     :param serialized_fixed_header:
#     :return:
#     """
#     if len(serialized_fixed_header) != 2:
#         raise ValueError(
#             "Expected a 2 byte value, received a {} byte value.".format(
#                 len(serialized_fixed_header)))
#     length = int.from_bytes(serialized_fixed_header, "big")
#     return length


# def deserialize_json_object(json_object: bytes) -> Dict[str, str]:
#     try:
#         message_dictionary = json.loads(json_object)
#         return message_dictionary
#     except json.JSONDecodeError as exception:
#         raise MessageCorruptError


if __name__ == '__main__':
    print("test")
