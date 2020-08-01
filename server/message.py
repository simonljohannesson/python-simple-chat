# message.py
class InvalidMessageFormatError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class Message:
    """
    A class that represents a message that is sent between a client and server.
    
    Message specifications by message type:
        TYPE_CHAT_MESSAGE
            * content:      non-empty string, the chat message
            * sender:       non-empty string
            * receiver:     non-empty string
        TYPE_REQUEST_NEW_MESSAGES
            * content:      non-empty string, id of last number received
            * sender:       non-empty string
            * receiver:     non-empty string
    
    Attributes:
        TYPE_CHAT_MESSAGE -- message type used when message is a chat message
        TYPE_REQUEST_NEW_MESSAGES -- message type used when requesting new
                                     messages that are available on server.
    
    """
    TYPE_CHAT_MESSAGE = 0
    TYPE_REQUEST_NEW_MESSAGES = 1
    
    def __init__(self, msg_type: int,
                 content="",
                 sender="",
                 receiver=""):
        """
        Initializes a Message object.
        
        :raises InvalidMessageFormatError: Exception is raised when the message
            has an incorrect format.
        :param msg_type: type of message
        :param content: content of the message
        :param sender: name of sender
        :param receiver: name of receiver
        """
        self.json_header = dict()
        self.msg_content = dict()
        
        if msg_type is Message.TYPE_CHAT_MESSAGE and content == "":
            raise InvalidMessageFormatError("Chat message text is missing.")
        
        self.msg_content["type"] = str(msg_type)
        self.msg_content["content"] = content
        self.msg_content["sender"] = sender
        self.msg_content["receiver"] = receiver
