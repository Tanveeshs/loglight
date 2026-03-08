import json
import pytest
from loglight import log
from loglight.config import LoggerConfig
from loglight.handlers import ConsoleHandler


def test_end_to_end_logging(capsys):
    config = LoggerConfig(service="test-service", env="test")
    logger = log.__class__(config=config, handler=ConsoleHandler())

    logger.info("test message", user_id="123", request_id="abc")

    captured = capsys.readouterr()
    output = captured.out.strip()
    log_entry = json.loads(output)

    assert log_entry["message"] == "test message"
    assert log_entry["service"] == "test-service"
    assert log_entry["env"] == "test"
    assert log_entry["user_id"] == "123"
    assert log_entry["request_id"] == "abc"


def test_request_context(capsys):
    from loglight.logger import Logger
    config = LoggerConfig()
    logger = Logger(config=config, handler=ConsoleHandler())

    # Set context
    Logger.request_id_context.set("ctx-123")

    logger.info("context test")

    captured = capsys.readouterr()
    output = captured.out.strip()
    log_entry = json.loads(output)

    assert log_entry["request_id"] == "ctx-123"


def test_redaction(capsys):
    config = LoggerConfig(redaction_rules=["password"])
    logger = log.__class__(config=config, handler=ConsoleHandler())

    logger.info("login", password="secret123")

    captured = capsys.readouterr()
    output = captured.out.strip()
    log_entry = json.loads(output)

    assert log_entry["password"] == "***"


def test_sampling_integration(capsys):
    config = LoggerConfig(sampling_rate=0.5)
    logger = log.__class__(config=config, handler=ConsoleHandler())

    # With sampling, some logs may appear, but not all
    logs = []
    for i in range(100):
        logger.info(f"log_{i}")
        captured = capsys.readouterr()
        if captured.out.strip():
            logs.append(captured.out.strip())

    # Should have some logs, but not all 100
    assert 0 < len(logs) < 100


def test_rate_limiting_integration(capsys):
    import time
    config = LoggerConfig(rate_limit=2)
    logger = log.__class__(config=config, handler=ConsoleHandler())

    for i in range(5):
        logger.info(f"log_{i}")

    captured = capsys.readouterr()
    outputs = [line for line in captured.out.strip().split("\n") if line]
    assert len(outputs) <= 2  # At most 2 logs per second


def test_metrics_integration(capsys):
    config = LoggerConfig()
    logger = log.__class__(config=config, handler=ConsoleHandler())

    logger.info("test")
    logger.warning("warn")
    logger.error("err")
    logger.critical("crit")

    metrics = logger.get_metrics()
    assert metrics["logs"] == 4
    assert metrics["errors"] == 2  # error and critical


def test_decorator_integration(capsys):
    import time
    from loglight.decorators import log_timing

    @log_timing()
    def timed_integration_func():
        time.sleep(0.01)
        return "timed"

    result = timed_integration_func()
    assert result == "timed"
