import pytest
from unittest.mock import patch
from loglight.decorators import log_function, log_exceptions, log_timing, log_with_metadata
from loglight import log


def test_log_function_decorator(capsys):
    @log_function()
    def dummy_func():
        return "ok"

    with patch('loglight.decorators.log.log') as mock_log:
        result = dummy_func()
        assert result == "ok"
        assert mock_log.call_count == 2  # start and end


def test_log_exceptions_decorator(capsys):
    @log_exceptions()
    def failing_func():
        raise ValueError("test error")

    with pytest.raises(ValueError):
        failing_func()


def test_log_timing_decorator(capsys):
    @log_timing()
    def timed_func():
        return "done"

    with patch('loglight.decorators.log.log') as mock_log:
        result = timed_func()
        assert result == "done"
        # Check that duration is logged
        calls = mock_log.call_args_list
        assert len(calls) == 2
        # Second call should have duration
        assert 'duration' in calls[1][1]


def test_log_with_metadata_decorator(capsys):
    @log_with_metadata(metadata={"component": "test"})
    def meta_func():
        return "meta"

    with patch('loglight.decorators.log.info') as mock_info:
        result = meta_func()
        assert result == "meta"
        calls = mock_info.call_args_list
        assert len(calls) == 2
        assert calls[0][1]['component'] == "test"


def test_log_function_decorator_with_level(capsys):
    @log_function(level="debug")
    def debug_func():
        return "debug"

    with patch('loglight.decorators.log.log') as mock_log:
        result = debug_func()
        assert result == "debug"
        calls = mock_log.call_args_list
        assert calls[0][0][0] == "debug"  # level


def test_log_timing_decorator_exception(capsys):
    @log_timing()
    def failing_timed_func():
        raise RuntimeError("timed error")

    with patch('loglight.decorators.log.error') as mock_error:
        with pytest.raises(RuntimeError):
            failing_timed_func()
        mock_error.assert_called_once()


def test_log_exceptions_decorator_custom_level(capsys):
    @log_exceptions(level="critical")
    def critical_fail_func():
        raise Exception("critical")

    with pytest.raises(Exception):
        critical_fail_func()


def test_log_with_metadata_multiple_calls(capsys):
    @log_with_metadata(metadata={"version": "1.0"})
    def multi_func():
        pass

    with patch('loglight.decorators.log.info') as mock_info:
        multi_func()
        multi_func()
        assert mock_info.call_count == 4  # 2 per call
