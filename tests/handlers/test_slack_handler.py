import json
import pytest
from unittest.mock import patch, MagicMock
from loglight.handlers import SlackHandler


@patch("requests.post")
def test_slack_handler_sends_formatted_message(mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    webhook_url = "https://hooks.slack.com/services/test/webhook"
    handler = SlackHandler(webhook_url, channel="#general")

    log_entry = {
        "level": "WARNING",
        "message": "something_happened",
        "details": {"user": "alice", "action": "login"},
    }
    log_str = json.dumps(log_entry)

    handler.emit(log_str)

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    payload = kwargs.get("json", {})
    assert "text" in payload
    assert "[WARNING]" in payload["text"]
    assert "something_happened" in payload["text"]
    assert payload.get("channel") == "#general"


@patch("requests.post")
def test_slack_handler_handles_invalid_json(mock_post, capsys):
    mock_post.return_value = MagicMock(raise_for_status=lambda: None)

    handler = SlackHandler("https://hooks.slack.com/services/test/webhook")
    # Send invalid JSON string
    handler.emit("not a json")

    captured = capsys.readouterr()
    assert "slack_emit_failed" in captured.err
