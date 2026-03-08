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


def test_console_handler_custom_stream():
    custom_stream = io.StringIO()
    handler = ConsoleHandler(stream=custom_stream)

    handler.emit('{"custom": "stream"}')
    output = custom_stream.getvalue().strip()
    assert output == '{"custom": "stream"}'


def test_console_handler_multiple_emits():
    fake_stream = io.StringIO()
    handler = ConsoleHandler(stream=fake_stream)

    handler.emit('{"first": "log"}')
    handler.emit('{"second": "log"}')

    output = fake_stream.getvalue().strip().split("\n")
    assert len(output) == 2
    assert output[0] == '{"first": "log"}'
    assert output[1] == '{"second": "log"}'


def test_console_handler_empty_emit():
    fake_stream = io.StringIO()
    handler = ConsoleHandler(stream=fake_stream)

    handler.emit("")
    output = fake_stream.getvalue().strip()
    assert output == ""


def test_console_handler_with_newlines():
    fake_stream = io.StringIO()
    handler = ConsoleHandler(stream=fake_stream)

    handler.emit('{"msg": "with\nnewline"}')
    output = fake_stream.getvalue()
    assert output.endswith("\n")
