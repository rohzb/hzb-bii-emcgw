# Import necessary libraries
import socket
import threading
import argparse
import logging
import yaml

# Disable SOCKS proxy for now
# import socks
# socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '174.26.2.2', 9052)
# socket.socket = socks.socksocket

# Configure logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s')

# Define a function to handle data flows between the local and remote ports
def handle(buffer: bytes, direction: bool, src_address: tuple[str, int], src_port: int, dst_address: tuple[str, int], dst_port: int) -> bytes:
    """
    Intercept the data flows between local port and the target port
    """
    if direction:
        logging.debug(f"{src_address[0]},{src_port} -> {dst_address[0]},{dst_port} {len(buffer)} bytes")
    else:
        logging.debug(f"{dst_address[0]},{dst_port} <- {src_address[0]},{src_port} {len(buffer)} bytes")
    return buffer

# Define a function to transfer data between two sockets
def transfer(src: socket.socket, dst: socket.socket, direction: bool):
    """
    Transfer data between two sockets in a given direction
    """
    src_address, src_port = src.getsockname()
    dst_address, dst_port = dst.getsockname()
    while True:
        try:
            buffer = src.recv(4096)
            dst.send(handle(buffer, direction, src_address, src_port, dst_address, dst_port))
        except Exception as e:
            logging.error(repr(e))
            break
    logging.warning(f"Closing connection {src_address[0]},{src_port}! ")
    src.close()
    logging.warning(f"Closing connection {dst_address[0]},{dst_port}! ")
    dst.close()

# Define a function to start a server that listens on a given port and forwards connections to a remote host and port
def server(local_host: str, local_port: int, remote_host: str, remote_port: int):
    """
    Start a server that listens on a given port and forwards connections to a remote host and port
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((local_host, local_port))
    server_socket.listen(0x40)
    logging.info(f"Server started on {local_host}:{local_port}")
    logging.info(f"Connect to {local_host}:{local_port} to access {remote_host}:{remote_port}")
    while True:
        src_socket, src_address = server_socket.accept()
        logging.info(f"[Establishing connection] {src_address[0]} -> {local_host}:{local_port} -> ? -> {remote_host}:{remote_port}")
        try:
            dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dst_socket.connect((remote_host, remote_port))
            logging.info(f"[OK] {src_address[0]} -> {local_host}:{local_port} -> {dst_socket.getsockname()} -> {remote_host}:{remote_port}")
            s = threading.Thread(target=transfer, args=(dst_socket, src_socket, False))
            r = threading.Thread(target=transfer, args=(src_socket, dst_socket, True))
            s.start()
            r.start()
        except Exception as e:
            logging.error(repr(e))

# Define the main function
def main():
    # Create an argparse parser
    parser = argparse.ArgumentParser()

    # Add arguments for the config file, listen and connect host/port
    parser.add_argument("-c", "--config", help="Path to YAML config file")
    parser.add_argument("-l", "--listen-host", help="The host to listen on")
    parser.add_argument("-p", "--listen-port", type=int, help="The port to bind to")
    parser.add_argument("-r", "--connect-host", help="The target host to connect to")
    parser.add_argument("-P", "--connect-port", type=int, help="The target port to connect to")

    # Parse the command line arguments
    args = parser.parse_args()

    # Load the configuration from the config file or command line arguments
    config = {}
    if args.config:
        with open(args.config, "r") as f:
            config = yaml.safe_load(f)
    config.update({
        "listen_host": args.listen_host or config.get("listen_host"),
        "listen_port": args.listen_port or config.get("listen_port"),
        "connect_host": args.connect_host or config.get("connect_host"),
        "connect_port": args.connect_port or config.get("connect_port")
    })

    # Start the server
    server(config["listen_host"], config["listen_port"],
           config["connect_host"], config["connect_port"])

if __name__ == "__main__":
    main()