try:
    from kafka import KafkaProducer
except ImportError:  # pragma: no cover - exercised only when kafka-python is missing
    KafkaProducer = None

from loglight.handlers.BaseHandler import BaseHandler


class KafkaHandler(BaseHandler):
    def __init__(self, bootstrap_servers, topic, enable_internal_logging=True):
        super().__init__(enable_internal_logging)
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None

    def _get_producer(self):
        if self.producer is not None:
            return self.producer
        if KafkaProducer is None:
            raise ImportError("kafka-python is required for KafkaHandler")
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: v.encode("utf-8"),
        )
        return self.producer

    def emit(self, log_str: str):
        try:
            producer = self._get_producer()
            producer.send(self.topic, log_str)
            producer.flush()
        except Exception as e:
            self.log_internal_error("kafka_emit_failed", e)
