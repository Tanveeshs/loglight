import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from loglight.logger import Logger


class LogLightMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger: Logger = None):
        super().__init__(app)
        self.logger = logger or Logger()

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        # Set request_id in context
        token = self.logger.request_id_context.set(request_id)
        try:
            response = await call_next(request)
            return response
        finally:
            self.logger.request_id_context.reset(token)
