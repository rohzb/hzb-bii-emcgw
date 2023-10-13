import socket
import threading
import argparse
import logging
import yaml

class ConnectionHandler:
    """
    Handles data transfer between two sockets and logs the data flow.
    """
    def __init__(self, src_socket, dst_socket):
        """
        Initialize a ConnectionHandler instance.

        Args:
            src_socket (socket.socket): The source socket for data transfer.
            dst_socket (socket.socket): The destination socket for data transfer.
        """
        self.src_socket = src_socket
        self.dst_socket = dst_socket

    def handle(self, buffer: bytes, direction: bool) -> bytes:
        """
        Handle data and log the data flow information.

        Args:
            buffer (bytes): The data buffer to handle.
            direction (bool): The direction of data flow (True for outgoing, False for incoming).

        Returns:
            bytes: The processed data buffer.
        """
        src_address, src_port = self.src_socket.getsockname()
        dst_address, dst_port = self.dst_socket.getsockname()

        if direction:
            logging.debug(f"{src_address[0]},{src_port} -> {dst_address[0]},{dst_port} {len(buffer)} bytes")
        else:
            logging.debug(f"{dst_address[0]},{dst_port} <- {src_address[0]},{src_port} {len(buffer)} bytes")

        return buffer

    def start_transfer(self):
        """
        Start data transfer threads for both directions.
        """
        src_address, src_port = self.src_socket.getsockname()
        dst_address, dst_port = self.dst_socket.getsockname()

        s = threading.Thread(target=self.transfer, args=(self.dst_socket, self.src_socket, False))
        r = threading.Thread(target=self.transfer, args=(self.src_socket, self.dst_socket, True))
        s.start()
        r.start()

    def transfer(self, src, dst, direction: bool):
        """
        Transfer data between two sockets in a given direction.

        Args:
            src (socket.socket): The source socket.
            dst (socket.socket): The destination socket.
            direction (bool): The direction of data flow (True for outgoing, False for incoming).
        """
        while True:
            try:
                buffer = src.recv(4096)
                dst.send(self.handle(buffer, direction))
            except Exception as e:
                logging.error(repr(e))
                break
        logging.warning(f"Closing connection {src.getsockname()[0]},{src.getsockname()[1]}!")
        src.close()
        logging.warning(f"Closing connection {dst.getsockname()[0]},{dst.getsockname()[1]}!")
        dst.close()

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

def main():
    """
    Main function to parse command-line arguments, configure logging, and start the server.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to YAML config file")
    parser.add_argument("-l", "--listen-host", help="The host to listen on")
    parser.add_argument("-p", "--listen-port", type=int, help="The port to bind to")
    parser.add_argument("-r", "--connect-host", help="The target host to connect to")
    parser.add_argument("-P", "--connect-port", type=int, help="The target port to connect to")
    parser.add_argument("-L", "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set logging level")
    parser.add_argument("-v", dest="verbosity", action="count", default=0, help="Increase verbosity level (-v for INFO, -vv for DEBUG, -vvv for TRACE)")

    args = parser.parse_args()
    config = {}

    # read optional config file
    if args.config:
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)

    config.update({
        "listen_host": args.listen_host or config.get("listen_host"),
        "listen_port": args.listen_port or config.get("listen_port"),
        "connect_host": args.connect_host or config.get("connect_host"),
        "connect_port": args.connect_port or config.get("connect_port"),
    })

    # Set logging level from command line or config file
    log_level = args.log_level or config.get("log_level", "INFO")
    
    # Adjust logging level based on verbosity
    if args.verbosity == 1:
        log_level = "INFO"
    elif args.verbosity == 2:
        log_level = "DEBUG"
    elif args.verbosity >= 3:
        log_level = "TRACE"

    # Define a custom TRACE log level
    logging.addLevelName('TRACE', logging.DEBUG - 5)
    setattr(logging, 'TRACE', logging.DEBUG - 5)
    
    # Configure logging
    logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s')

    # Start the server
    server = Server(config["listen_host"], config["listen_port"], config["connect_host"], config["connect_port"])
    server.start()

if __name__ == "__main__":
    main()
