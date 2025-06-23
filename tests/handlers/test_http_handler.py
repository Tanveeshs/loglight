import pytest
from unittest.mock import patch, MagicMock
from loglight.handlers import HTTPHandler


@patch("requests.post")
def test_http_handler_posts_data(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    handler = HTTPHandler("http://example.com/logs")
    log_str = '{"level":"INFO","event":"test"}'
    handler.emit(log_str)

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["data"] == log_str
    assert kwargs["headers"]["Content-Type"] == "application/json"


@patch("requests.post")
def test_http_handler_handles_exception_gracefully(mock_post, capsys):
    mock_post.side_effect = Exception("Connection error")

    handler = HTTPHandler("http://example.com/logs")
    handler.emit('{"level":"ERROR"}')

    captured = capsys.readouterr()
    assert "http_handler_error" in captured.err
