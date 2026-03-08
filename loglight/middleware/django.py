import uuid
from django.utils.deprecation import MiddlewareMixin

from loglight.logger import Logger


class LogLightMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None, logger: Logger = None):
        self.logger = logger or Logger()
        super().__init__(get_response)

    def process_request(self, request):
        request_id = str(uuid.uuid4())
        request.request_id = request_id
        # Set in context
        self.logger.request_id_context.set(request_id)

    def process_response(self, request, response):
        return response
