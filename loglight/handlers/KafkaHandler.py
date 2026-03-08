from kafka import KafkaProducer
from loglight.handlers.BaseHandler import BaseHandler


class KafkaHandler(BaseHandler):
    def __init__(self, bootstrap_servers, topic, enable_internal_logging=True):
        super().__init__(enable_internal_logging)
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=lambda v: v.encode('utf-8'))
        self.topic = topic

    def emit(self, log_str: str):
        try:
            self.producer.send(self.topic, log_str)
            self.producer.flush()
        except Exception as e:
            self.log_internal_error("kafka_emit_failed", e)
