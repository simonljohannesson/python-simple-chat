#client_thread.py


import threading
import socket
import server.message


class ClientThread(threading.Thread):
    """
    Class used to dispatch threads that handles client connections.

    Attributes:
        self.client_socket (socket): The socket used to connect to client.
    """
    def __init__(self, client_socket: socket.socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
    
    def run(self):
        received_message = self._receive_client_message()
        print(received_message.msg_content)
        # if not received_message.check_message_structure_valid():
        #     return
        # self._act_on_message(received_message)
        
    def _receive_client_message(self) -> server.message.Message:
        """Handles the connection with the client socket.
        TODO: could send information by having a listener or reference to msg parser
        TODO: refactor to something slightly more clever
        """
        bytes_rcvd_count = 0
        fix_header = 0
        var_header = None
        msg_content = None
        bytes_rcvd = b''
        with self.client_socket as s:
            # get fixed header of message
            while bytes_rcvd_count < 2:
                data = s.recv(2)
                if not data:
                    break                       # TODO: throw exception?
                bytes_rcvd_count += len(data)
                bytes_rcvd += data
            fix_header = server.message.deserialize_fix_len_head(bytes_rcvd[:2])
            bytes_rcvd = bytes_rcvd[2:]
            bytes_rcvd_count = len(bytes_rcvd)
            
            # get variable header of message
            var_header_length = fix_header
            while bytes_rcvd_count < var_header_length:
                data = s.recv(32)
                if not data:
                    break                       # TODO: throw exception?
                bytes_rcvd_count += len(data)
                bytes_rcvd += data
            var_header = server.message.deserialize_var_len_head(bytes_rcvd[:fix_header])
            bytes_rcvd = bytes_rcvd[fix_header:]
            bytes_rcvd_count = len(bytes_rcvd)
            
            # get message content
            msg_content_length = int(var_header["length"])
            while bytes_rcvd_count < msg_content_length:
                data = s.recv(32)
                if not data:
                    break                       # TODO: throw exception?
                bytes_rcvd_count += len(data)
                bytes_rcvd += data
            msg_content = server.message.deserialize_content(bytes_rcvd[:msg_content_length])
            return server.message.Message(msg_content)
        # does this connection need to stay open in order to send back information?
        
    def _act_on_message(self, message: server.message.Message):
        # call database handler with the appropriate function
        raise NotImplementedError
