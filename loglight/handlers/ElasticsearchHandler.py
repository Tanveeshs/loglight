import requests

from loglight.handlers.BaseHandler import BaseHandler


class ElasticsearchHandler(BaseHandler):
    def __init__(self, es_url, index_name, enable_internal_logging=True):
        super().__init__(enable_internal_logging)
        self.es_url = es_url
        self.index_name = index_name

    def emit(self, log_str: str):
        try:
            url = f"{self.es_url}/{self.index_name}/_doc"
            response = requests.post(
                url, data=log_str, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
        except Exception as e:
            self.log_internal_error("elasticsearch_emit_failed", e)
