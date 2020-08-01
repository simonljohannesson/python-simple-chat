# protocol_handler.py
from server.message import Message
from typing import Dict
import json
import sys


class ProtocolViolationError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class MessageCorruptError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


def serialize_message(message: Message) -> bytes:
    encoding = "UTF-8"
    # message content
    msg_content_serialized = json.dumps(message.msg_content).encode(encoding)
    # json header
    message.json_header["byteorder"] = sys.byteorder
    message.json_header["encoding"] = encoding
    message.json_header["length"] = str(len(msg_content_serialized))
    json_header_serialized = json.dumps(message.json_header).encode("UTF-8")
    # fixed length header
    json_header_length = len(json_header_serialized)
    serialized_message = \
        json_header_length.to_bytes(2, "big") \
        + json_header_serialized \
        + msg_content_serialized
    return serialized_message


def deserialize_two_byte_header(serialized_fixed_header: bytes) -> int:
    """
    Deserialize a two byte long header in big endian byteorder.
    
    Caller should make sure that the length of the header is correct when
    calling the function.
    
    :param serialized_fixed_header:
    :return:
    """
    if len(serialized_fixed_header) != 2:
        raise ValueError(
            "Expected a 2 byte value, received a {} byte value.".format(
                len(serialized_fixed_header)))
    length = int.from_bytes(serialized_fixed_header, "big")
    return length


def deserialize_json_object(json_object: bytes) -> Dict[str, str]:
    try:
        message_dictionary = json.loads(json_object)
        return message_dictionary
    except json.JSONDecodeError as exception:
        raise MessageCorruptError


def reassemble_message(message_content: Dict[str, str]) -> Message:
    try:
        reassembled_msg = Message(
            int(message_content["type"]),  # type should be an integer
            message_content["content"],
            message_content["sender"],
            message_content["receiver"])
        return reassembled_msg
    except (KeyError, TypeError) as exception:
        raise ProtocolViolationError(
            "The format of argument 'message_content' was incorrect.")