import socket
import logging
from .connection_handler import ConnectionHandler

class Server:
    """
    Represents a server that listens on a given port and forwards connections to a remote host and port.
    """
    def __init__(self, local_host, local_port, remote_host, remote_port, access_list=None):
        """
        Initialize a Server instance.

        Args:
            local_host (str): The host to listen on.
            local_port (int): The port to bind to.
            remote_host (str): The target host to connect to.
            remote_port (int): The target port to connect to.
            access_list (list): Optional list of allowed client IP addresses.
        """
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.access_list = access_list

    def is_client_allowed(self, client_address):
        """
        Check if the client's IP address is allowed based on the access list.

        Args:
            client_address (str): The client's IP address.

        Returns:
            bool: True if the client is allowed, False otherwise.
        """
        if not self.access_list:
            return True  # No access list, allow all clients

        return client_address in self.access_list

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

            if not self.is_client_allowed(src_address[0]):
                logging.warning(f"Connection from {src_address[0]} denied (not in access list).")
                src_socket.close()
                continue

            logging.info(f"[Establishing connection] {src_address[0]} -> {self.local_host}:{self.local_port} -> ? -> {self.remote_host}:{self.remote_port}")

            try:
                dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dst_socket.connect((self.remote_host, self.remote_port))
                logging.info(f"[OK] {src_address[0]} -> {self.local_host}:{self.local_port} -> {dst_socket.getsockname()} -> {self.remote_host}:{self.remote_port}")

                connection_handler = ConnectionHandler(src_socket, dst_socket)
                connection_handler.start_transfer()
            except Exception as e:
                logging.error(repr(e))
