# protocol.py
"""The purpose of this module is to handle the serialization and deserialization
of a Message object, and it is designed to do so while complying with the below
specification of a serialized message.

Specification of a serialized message.
    A serialized message shall be composed of two parts, (1) a fixed length
    header and (2) the message. There shall be nothing between the parts.
    
    The message (2) cannot be longer than 2^16 bytes since that is the biggest
    number that the fixed length header can represent.
    
    1. Fixed length header
        * An integer that denotes the length of (2) the variable length header.
        * Shall be two bytes long, in big-endian/network byteorder.
    2. The message
        * JSON object
        * Shall contain key "msg_type": non-empty string denoting the message msg_type value.
        * Shall contain key "content", string containing the message content.
        * Is of variable length.
"""
from typing import Dict
import json


class InvalidMessageFormatError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class Message:
    """
    A class that represents a message that is sent between a client and server.
    
    Message specifications by message msg_type:
        CHAT_MESSAGE
            * content:      non-empty string, the chat message
            * sender:       non-empty string
            * receiver:     non-empty string
        REQUEST_NEW_MESSAGES
            * content:      non-empty string, id of last number received
            * sender:       non-empty string
            * receiver:     non-empty string
        TODO: NEW_MESSAGES
            * content:      non-empty string, a list of serialized messages
    
    Attributes
        CHAT_MESSAGE -- message msg_type used when message is a chat message
        REQUEST_NEW_MESSAGES -- message msg_type used when requesting new
        messages that are available on server\n
        NEW_MESSAGES -- message msg_type used when sending new messages from the
        server, sent as a response to type REQUEST_NEW_MESSAGES\n
    """
    CHAT_MESSAGE = 0
    REQUEST_NEW_MESSAGES = 1
    NEW_MESSAGES = 2
    
    def __init__(self, msg_type: int,
                 content="",
                 sender="",
                 receiver=""):
        """
        Initializes a Message object.
        
        :raises InvalidMessageFormatError: Exception is raised when the message
            has an incorrect format.
        :param msg_type: msg_type of message
        :param content: content of the message
        :param sender: name of sender
        :param receiver: name of receiver
        """
        
        self.msg_type = msg_type
        self.content = str(content)
        self.sender = str(sender)
        self.receiver = str(receiver)
        
        if msg_type is Message.CHAT_MESSAGE and content == "":
            raise InvalidMessageFormatError("Chat message text is missing.")
    
    def __str__(self):
        str_rep = '{{"msg_type": "{msg_type}", "content": "{content}", ' \
                  '"sender": "{sender}", "receiver": "{receiver}"}}'
        return str_rep.format(msg_type=self.msg_type,
                              content=self.content,
                              sender=self.sender,
                              receiver=self.receiver)


class ProtocolViolationError(Exception):
    """
    Class signaling that the message protocol was violated.
    """
    def __init__(self, msg: str):
        self.msg = msg


class MessageCorruptError(Exception):
    """
    Class signaling that the message was received in a corrupt format.
    """
    def __init__(self, msg: str):
        self.msg = msg


def serialize_message(message: Message) -> bytes:
    """
    Takes a message and serializes it according to the protocol specification.
    
    :param message: the message that should be serialized
    :return: the serialized message
    """
    encoding = "UTF-8"
    msg_content_serialized = serialize_message_content(message).encode(encoding)
    msg_len = len(msg_content_serialized)
    if msg_len > 2**16:  # max unsigned integer in 2 bytes
        raise ProtocolViolationError("Message is too long.")
    serialized_message = msg_len.to_bytes(2,"big") + msg_content_serialized
    return serialized_message


def serialize_message_content(message) -> str:
    """
    Takes a message and serializes it according to the protocol specification.
    :param message: message to be serialized
    :return: serialized message
    """
    # message content
    message_content = dict()
    message_content["msg_type"] = message.msg_type
    message_content["content"] = message.content
    message_content["sender"] = message.sender
    message_content["receiver"] = message.receiver
    
    msg_content_serialized = json.dumps(message_content)
    return msg_content_serialized


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
    except json.JSONDecodeError:
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
                content=str(content),
                sender=str(sender),
                receiver=str(receiver))
        return reassembled_msg
    except (KeyError, TypeError) as exception:
        raise ProtocolViolationError(error_msg_format)


def valid_sender_format(message: Message) -> bool:
    """
    Checks if the sender of the message is in a valid REQUEST_NEW_MESSAGES format.
    :param message: message with the sender that should be validated
    :return: True if sender is valid, otherwise False
    """
    if type(message.sender) is not str or len(message.sender) == 0:
        return False
    return True


def valid_receiver_format(message: Message) -> bool:
    """
    Checks if the receiver of the message is in a valid REQUEST_NEW_MESSAGES format.
    :param message: message with the receiver that should be validated
    :return: True if receiver is valid, otherwise False
    """
    if type(message.receiver) is not str or len(message.receiver) == 0:
        return False
    return True


def valid_content_format(message: Message) -> bool:
    """
    Checks if the content of the message is in a valid REQUEST_NEW_MESSAGES format.
    :param message: message with the content that should be validated
    :return: True if content is valid, otherwise False
    """
    if type(message.content) is not str or len(message.content) == 0:
        return False
    return True


def validate_request_message_format(message: Message) -> None:
    """
    Validates the format of a message requesting new messages.
    
    :param message: message that should be validated
    :return:
    """
    if not message.msg_type == Message.REQUEST_NEW_MESSAGES or \
            not message.content.isdigit() or \
            not valid_content_format(message) or \
            not valid_sender_format(message) or \
            not valid_receiver_format(message):
        raise MessageCorruptError(
            "Message does not conform to REQUEST_NEW_MESSAGES format," +
            " message:" + str(message))

