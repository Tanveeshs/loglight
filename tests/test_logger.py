import json
import re

from loglight.logger import Logger
from loglight.config import LoggerConfig
from loglight.handlers import ConsoleHandler


def test_log_output_structure(capsys):
    config = LoggerConfig(level="DEBUG")
    logger = Logger(config, handler=ConsoleHandler())
    logger.info("test_event", details={"foo": "bar"}, extra_field=123)
    captured = capsys.readouterr()

    output = captured.out.strip()

    # Parse output JSON
    log_entry = json.loads(output)

    # Check required keys
    assert "timestamp" in log_entry
    assert "level" in log_entry
    assert "event" in log_entry
    assert "details" in log_entry

    # Validate level and event
    assert log_entry["level"] == "INFO"
    assert log_entry["event"] == "test_event"

    # Validate details contains the passed fields (including extra fields)
    assert log_entry["details"]["foo"] == "bar"
    assert log_entry["details"]["extra_field"] == 123

    # Validate timestamp format (ISO 8601 UTC)
    iso8601_utc = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z"
    assert re.match(iso8601_utc, log_entry["timestamp"])


def test_log_level_filtering(capsys):
    # Use LoggerConfig to set level
    config = LoggerConfig(level="WARNING")
    logger = Logger(config=config, handler=ConsoleHandler())

    # INFO should not log (filtered out)
    logger.info("should_not_log")
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert output == ""

    # ERROR should log
    logger.error("should_log", details={"error": True})
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert output != ""


def test_log_methods(capsys):
    config = LoggerConfig(level="DEBUG")
    logger = Logger(config=config,handler=ConsoleHandler())

    logger.debug("debug_event")
    logger.info("info_event")
    logger.warning("warn_event")
    logger.error("error_event")
    logger.critical("crit_event")

    captured = capsys.readouterr()

    outputs = [line for line in captured.out.strip().split("\n") if line]
    expected_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    expected_events = ["debug_event", "info_event", "warn_event", "error_event", "crit_event"]

    assert len(outputs) == len(expected_levels)

    for i, line in enumerate(outputs):
        log_entry = json.loads(line)
        assert log_entry["level"] == expected_levels[i]
        assert log_entry["event"] == expected_events[i]
