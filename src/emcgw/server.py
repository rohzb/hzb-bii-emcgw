import socket
import logging
from .connection_handler import ConnectionHandler

class Server:
    """
    Represents a server that listens on a given port and forwards connections to a remote host and port.
    """
    def __init__(self, local_host, local_port, remote_host, remote_port):
        """
        Initialize a Server instance.

        Args:
            local_host (str): The host to listen on.
            local_port (int): The port to bind to.
            remote_host (str): The target host to connect to.
            remote_port (int): The target port to connect to.
        """
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port

    def start(self):
        """
        Start the server, listen for incoming connections, and handle data transfer.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.local_host, self.local_port))
        server_socket.listen(0x40)
        logging.info(f"Server started on {self.local_host}:{self.local_port}")
        logging.info(f"Connect to {self.local_host}:{self.local_port} to access {self.remote_host}:{self.remote_port}")

        while True:
            src_socket, src_address = server_socket.accept()
            logging.info(f"[Establishing connection] {src_address[0]} -> {self.local_host}:{self.local_port} -> ? -> {self.remote_host}:{self.remote_port}")

            try:
                dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dst_socket.connect((self.remote_host, self.remote_port))
                logging.info(f"[OK] {src_address[0]} -> {self.local_host}:{self.local_port} -> {dst_socket.getsockname()} -> {self.remote_host}:{self.remote_port}")

                connection_handler = ConnectionHandler(src_socket, dst_socket)
                connection_handler.start_transfer()
            except Exception as e:
                logging.error(repr(e))
