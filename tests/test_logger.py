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
    assert "message" in log_entry

    # Validate level and message
    assert log_entry["level"] == "info"
    assert log_entry["message"] == "test_event"

    # Validate flattened fields
    assert log_entry["foo"] == "bar"
    assert log_entry["extra_field"] == 123

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
    logger = Logger(config=config, handler=ConsoleHandler())

    logger.debug("debug_event")
    logger.info("info_event")
    logger.warning("warn_event")
    logger.error("error_event")
    logger.critical("crit_event")

    captured = capsys.readouterr()

    outputs = [line for line in captured.out.strip().split("\n") if line]
    expected_levels = ["debug", "info", "warning", "error", "critical"]
    expected_messages = [
        "debug_event",
        "info_event",
        "warn_event",
        "error_event",
        "crit_event",
    ]

    assert len(outputs) == len(expected_levels)

    for i, line in enumerate(outputs):
        log_entry = json.loads(line)
        assert log_entry["level"] == expected_levels[i]
        assert log_entry["message"] == expected_messages[i]


def test_sampling(capsys):
    config = LoggerConfig(sampling_rate=0.0)  # Never log
    logger = Logger(config=config, handler=ConsoleHandler())

    logger.info("should_not_log")
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert output == ""


def test_rate_limiting(capsys):
    config = LoggerConfig(rate_limit=1)  # Only 1 log per second
    logger = Logger(config=config, handler=ConsoleHandler())

    logger.info("first_log")
    captured = capsys.readouterr()
    assert captured.out.strip() != ""

    logger.info("second_log")  # Should be rate limited
    captured = capsys.readouterr()
    assert captured.out.strip() == ""


def test_metrics(capsys):
    config = LoggerConfig()
    logger = Logger(config=config, handler=ConsoleHandler())

    logger.info("info_log")
    logger.error("error_log")

    metrics = logger.get_metrics()
    assert metrics["logs"] == 2
    assert metrics["errors"] == 1


def test_redaction_multiple_fields(capsys):
    config = LoggerConfig(redaction_rules=["password", "token"])
    logger = Logger(config=config, handler=ConsoleHandler())

    logger.info("login", password="secret", token="abc123", user="test")

    captured = capsys.readouterr()
    output = captured.out.strip()
    log_entry = json.loads(output)

    assert log_entry["password"] == "***"
    assert log_entry["token"] == "***"
    assert log_entry["user"] == "test"


def test_sampling_zero(capsys):
    config = LoggerConfig(sampling_rate=0.0)
    logger = Logger(config=config, handler=ConsoleHandler())

    for _ in range(10):
        logger.info("should_not_log")

    captured = capsys.readouterr()
    output = captured.out.strip()
    assert output == ""


def test_rate_limit_zero(capsys):
    config = LoggerConfig(rate_limit=0)  # No limit
    logger = Logger(config=config, handler=ConsoleHandler())

    for i in range(10):
        logger.info(f"log_{i}")

    captured = capsys.readouterr()
    outputs = [line for line in captured.out.strip().split("\n") if line]
    assert len(outputs) == 10


def test_request_context_inheritance(capsys):
    from loglight.logger import Logger

    config = LoggerConfig()
    logger = Logger(config=config, handler=ConsoleHandler())

    Logger.request_id_context.set("parent_id")

    def child_func():
        Logger.request_id_context.set("child_id")
        logger.info("child log")

    logger.info("parent log")
    child_func()

    captured = capsys.readouterr()
    outputs = [json.loads(line) for line in captured.out.strip().split("\n") if line]

    assert outputs[0]["request_id"] == "parent_id"
    assert outputs[1]["request_id"] == "child_id"
