import socket
import logging
from .connection_handler import ConnectionHandler
import ipaddress

class AccessList:
    def __init__(self, allowed_clients=None):
        """
        Initialize an AccessList instance.

        Args:
            allowed_clients (list): Optional list of allowed client specifications. Client specifications can include
            individual IPs, IP ranges (in CIDR notation), or hostnames.

        Example allowed_clients lists:
        - ["192.168.1.1", "192.168.2.0/24", "example.com"]
        - ["10.0.0.0/8"]
        """
        self.allowed_clients = self.parse_allowed_clients(allowed_clients)

    def parse_allowed_clients(self, allowed_clients):
        """
        Parse allowed client specifications and store them as network objects.

        Args:
            allowed_clients (list): List of client specifications, which can include individual IPs, IP ranges, or hostnames.

        Returns:
            list: List of IP network objects (ipaddress.IPv4Network or ipaddress.IPv6Network).
        """
        parsed_clients = []

        if allowed_clients is None:
            return parsed_clients

        for client_spec in allowed_clients:
            if '/' in client_spec:  # Assuming CIDR notation
                try:
                    network = ipaddress.ip_network(client_spec, strict=False)
                    parsed_clients.append(network)
                except ValueError:
                    # Invalid CIDR notation, log a warning
                    logging.warning(f"Invalid CIDR notation: {client_spec}")
            else:
                try:
                    address = ipaddress.ip_address(client_spec)
                    # Add the network corresponding to the single IP address
                    parsed_clients.append(ipaddress.ip_network(address))
                except ValueError:
                    # Client specification is not a valid IP address, assuming it's a hostname
                    try:
                        ip_address = ipaddress.ip_network(socket.gethostbyname(client_spec))
                        parsed_clients.append(ip_address)
                    except (socket.gaierror, ValueError):
                        # Invalid hostname or IP address, log a warning
                        logging.warning(f"Cannot parse client specification: {client_spec}")

        return parsed_clients

    def is_client_allowed(self, client_address):
        """
        Check if the client's IP address is allowed based on the access list.

        Args:
            client_address (str): The client's IP address.

        Returns:
            bool: True if the client is allowed, False otherwise.
        """
        ip_address = ipaddress.ip_address(client_address)

        for allowed_network in self.allowed_clients:
            if ip_address in allowed_network:
                return True

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
        return self.access_list.is_client_allowed(client_address)

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
