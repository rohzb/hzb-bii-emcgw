import socket
import threading
import logging

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
        self.stop_event = threading.Event()

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
        while not self.stop_event.is_set():
            try:
                buffer = src.recv(4096)
                if not buffer:
                    break  # Handle disconnect properly
                dst.send(self.handle(buffer, direction))
            except (socket.error, ConnectionResetError):
                logging.warning("Socket connection closed.")
                break

        self.stop_event.set()  # Signal thread termination
        logging.warning(f"Closing connection {src.getsockname()[0]},{src.getsockname()[1]}!")
        src.close()
        logging.warning(f"Closing connection {dst.getsockname()[0]},{dst.getsockname()[1]}!")
        dst.close()
    