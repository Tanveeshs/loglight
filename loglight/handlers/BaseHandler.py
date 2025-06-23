import sys


class BaseHandler:
    def __init__(self, enable_internal_logging):
        self.enable_internal_logging = enable_internal_logging
        self.internal_logger= None

    def log_internal_error(self, event: str, error: Exception, context: dict = None):
        if self.enable_internal_logging:
            details = context or {}
            details["error"] = str(error)
            if not self.internal_logger:
                from loglight.logger import Logger
                from loglight.config import LoggerConfig
                from loglight.handlers.ConsoleHandler import ConsoleHandler
                self.internal_logger = Logger(
                    config=LoggerConfig(level="ERROR"),
                    handler=ConsoleHandler(stream=sys.stderr)
                )
            details = context or {}
            details["error"] = str(error)
            self.internal_logger.error(event, details=details)
