# tests/test_routing_scenarios.py
"""
Real-world routing scenario tests.
"""

import json
from unittest.mock import Mock
import pytest
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig
from loglight.logger import Logger
from loglight.config import LoggerConfig


class TestRealWorldScenarios:
    """Test real-world routing scenarios."""

    def test_scenario_slack_errors_webhook_all(self):
        """
        Scenario: Route ERROR/CRITICAL logs to Slack, all logs to Webhook.
        """
        logger = Logger()
        logger.clear_handlers()

        slack_logs = []
        webhook_logs = []

        def capture_slack(log_str):
            slack_logs.append(json.loads(log_str))

        def capture_webhook(log_str):
            webhook_logs.append(json.loads(log_str))

        slack_handler = Mock()
        slack_handler.emit = capture_slack
        webhook_handler = Mock()
        webhook_handler.emit = capture_webhook

        # Slack: Only ERROR and CRITICAL
        slack_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.LEVEL, value="ERROR")],
            name="slack_errors"
        )
        logger.add_handler(slack_handler, slack_config)

        # Webhook: All logs
        logger.add_handler(webhook_handler)

        # Send logs
        logger.info("info message")
        logger.error("error message")
        logger.critical("critical message")

        # Verify Slack got ERROR and CRITICAL
        assert len(slack_logs) == 2
        assert slack_logs[0]["level"] == "error"
        assert slack_logs[1]["level"] == "critical"

        # Verify Webhook got all
        assert len(webhook_logs) == 3

    def test_scenario_service_based_routing(self):
        """
        Scenario: Different services route to different handlers.
        - payment service -> Slack
        - auth service -> Webhook
        - all services -> Console
        """
        # Create loggers for different services
        payment_logger = Logger(config=LoggerConfig(service="payment"))
        auth_logger = Logger(config=LoggerConfig(service="auth"))
        general_logger = Logger()

        # Use same handlers for all
        payment_logger.clear_handlers()
        auth_logger.clear_handlers()
        general_logger.clear_handlers()

        payment_logs = []
        auth_logs = []
        console_logs = []

        def capture_payment(log_str):
            payment_logs.append(json.loads(log_str))

        def capture_auth(log_str):
            auth_logs.append(json.loads(log_str))

        def capture_console(log_str):
            console_logs.append(json.loads(log_str))

        slack_handler = Mock()
        slack_handler.emit = capture_payment
        webhook_handler = Mock()
        webhook_handler.emit = capture_auth
        console_handler = Mock()
        console_handler.emit = capture_console

        # Payment service handler
        payment_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")],
            name="payment_logs"
        )
        payment_logger.add_handler(slack_handler, payment_config)

        # Auth service handler
        auth_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.EXACT, key="service", value="auth")],
            name="auth_logs"
        )
        auth_logger.add_handler(webhook_handler, auth_config)

        # Console handler for all
        general_logger.add_handler(console_handler)

        # Log from different services
        payment_logger.info("payment processed")
        auth_logger.info("user authenticated")

        assert len(payment_logs) == 1
        assert len(auth_logs) == 1

    def test_scenario_regex_based_routing(self):
        """
        Scenario: Route logs based on message patterns.
        - Database errors -> specialized handler
        - API errors -> another handler
        """
        logger = Logger()
        logger.clear_handlers()

        db_logs = []
        api_logs = []
        console_logs = []

        def capture_db(log_str):
            db_logs.append(json.loads(log_str))

        def capture_api(log_str):
            api_logs.append(json.loads(log_str))

        def capture_console(log_str):
            console_logs.append(json.loads(log_str))

        db_handler = Mock()
        db_handler.emit = capture_db
        api_handler = Mock()
        api_handler.emit = capture_api
        console_handler = Mock()
        console_handler.emit = capture_console

        # Database error handler
        db_config = RoutingConfig(
            [RoutingRule(
                RoutingRuleType.REGEX,
                key="message",
                pattern=r"(?i)database|sql|query"
            )],
            name="db_errors"
        )
        logger.add_handler(db_handler, db_config)

        # API error handler
        api_config = RoutingConfig(
            [RoutingRule(
                RoutingRuleType.REGEX,
                key="message",
                pattern=r"(?i)api|endpoint|http"
            )],
            name="api_errors"
        )
        logger.add_handler(api_handler, api_config)

        # Console handler for all
        logger.add_handler(console_handler)

        # Send logs
        logger.error("Database connection failed")
        logger.error("API endpoint timeout")
        logger.error("General error")

        assert len(db_logs) == 1
        assert len(api_logs) == 1
        assert len(console_logs) == 3

    def test_scenario_priority_based_routing(self):
        """
        Scenario: Route logs based on custom priority field.
        - High priority -> Slack
        - Medium priority -> Webhook
        - Low priority -> Console
        """
        logger = Logger()
        logger.clear_handlers()

        high_logs = []
        medium_logs = []
        low_logs = []

        def capture_high(log_str):
            high_logs.append(json.loads(log_str))

        def capture_medium(log_str):
            medium_logs.append(json.loads(log_str))

        def capture_low(log_str):
            low_logs.append(json.loads(log_str))

        high_handler = Mock()
        high_handler.emit = capture_high
        medium_handler = Mock()
        medium_handler.emit = capture_medium
        low_handler = Mock()
        low_handler.emit = capture_low

        # High priority handler
        high_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.EXACT, key="priority", value="high")],
            name="high_priority"
        )
        logger.add_handler(high_handler, high_config)

        # Medium priority handler
        medium_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.EXACT, key="priority", value="medium")],
            name="medium_priority"
        )
        logger.add_handler(medium_handler, medium_config)

        # Low priority handler
        low_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.EXACT, key="priority", value="low")],
            name="low_priority"
        )
        logger.add_handler(low_handler, low_config)

        logger.error("Critical payment failed", priority="high")
        logger.warning("Slow API response", priority="medium")
        logger.info("User logged in", priority="low")

        assert len(high_logs) == 1
        assert len(medium_logs) == 1
        assert len(low_logs) == 1

    def test_scenario_error_level_and_service_combination(self):
        """
        Scenario: Route logs based on BOTH error level AND service.
        - ERROR/CRITICAL from payment service -> Slack
        - ERROR/CRITICAL from auth service -> Webhook
        - All other logs -> Console
        """
        payment_logger = Logger(config=LoggerConfig(service="payment"))
        auth_logger = Logger(config=LoggerConfig(service="auth"))
        general_logger = Logger()

        for logger in [payment_logger, auth_logger, general_logger]:
            logger.clear_handlers()

        slack_logs = []
        webhook_logs = []
        console_logs = []

        def capture_slack(log_str):
            slack_logs.append(json.loads(log_str))

        def capture_webhook(log_str):
            webhook_logs.append(json.loads(log_str))

        def capture_console(log_str):
            console_logs.append(json.loads(log_str))

        slack_handler = Mock()
        slack_handler.emit = capture_slack
        webhook_handler = Mock()
        webhook_handler.emit = capture_webhook
        console_handler = Mock()
        console_handler.emit = capture_console

        # Slack: ERROR+ from payment
        slack_config = RoutingConfig(
            [
                RoutingRule(RoutingRuleType.LEVEL, value="ERROR"),
                RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"),
            ],
            match_mode="all",
            name="payment_errors_to_slack"
        )
        payment_logger.add_handler(slack_handler, slack_config)

        # Webhook: ERROR+ from auth
        webhook_config = RoutingConfig(
            [
                RoutingRule(RoutingRuleType.LEVEL, value="ERROR"),
                RoutingRule(RoutingRuleType.EXACT, key="service", value="auth"),
            ],
            match_mode="all",
            name="auth_errors_to_webhook"
        )
        auth_logger.add_handler(webhook_handler, webhook_config)

        # Console: All
        for logger in [payment_logger, auth_logger, general_logger]:
            logger.add_handler(console_handler)

        # Log various messages
        payment_logger.info("payment info")
        payment_logger.error("payment error")

        auth_logger.info("auth info")
        auth_logger.error("auth error")

        # Verify routing
        assert len(slack_logs) == 1  # payment error only
        assert len(webhook_logs) == 1  # auth error only
        assert len(console_logs) == 4  # all logs

    def test_scenario_exclusion_rules(self):
        """
        Scenario: Send all logs EXCEPT sensitive ones to external system.
        Uses custom function to exclude sensitive logs.
        """
        logger = Logger()
        logger.clear_handlers()

        external_logs = []
        sensitive_logs = []

        def capture_external(log_str):
            external_logs.append(json.loads(log_str))

        def capture_sensitive(log_str):
            sensitive_logs.append(json.loads(log_str))

        external_handler = Mock()
        external_handler.emit = capture_external
        sensitive_handler = Mock()
        sensitive_handler.emit = capture_sensitive

        def is_sensitive(log_entry):
            """Check if log contains sensitive data."""
            message = log_entry.get("message", "").lower()
            return any(word in message for word in ["password", "secret", "token", "key"])

        # External handler: Non-sensitive logs only
        external_config = RoutingConfig(
            [RoutingRule(
                RoutingRuleType.FUNCTION,
                func=lambda log: not is_sensitive(log)
            )],
            name="external_safe_logs"
        )
        logger.add_handler(external_handler, external_config)

        # Sensitive handler: Sensitive logs only
        sensitive_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.FUNCTION, func=is_sensitive)],
            name="sensitive_logs"
        )
        logger.add_handler(sensitive_handler, sensitive_config)

        logger.info("User logged in")
        logger.error("Password reset failed")
        logger.warning("API call timeout")
        logger.error("Invalid secret provided")

        # Verify routing
        assert len(external_logs) == 2
        assert len(sensitive_logs) == 2

    def test_scenario_multi_handler_per_route(self):
        """
        Scenario: Same log can go to multiple handlers with different routes.
        - All ERROR logs go to Slack AND Email
        - All logs go to File
        """
        logger = Logger()
        logger.clear_handlers()

        slack_logs = []
        email_logs = []
        file_logs = []

        def capture_slack(log_str):
            slack_logs.append(json.loads(log_str))

        def capture_email(log_str):
            email_logs.append(json.loads(log_str))

        def capture_file(log_str):
            file_logs.append(json.loads(log_str))

        slack_handler = Mock()
        slack_handler.emit = capture_slack
        email_handler = Mock()
        email_handler.emit = capture_email
        file_handler = Mock()
        file_handler.emit = capture_file

        # Slack: Errors only
        slack_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.LEVEL, value="ERROR")],
            name="errors_to_slack"
        )
        logger.add_handler(slack_handler, slack_config)

        # Email: Errors only
        email_config = RoutingConfig(
            [RoutingRule(RoutingRuleType.LEVEL, value="ERROR")],
            name="errors_to_email"
        )
        logger.add_handler(email_handler, email_config)

        # File: All logs
        logger.add_handler(file_handler)

        logger.info("info message")
        logger.error("error message")

        # Verify
        assert len(slack_logs) == 1
        assert len(email_logs) == 1
        assert len(file_logs) == 2

