# tests/test_router_handler.py
"""
Unit tests for RouterHandler and Logger integration with routing.
"""

import pytest
import json
from unittest.mock import Mock
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig, RouterHandler
from loglight.logger import Logger
from loglight.config import LoggerConfig


class TestRouterHandler:
    """Test RouterHandler functionality."""

    def test_router_handler_initialization(self):
        """Test RouterHandler initialization."""
        mock_handler = Mock()
        config = RoutingConfig()
        router = RouterHandler(mock_handler, config)

        assert router.handler == mock_handler
        assert router.routing_config == config

    def test_router_handler_should_handle_true(self):
        """Test should_handle returns True when routing matches."""
        mock_handler = Mock()
        rule = RoutingRule(RoutingRuleType.EXACT, key="level", value="error")
        config = RoutingConfig([rule])
        router = RouterHandler(mock_handler, config)

        assert router.should_handle({"level": "error"}) is True

    def test_router_handler_should_handle_false(self):
        """Test should_handle returns False when routing doesn't match."""
        mock_handler = Mock()
        rule = RoutingRule(RoutingRuleType.EXACT, key="level", value="error")
        config = RoutingConfig([rule])
        router = RouterHandler(mock_handler, config)

        assert router.should_handle({"level": "info"}) is False

    def test_router_handler_emit_with_routing_match(self):
        """Test emit delegates to handler when routing matches."""
        mock_handler = Mock()
        rule = RoutingRule(RoutingRuleType.EXACT, key="level", value="error")
        config = RoutingConfig([rule])
        router = RouterHandler(mock_handler, config)

        log_entry = {"level": "error", "message": "test"}
        log_str = '{"level": "error", "message": "test"}'

        router.emit(log_str, log_entry)
        mock_handler.emit.assert_called_once_with(log_str)

    def test_router_handler_emit_with_routing_no_match(self):
        """Test emit does NOT delegate when routing doesn't match."""
        mock_handler = Mock()
        rule = RoutingRule(RoutingRuleType.EXACT, key="level", value="error")
        config = RoutingConfig([rule])
        router = RouterHandler(mock_handler, config)

        log_entry = {"level": "info", "message": "test"}
        log_str = '{"level": "info", "message": "test"}'

        router.emit(log_str, log_entry)
        mock_handler.emit.assert_not_called()

    def test_router_handler_emit_without_log_entry(self):
        """Test emit delegates without log_entry (backward compatibility)."""
        mock_handler = Mock()
        router = RouterHandler(mock_handler)

        log_str = '{"level": "info", "message": "test"}'
        router.emit(log_str)
        mock_handler.emit.assert_called_once_with(log_str)

    def test_router_handler_emit_exception_handling(self):
        """Test emit handles exceptions gracefully."""
        mock_handler = Mock()
        mock_handler.emit.side_effect = Exception("Handler error")

        router = RouterHandler(mock_handler)
        # Should not raise exception
        router.emit('{"message": "test"}')


class TestLoggerMultipleHandlers:
    """Test Logger with multiple handlers."""

    def test_add_handler_single(self):
        """Test adding a single handler."""
        logger = Logger()
        mock_handler = Mock()
        logger.add_handler(mock_handler)

        assert len(logger.handlers) == 2  # Console + new handler

    def test_add_handler_with_routing(self):
        """Test adding handler with routing config."""
        logger = Logger()
        mock_handler = Mock()
        config = RoutingConfig([RoutingRule(RoutingRuleType.LEVEL, value="ERROR")])

        logger.add_handler(mock_handler, config)
        assert len(logger.handlers) == 2
        assert isinstance(logger.handlers[1], RouterHandler)

    def test_clear_handlers(self):
        """Test clearing all handlers."""
        logger = Logger()
        logger.clear_handlers()
        assert len(logger.handlers) == 0

    def test_remove_handler(self):
        """Test removing a specific handler."""
        logger = Logger()
        mock_handler = Mock()
        logger.add_handler(mock_handler)

        result = logger.remove_handler(logger.handlers[1])
        assert result is True
        assert len(logger.handlers) == 1

    def test_remove_handler_not_found(self):
        """Test removing non-existent handler."""
        logger = Logger()
        mock_handler = Mock()
        result = logger.remove_handler(mock_handler)
        assert result is False

    def test_logger_emit_to_all_handlers(self):
        """Test log emits to all handlers."""
        logger = Logger()
        logger.clear_handlers()

        mock_handler1 = Mock()
        mock_handler2 = Mock()
        logger.add_handler(mock_handler1)
        logger.add_handler(mock_handler2)

        logger.info("test message")

        assert mock_handler1.emit.called
        assert mock_handler2.emit.called

    def test_logger_emit_with_routing_filters(self):
        """Test log respects routing filters."""
        logger = Logger()
        logger.clear_handlers()

        # Handler 1: All logs
        mock_handler1 = Mock()
        logger.add_handler(mock_handler1)

        # Handler 2: Only errors
        mock_handler2 = Mock()
        error_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.LEVEL, value="ERROR")]
        )
        logger.add_handler(mock_handler2, error_config)

        # Log info
        logger.info("info message")
        assert mock_handler1.emit.call_count == 1
        assert mock_handler2.emit.call_count == 0

        # Log error
        logger.error("error message")
        assert mock_handler1.emit.call_count == 2
        assert mock_handler2.emit.call_count == 1

    def test_logger_emit_with_service_routing(self):
        """Test routing based on service field."""
        logger = Logger(config=LoggerConfig(service="payment"))
        logger.clear_handlers()

        # Slack handler for payment service
        mock_slack = Mock()
        payment_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")],
            name="payment_to_slack",
        )
        logger.add_handler(mock_slack, payment_config)

        # Webhook handler for auth service
        mock_webhook = Mock()
        auth_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.EXACT, key="service", value="auth")],
            name="auth_to_webhook",
        )
        logger.add_handler(mock_webhook, auth_config)

        logger.info("payment operation")
        assert mock_slack.emit.called
        assert not mock_webhook.emit.called

    def test_logger_emit_with_complex_routing(self):
        """Test complex routing with multiple rules (AND logic)."""
        logger = Logger(config=LoggerConfig(service="api"))
        logger.clear_handlers()

        # Console: All logs
        mock_console = Mock()
        logger.add_handler(mock_console)

        # Slack: Errors from payment service (AND logic)
        mock_slack = Mock()
        slack_config = RoutingConfig(
            [
                RoutingRule(RoutingRuleType.LEVEL, value="ERROR"),
                RoutingRule(RoutingRuleType.CONTAINS, key="operation", value="payment"),
            ],
            match_mode="all",
            name="critical_payments",
        )
        logger.add_handler(mock_slack, slack_config)

        # Case 1: Info log (not matched by Slack)
        logger.info("info message", operation="payment")
        assert mock_console.emit.call_count == 1
        assert mock_slack.emit.call_count == 0

        # Case 2: Error but not payment (not matched by Slack)
        logger.error("error message", operation="auth")
        assert mock_console.emit.call_count == 2
        assert mock_slack.emit.call_count == 0

        # Case 3: Error payment (matched by Slack)
        logger.error("error message", operation="payment")
        assert mock_console.emit.call_count == 3
        assert mock_slack.emit.call_count == 1

    def test_logger_emit_with_custom_function_routing(self):
        """Test routing with custom function."""
        logger = Logger()
        logger.clear_handlers()

        # Handler for logs with high priority
        mock_handler = Mock()

        def high_priority_filter(log_entry):
            return log_entry.get("priority") == "high"

        config = RoutingConfig(
            [RoutingRule(RoutingRuleType.FUNCTION, func=high_priority_filter)],
            name="high_priority",
        )
        logger.add_handler(mock_handler, config)

        logger.info("normal log", priority="low")
        assert mock_handler.emit.call_count == 0

        logger.info("important log", priority="high")
        assert mock_handler.emit.call_count == 1

    def test_logger_emit_handler_exception_isolated(self):
        """Test exception in one handler doesn't affect others."""
        logger = Logger()
        logger.clear_handlers()

        # Handler 1: Works fine
        mock_handler1 = Mock()
        logger.add_handler(mock_handler1)

        # Handler 2: Raises exception
        mock_handler2 = Mock()
        mock_handler2.emit.side_effect = Exception("Handler failure")
        logger.add_handler(mock_handler2)

        # Handler 3: Works fine
        mock_handler3 = Mock()
        logger.add_handler(mock_handler3)

        # Log a message
        logger.info("test message")

        # All handlers should be called despite exception in handler2
        assert mock_handler1.emit.called
        assert mock_handler3.emit.called
