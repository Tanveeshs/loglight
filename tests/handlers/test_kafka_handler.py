import pytest
from unittest.mock import patch, MagicMock
from loglight.handlers.KafkaHandler import KafkaHandler


def test_kafka_handler_emit_success():
    handler = KafkaHandler(bootstrap_servers="localhost:9092", topic="test-topic")

    with patch('loglight.handlers.KafkaHandler.KafkaProducer') as mock_producer_class:
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer

        handler.emit('{"test": "data"}')

        mock_producer.send.assert_called_once_with("test-topic", '{"test": "data"}')
        mock_producer.flush.assert_called_once()


def test_kafka_handler_emit_failure():
    handler = KafkaHandler(bootstrap_servers="localhost:9092", topic="test-topic")

    with patch('loglight.handlers.KafkaHandler.KafkaProducer') as mock_producer_class:
        mock_producer = MagicMock()
        mock_producer.send.side_effect = Exception("Kafka error")
        mock_producer_class.return_value = mock_producer

        with patch.object(handler, 'log_internal_error') as mock_log_error:
            handler.emit('{"test": "data"}')
            mock_log_error.assert_called_once()


def test_kafka_handler_multiple_servers():
    handler = KafkaHandler(bootstrap_servers=["server1:9092", "server2:9092"], topic="multi-topic")

    with patch('loglight.handlers.KafkaHandler.KafkaProducer') as mock_producer_class:
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer

        handler.emit('{"multi": "log"}')

        mock_producer_class.assert_called_once_with(bootstrap_servers=["server1:9092", "server2:9092"], value_serializer=mock_producer_class.call_args[1]['value_serializer'])
        mock_producer.send.assert_called_once_with("multi-topic", '{"multi": "log"}')


def test_kafka_handler_flush_called():
    handler = KafkaHandler(bootstrap_servers="localhost:9092", topic="test-topic")

    with patch('loglight.handlers.KafkaHandler.KafkaProducer') as mock_producer_class:
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer

        handler.emit('{"test": "data"}')

        mock_producer.flush.assert_called_once()


def test_kafka_handler_empty_message():
    handler = KafkaHandler(bootstrap_servers="localhost:9092", topic="test-topic")

    with patch('loglight.handlers.KafkaHandler.KafkaProducer') as mock_producer_class:
        mock_producer = MagicMock()
        mock_producer_class.return_value = mock_producer

        handler.emit('')

        mock_producer.send.assert_called_once_with("test-topic", '')
        mock_producer.flush.assert_called_once()


def test_kafka_handler_internal_logging_disabled():
    handler = KafkaHandler(bootstrap_servers="localhost:9092", topic="test-topic", enable_internal_logging=False)

    with patch('loglight.handlers.KafkaHandler.KafkaProducer') as mock_producer_class:
        mock_producer = MagicMock()
        mock_producer.send.side_effect = Exception("Error")
        mock_producer_class.return_value = mock_producer

        # Should not log internal error
        handler.emit('{"test": "data"}')
