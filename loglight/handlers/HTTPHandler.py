import sys

from loglight.handlers.BaseHandler import BaseHandler


class HTTPHandler(BaseHandler):
    def __init__(self, url, headers=None, timeout=5, enable_internal_logging=True):
        super().__init__(enable_internal_logging)
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}
        self.timeout = timeout
        try:
            import requests

            self.requests = requests
        except ImportError:
            raise ImportError(
                "requests is required for HTTPHandler. Install with: pip install loglight[http]"
            )

    def emit(self, log_str: str):
        try:
            response = self.requests.post(
                self.url, data=log_str, headers=self.headers, timeout=self.timeout
            )
            response.raise_for_status()
        except Exception as e:
            self.log_internal_error("http_handler_error", e)
