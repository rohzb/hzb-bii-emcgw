import logging

class Logger(logging.Logger):
    def __init__(self, log_level: str = "INFO"):
        """
        Initializes the custom logger with the specified log_level.

        Args:
            log_level (str): The log level for the logger (default is "INFO").

        Returns:
            None
        """
        super().__init__('custom_logger', level=getattr(logging, log_level))
        self.create_custom_log_levels()
        self.configure_basic()

    def create_custom_log_levels(self):
        """
        Create custom log levels: VERBOSE and TRACE.

        The VERBOSE level is set to INFO - 5, and TRACE is set to DEBUG - 5.
        These custom log levels allow finer control of log output.

        Args:
            None

        Returns:
            None
        """
        logging.addLevelName('VERBOSE', logging.INFO - 5)
        setattr(logging, 'VERBOSE', logging.INFO - 5)
        logging.addLevelName('TRACE', logging.DEBUG - 5)
        setattr(logging, 'TRACE', logging.DEBUG - 5)

    def configure_basic(self):
        """
        Configure basic logging options.

        This method configures basic options such as log format and handler (stream handler).

        Args:
            None

        Returns:
            None
        """
        formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.addHandler(stream_handler)

    def set_log_level(self, log_level: str):
        """
        Set the log level for the logger.

        Args:
            log_level (str): The log level to set for the logger.

        Returns:
            None
        """
        self.setLevel(getattr(logging, log_level))

# Common logger instance for the project
logger = Logger()
