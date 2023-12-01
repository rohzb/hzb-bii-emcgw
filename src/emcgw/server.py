import socket
from .logger import logger
import logging
import ipaddress
from .connection_handler import ConnectionHandler
from typing import List, Union

class AccessList:
    def __init__(self, clients: Union[List[str], 'AccessList'] = None) -> None:
        """
        Initialize an AccessList instance.

        Args:
            clients (list or AccessList): Optional list of client specifications or an existing AccessList instance.

        Example client lists:
        - ["192.168.1.1", "192.168.2.0/24", "example.com"]
        - ["10.0.0.0/8"]
        """
        if isinstance(clients, AccessList):
            self.clients = clients.clients.copy()
        elif isinstance(clients, list):
            self.clients = self.parse_clients(clients)
        elif clients is None:
            self.clients = set()

    def parse_clients(self, client_list: List[str]) -> set:
        """
        Parse and validate a list of client specifications.

        Args:
            client_list (list): List of client specifications.

        Returns:
            set: A set of valid client representations (IP addresses or networks).
        """
        parsed_clients = set()
        for client_spec in client_list:
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

    def __contains__(self, client_address: str) -> bool:
        """
        Check if a client's IP address is in the current access list.

        Args:
            client_address (str): The client's IP address.

        Returns:
            bool: True if the client is allowed, False otherwise.
        """
        try:
            client_ip = ipaddress.IPv4Address(client_address)
            for client in self.clients:
                if isinstance(client, ipaddress.IPv4Network) and client_ip in client:
                    return True
                elif client_ip == client:
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
    def __init__(self, local_host, local_port, remote_host, remote_port, allowed_clients=None, denied_clients=None, access_order="allow_first"):
        """
        Initialize a Server instance.

        Args:
            local_host (str): The host to listen on.
            local_port (int): The port to bind to.
            remote_host (str): The target host to connect to.
            remote_port (int): The target port to connect to.
            allowed_clients (list): Optional list of allowed client IP addresses.
            denied_clients (list): Optional list of denied client IP addresses.
            access_order (str): The order in which access control is applied ("allow-first" or "deny-first").
        """
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.allowed_clients = AccessList(clients=allowed_clients)
        self.denied_clients = AccessList(clients=denied_clients)
        self.access_order = access_order

    def is_client_allowed(self, client_address):
        """
        Check if the client's IP address is allowed based on the access lists and access order.

        Args:
            client_address (str): The client's IP address.

        Returns:
            Tuple[bool, str]: A tuple of two values:
                - The first element indicates if the client is allowed (True/False).
                - The second element is a string indicating the reason to deny the client (empty if allowed).
        """
        if not self.allowed_clients and not self.denied_clients:
            return True, ""

        allowed = client_address in self.allowed_clients
        denied = client_address in self.denied_clients

        if self.access_order == "deny-first":
            if denied:
                return False, "Client is in the deny list."
            return True, "" if allowed else "Client is not in the access list."
        elif self.access_order == "allow-first":
            if allowed:
                return True, ""
            return False, "Client is not in the access list." if denied else ""

        return False, "Invalid access order."

    def start(self):
        """
        Start the server, listen for incoming connections, and handle data transfer.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.local_host, self.local_port))
        except socket.error as e:
            logging.error(f"Failed to bind to {self.local_host}:{self.local_port} - {e}")
            server_socket.close()
            return

        server_socket.listen(0x40)
        logger.info(f"Server started on {self.local_host}:{self.local_port}")
        logger.info(f"Connect to {self.local_host}:{self.local_port} to access {self.remote_host}:{self.remote_port}")

        while True:
            src_socket, src_address = server_socket.accept()

            # Check if the client is allowed
            is_allowed, denial_reason = self.is_client_allowed(src_address[0])

            if not is_allowed:
                # Log the reason for denial
                logger.warning(f"Connection from {src_address[0]} denied: {denial_reason}")

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
