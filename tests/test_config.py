import os
import pytest
from loglight.config import LoggerConfig


def test_config_defaults():
    config = LoggerConfig()
    assert config.level == "INFO"
    assert config.sampling_rate == 1.0
    assert config.rate_limit == 0


def test_config_env_loading(monkeypatch):
    monkeypatch.setenv('LOG_LEVEL', 'DEBUG')
    monkeypatch.setenv('LOG_SERVICE', 'test-service')
    monkeypatch.setenv('LOG_SAMPLING_RATE', '0.5')
    monkeypatch.setenv('LOG_RATE_LIMIT', '10')
    monkeypatch.setenv('LOG_REDACTION_RULES', 'password,secret')

    config = LoggerConfig()
    assert config.level == "DEBUG"
    assert config.service == "test-service"
    assert config.sampling_rate == 0.5
    assert config.rate_limit == 10
    assert config.redaction_rules == ['password', 'secret']


def test_config_env_invalid_values(monkeypatch):
    monkeypatch.setenv('LOG_SAMPLING_RATE', 'invalid')
    monkeypatch.setenv('LOG_RATE_LIMIT', 'not_a_number')

    config = LoggerConfig()
    # Should use defaults if invalid
    assert config.sampling_rate == 1.0
    assert config.rate_limit == 0


def test_config_redaction_env(monkeypatch):
    monkeypatch.setenv('LOG_REDACTION_RULES', 'password,token,secret')

    config = LoggerConfig()
    assert config.redaction_rules == ['password', 'token', 'secret']
