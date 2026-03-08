import socket
import sys
from loglight.handlers.BaseHandler import BaseHandler


class SyslogHandler(BaseHandler):
    def __init__(self, address=('localhost', 514), facility=1, enable_internal_logging=True):
        super().__init__(enable_internal_logging)
        self.address = address
        self.facility = facility
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def emit(self, log_str: str):
        try:
            # Simple syslog format: <priority>timestamp hostname message
            priority = self.facility * 8  # assuming level 0
            message = f"<{priority}> {log_str}"
            self.sock.sendto(message.encode('utf-8'), self.address)
        except Exception as e:
            self.log_internal_error("syslog_emit_failed", e, context={"address": self.address})
