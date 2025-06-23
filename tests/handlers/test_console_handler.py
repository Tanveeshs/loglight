import io
import pytest
from loglight.handlers import ConsoleHandler


def test_stream_handler_writes_to_stream():
    fake_stream = io.StringIO()
    handler = ConsoleHandler(stream=fake_stream)

    handler.emit('{"event":"test_event"}')
    output = fake_stream.getvalue().strip()
    assert output == '{"event":"test_event"}'


def test_stream_handler_defaults_to_stdout(monkeypatch):
    import sys

    captured = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured)

    handler = ConsoleHandler()
    handler.emit('{"message":"hello"}')
    output = captured.getvalue().strip()
    assert output == '{"message":"hello"}'
