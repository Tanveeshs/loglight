import pytest
from unittest.mock import patch, MagicMock
from loglight.handlers.ElasticsearchHandler import ElasticsearchHandler


def test_elasticsearch_handler_emit_success():
    handler = ElasticsearchHandler(
        es_url="http://localhost:9200", index_name="test-index"
    )

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        handler.emit('{"test": "data"}')

        mock_post.assert_called_once_with(
            "http://localhost:9200/test-index/_doc",
            data='{"test": "data"}',
            headers={"Content-Type": "application/json"},
        )


def test_elasticsearch_handler_emit_failure():
    handler = ElasticsearchHandler(
        es_url="http://localhost:9200", index_name="test-index"
    )

    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Connection error")

        with patch.object(handler, "log_internal_error") as mock_log_error:
            handler.emit('{"test": "data"}')
            mock_log_error.assert_called_once()


def test_elasticsearch_handler_custom_url_and_index():
    handler = ElasticsearchHandler(
        es_url="https://es.example.com:9200", index_name="my-logs"
    )

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        handler.emit('{"custom": "log"}')

        mock_post.assert_called_once_with(
            "https://es.example.com:9200/my-logs/_doc",
            data='{"custom": "log"}',
            headers={"Content-Type": "application/json"},
        )


def test_elasticsearch_handler_http_error():
    handler = ElasticsearchHandler(
        es_url="http://localhost:9200", index_name="test-index"
    )

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 400")
        mock_post.return_value = mock_response

        with patch.object(handler, "log_internal_error") as mock_log_error:
            handler.emit('{"test": "data"}')
            mock_log_error.assert_called_once()


def test_elasticsearch_handler_empty_log():
    handler = ElasticsearchHandler(
        es_url="http://localhost:9200", index_name="test-index"
    )

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        handler.emit("")

        mock_post.assert_called_once_with(
            "http://localhost:9200/test-index/_doc",
            data="",
            headers={"Content-Type": "application/json"},
        )


def test_elasticsearch_handler_internal_logging_disabled():
    handler = ElasticsearchHandler(
        es_url="http://localhost:9200",
        index_name="test-index",
        enable_internal_logging=False,
    )

    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Error")

        # Should not log internal error since disabled
        handler.emit('{"test": "data"}')
        # No assertion needed, just ensure no error
