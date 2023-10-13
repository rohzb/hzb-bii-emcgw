import argparse
import logging
import yaml
from .server import Server

def main():
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
