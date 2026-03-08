import sys
import json


class BaseHandler:
    # Log level hierarchy
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    def __init__(self, enable_internal_logging, min_level=None, filter_func=None):
        self.enable_internal_logging = enable_internal_logging
        self.internal_logger = None
        # min_level: Only emit logs at this level or higher (e.g., "ERROR" means ERROR and CRITICAL)
        self.min_level = min_level
        self.min_level_value = self.LEVELS.get(min_level.upper(), 0) if min_level else 0
        # Custom filter function: takes log_entry dict, returns True to emit
        self.filter_func = filter_func

    def should_handle(self, log_entry: dict) -> bool:
        """Check if this handler should process the log entry based on filters.

        Args:
            log_entry: The log entry dictionary

        Returns:
            True if the handler should process this log, False otherwise
        """
        # Check minimum level
        log_level = log_entry.get("level", "INFO").upper()
        log_level_value = self.LEVELS.get(log_level, 20)
        if log_level_value < self.min_level_value:
            return False

        # Check custom filter function
        if self.filter_func and not self.filter_func(log_entry):
            return False

        return True

    def emit(self, log_str: str):
        """Emit a log record. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement emit()")

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
