# loglight/logger.py
import json
import sys
from datetime import datetime

from loglight.config import LoggerConfig
from loglight.handlers.ConsoleHandler import ConsoleHandler


class Logger:
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    def __init__(self,config: LoggerConfig = None, handler=None):
        self.config = config or LoggerConfig()
        self.level = self.LEVELS.get(self.config.level, 20)
        if handler:
            self.handler = handler
        else:
            self.handler = ConsoleHandler(self.config.output)

    def log(self, level, event, details=None, **extra):
        lvl_value = self.LEVELS.get(level.upper(), 20)
        if lvl_value < self.level:
            return

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level.upper(),
            "event": event,
            "details": details or {},
        }
        # Merge extra fields into details to keep consistent structure
        if extra:
            log_entry["details"].update(extra)

        serialized = self.config.serializer(log_entry)
        self.handler.emit(serialized)

    def debug(self, event, details=None, **extra):
        self.log("DEBUG", event, details, **extra)

    def info(self, event, details=None, **extra):
        self.log("INFO", event, details, **extra)

    def warning(self, event, details=None, **extra):
        self.log("WARNING", event, details, **extra)

    def error(self, event, details=None, **extra):
        self.log("ERROR", event, details, **extra)

    def critical(self, event, details=None, **extra):
        self.log("CRITICAL", event, details, **extra)
