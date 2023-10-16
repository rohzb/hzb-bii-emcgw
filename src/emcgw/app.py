import argparse
import logging
import yaml
import os
from .server import Server, AccessList

def main():
    """
    Start the emcgw server with optional configurations and allowed clients.

    Examples:
        Command-line arguments:
        - Start the server with default settings:
            emcgw

        - Start the server with custom settings and allowed clients:
            emcgw -c config.yaml -l localhost -p 8080 -r example.com -P 80 -L DEBUG -v -a 192.168.1.0/24 192.168.2.0/24

        Configuration YAML file (config.yaml):
        listen_host: "localhost"
        listen_port: 8080
        connect_host: "example.com"
        connect_port: 80
        log_level: "INFO"
        allowed_clients:
            - "192.168.1.0/24"
            - "192.168.2.0/24"

    Note:
        To specify allowed clients using the configuration YAML file, use the "allowed_clients" key, providing a list of client IP/CIDR or hostname strings.
    """
    parser = argparse.ArgumentParser(prog="emcgw")
    parser.add_argument("-c", "--config", help="Path to YAML config file")
    parser.add_argument("-l", "--listen-host", help="The host to listen on")
    parser.add_argument("-p", "--listen-port", type=int, help="The port to bind to")
    parser.add_argument("-r", "--connect-host", help="The target host to connect to")
    parser.add_argument("-P", "--connect-port", type=int, help="The target port to connect to")
    parser.add_argument("-L", "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "VERBOSE", "TRACE"], help="Set logging level")
    parser.add_argument("-v", dest="verbosity", action="count", default=0, help="Increase verbosity level (-v for INFO, -vv for DEBUG, -vvv for TRACE)")
    parser.add_argument("-a", "--allowed-clients", nargs="*", help="List of allowed clients in IP/CIDR or hostname format")

    args = parser.parse_args()
    config = {}

    # Read optional config files from standard locations
    config_files = [os.path.join("/etc/emcgw/config.yaml"), "/etc/emcgw.yaml", args.config]

    for file in config_files:
        if file and os.path.isfile(file):
            with open(file, "r") as f:
                config_data = yaml.safe_load(f)
                if config_data:
                    config.update(config_data)

    config.update({
        "listen_host": args.listen_host or config.get("listen_host"),
        "listen_port": args.listen_port or config.get("listen_port"),
        "connect_host": args.connect_host or config.get("connect_host"),
        "connect_port": args.connect_port or config.get("connect_port"),
    })

    # Parse allowed clients
    allowed_clients = args.allowed_clients or config.get("allowed_clients")

    # Set logging level from command line or config file
    log_level = args.log_level or config.get("log_level", "INFO")

    # Adjust logging level based on verbosity
    if args.verbosity == 0:
        log_level = "INFO"
    elif args.verbosity == 1:
        log_level = "VERBOSE"
    elif args.verbosity == 2:
        log_level = "DEBUG"
    elif args.verbosity >= 3:
        log_level = "TRACE"

    # Define custom log levels
    logging.addLevelName('VERBOSE', logging.INFO - 5)
    setattr(logging, 'VERBOSE', logging.INFO - 5)

    logging.addLevelName('TRACE', logging.DEBUG - 5)
    setattr(logging, 'TRACE', logging.DEBUG - 5)

    # Configure logging
    logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s')

    # Initialize an AccessList with allowed clients
    access_list = AccessList(allowed_clients)

    # Start the server with the access list
    server = Server(
        config["listen_host"],
        config["listen_port"],
        config["connect_host"],
        config["connect_port"],
        access_list
    )
    server.start()


if __name__ == "__main__":
    main()
