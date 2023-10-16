import socket
from .logger import logger
import ipaddress
from .connection_handler import ConnectionHandler
from typing import List, Union


class AccessList:
    def __init__(self, allowed_clients: Union[List[str], 'AccessList'] = None) -> None:
        """
        Initialize an AccessList instance.

        Args:
            allowed_clients (list or AccessList): Optional list of allowed client specifications or an existing
            AccessList instance.

        Example allowed_clients lists:
        - ["192.168.1.1", "192.168.2.0/24", "example.com"]
        - ["10.0.0.0/8"]
        """
        if isinstance(allowed_clients, AccessList):
            self.allowed_clients = allowed_clients.allowed_clients.copy()
        elif isinstance(allowed_clients, list):
            self.allowed_clients = self.parse_allowed_clients(allowed_clients)
        elif allowed_clients is None:
            self.allowed_clients = set()

    def parse_allowed_clients(self, allowed_clients: List[str]) -> set:
        parsed_clients = set()
        for client_spec in allowed_clients:
            try:
                # Check if it's an IP address
                ip = ipaddress.IPv4Address(client_spec)
                parsed_clients.add(ip)
            except ipaddress.AddressValueError:
                try:
                    # Check if it's a network
                    network = ipaddress.IPv4Network(client_spec, strict=False)
                    parsed_clients.add(network)
                except ipaddress.NetmaskValueError:
                    # It might be a hostname or an invalid entry
                    # Log a warning for an invalid client spec
                    logger.warning(f"Invalid client spec: {client_spec}")
        return parsed_clients

    def is_allowed(self, client_address: str) -> bool:
        try:
            client_ip = ipaddress.IPv4Address(client_address)
            for allowed in self.allowed_clients:
                if isinstance(allowed, ipaddress.IPv4Network) and client_ip in allowed:
                    return True
                elif client_ip == allowed:
                    return True
            return False
        except ipaddress.AddressValueError:
            # Log a warning for an invalid client address
            logger.warning(f"Invalid client address: {client_address}")
            return False

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
        #self.access_list = access_list
        self.access_list = AccessList(allowed_clients=access_list)

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

        #return client_address in self.access_list
        return self.access_list.is_allowed(client_address)

    def start(self):
        """
        Start the server, listen for incoming connections, and handle data transfer.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.local_host, self.local_port))
        server_socket.listen(0x40)
        logger.info(f"Server started on {self.local_host}:{self.local_port}")
        logger.info(f"Connect to {self.local_host}:{self.local_port} to access {self.remote_host}:{self.remote_port}")

        while True:
            src_socket, src_address = server_socket.accept()

            if not self.is_client_allowed(src_address[0]):
                logger.warning(f"Connection from {src_address[0]} denied (not in access list).")
                src_socket.close()
                continue

            logger.info(f"[Establishing connection] {src_address[0]} -> {self.local_host}:{self.local_port} -> ? -> {self.remote_host}:{self.remote_port}")

            try:
                dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dst_socket.connect((self.remote_host, self.remote_port))
                logger.info(f"[OK] {src_address[0]} -> {self.local_host}:{self.local_port} -> {dst_socket.getsockname()} -> {self.remote_host}:{self.remote_port}")

                connection_handler = ConnectionHandler(src_socket, dst_socket)
                connection_handler.start_transfer()
            except Exception as e:
                logger.error(repr(e))
