import uuid
from flask import g

from loglight.logger import Logger


class LogLightMiddleware:
    def __init__(self, app, logger: Logger = None):
        self.logger = logger or Logger()
        app.before_request(self.before_request)
        app.after_request(self.after_request)

    def before_request(self):
        request_id = str(uuid.uuid4())
        g.request_id = request_id
        # Set in context
        self.logger.request_id_context.set(request_id)

    def after_request(self, response):
        # Reset context if needed, but since per request, maybe not necessary
        return response
