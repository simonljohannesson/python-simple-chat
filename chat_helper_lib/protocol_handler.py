# protocol_handler.py
"""The purpose of this module is to handle the serialization and deserialization
of a Message object, and it is designed to do so while complying with the below
specification of a serialized message.

Specification of a serialized message.
    A serialized message shall be composed of three parts, (1) a fixed length
    header, (2) a variable length header and (3) message content. There shall
    be nothing between the parts.
    
    1. Fixed length header
        * An integer that denotes the length of (2) the variable length header.
        * Shall be two bytes long, in big-endian/network byteorder.
    2. Variable length header
        * A JSON object
        * Shall contain key "length": non-empty string denoting the length of (3) the message content.
        * Shall contain key "encoding" : non-empty string containing the encoding of (3) the message content
        * Shall contain key "byteorder" : non-empty string denoting byteorder used encoding (3) the message content.
        * Is encoded in UTF-8
        * Is of variable length.
    3. Message content
        * JSON object
        * Shall contain key "msg_type": non-empty string denoting the message msg_type value.
        * Shall contain key "content", string containing the message content.
        * Is of variable length.
"""
from chat_helper_lib.message import Message
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
    """
    Takes a message and serializes it according to the protocol specification.
    
    :param message: the message that should be serialized
    :return: the serialized message
    """
    encoding = "UTF-8"
    # message content
    message_content = dict()
    message_content["msg_type"] = message.msg_type
    message_content["content"] = message.content
    message_content["sender"] = message.sender
    message_content["receiver"] = message.receiver
    
    msg_content_serialized = json.dumps(message_content).encode(encoding)
    msg_len = len(msg_content_serialized)
    if msg_len > 2**16:  # max unsigned integer in 2 bytes
        raise ProtocolViolationError("Message is too long.")
    serialized_message = msg_len.to_bytes(2,"big") + msg_content_serialized
    return serialized_message


def deserialize_two_byte_header(serialized_fixed_header: bytes) -> int:
    """
    Deserialize a two byte long header in big endian byteorder.
    
    Caller should make sure that the length of the header is correct when
    calling the function.
    
    :param serialized_fixed_header: the two bytes that should be deserialized
    :return: the integer value of the two byte header
    """
    if len(serialized_fixed_header) != 2:
        raise ValueError(
            "Expected a 2 byte value, received a {} byte value.".format(
                len(serialized_fixed_header)))
    length = int.from_bytes(serialized_fixed_header, "big")
    return length


def deserialize_json_object(json_object: bytes) -> Dict[str, str]:
    """
    Deserializes a JSON object.
    
    Is used to deserialize the variable length header or the message content.
    :param json_object: the JSON object that should be deserialized
    :raises ProtocolViolationError: if the object entered is incomplete or has an
    invalid structure
    :return: a python dictionary corresponding to the JSON object
    """
    try:
        message_dictionary = json.loads(json_object)
        return message_dictionary
    except json.JSONDecodeError as exception:
        raise ProtocolViolationError("The JSON-object is not valid.")


def reassemble_message(message_content: Dict[str, str]) -> Message:
    """
    Reassembles message from python dictionary.
     
     The dictionary should be directly received from the function
     deserialize_json_object and not have been altered.
    :param message_content: dictionary used to reassemble message
    :return: a reassembled message as it should have looked before being serialized
    :raises ProtocolViolationError: raised if the dictionary message_content violates the protocol
    """
    error_msg_format = "The format of argument 'message_content' was incorrect."
        
    try:
        msg_type = message_content["msg_type"]
        content = message_content["content"]
        sender = message_content["sender"]
        receiver = message_content["receiver"]
        reassembled_msg = Message(
                msg_type=int(msg_type),  # msg_type should be an integer
                content=content,
                sender=sender,
                receiver=receiver)
        return reassembled_msg
    except (KeyError, TypeError) as exception:
        raise ProtocolViolationError(error_msg_format)


def has_valid_sender_format(message: Message) -> bool:
    if type(message.sender) is not str or len(message.sender) == 0:
        return False
    return True


def has_valid_receiver_format(message: Message) -> bool:
    if type(message.receiver) is not str or len(message.receiver) == 0:
        return False
    return True


def has_valid_content_format(message: Message) -> bool:
    if type(message.content) is not str or len(message.content) == 0:
        return False
    return True
