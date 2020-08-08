# message.py
class InvalidMessageFormatError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class Message:
    """
    A class that represents a message that is sent between a client and server.
    
    Message specifications by message msg_type:
        TYPE_CHAT_MESSAGE
            * content:      non-empty string, the chat message
            * sender:       non-empty string
            * receiver:     non-empty string
        TYPE_REQUEST_NEW_MESSAGES
            * content:      non-empty string, id of last number received
            * sender:       non-empty string
            * receiver:     non-empty string
    
    Attributes
        TYPE_CHAT_MESSAGE -- message msg_type used when message is a chat message
        TYPE_REQUEST_NEW_MESSAGES -- message msg_type used when requesting new
                                     messages that are available on server.
    
    """
    TYPE_CHAT_MESSAGE = 0
    TYPE_REQUEST_NEW_MESSAGES = 1
    TYPE_NEW_MESSAGES = 2
    
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
        self.content = content
        self.sender = sender
        self.receiver = receiver
        
        if msg_type is Message.TYPE_CHAT_MESSAGE and content == "":
            raise InvalidMessageFormatError("Chat message text is missing.")

    def __str__(self):
        str_rep = '{{"msg_type": "{msg_type}", "content": "{content}", ' \
                  '"sender": "{sender}", "receiver": "{receiver}"}}'
        return str_rep.format(msg_type=self.msg_type,
                              content=self.content,
                              sender=self.sender,
                              receiver=self.receiver)
