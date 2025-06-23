import pytest
from unittest.mock import patch, MagicMock
from loglight.handlers import WebhookHandler


@patch("requests.post")
def test_webhook_handler_posts_data(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    url = "http://example.com/webhook"
    handler = WebhookHandler(url)

    log_str = '{"event":"test"}'
    handler.emit(log_str)

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert kwargs["data"] == log_str
    assert kwargs["headers"]["Content-Type"] == "application/json"


@patch("requests.post")
def test_webhook_handler_handles_exception(mock_post, capsys):
    mock_post.side_effect = Exception("Failed to connect")

    handler = WebhookHandler("http://example.com/webhook")
    handler.emit('{"event":"error"}')

    captured = capsys.readouterr()
    assert "webhook_emit_failed" in captured.err
