# examples/routing_demo.py
"""
Comprehensive routing examples demonstrating different ways to route logs.
"""

import sys
from loglight import log
from loglight.handlers import ConsoleHandler, FileHandler, SlackHandler, WebhookHandler
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig
from loglight.logger import Logger
from loglight.config import LoggerConfig


def example_1_error_level_routing():
    """Example 1: Route ERROR logs to Slack, all logs to console."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Error Level Routing")
    print("="*60)

    logger = Logger()
    logger.clear_handlers()

    # Create mock handlers (in real use, these would be actual handlers)
    class MockSlackHandler:
        def emit(self, log_str):
            print(f"  [SLACK] {log_str}")

    # Add Slack handler for errors only
    slack_config = RoutingConfig([
        RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
    ])
    logger.add_handler(MockSlackHandler(), slack_config)

    # Add console handler for all
    logger.add_handler(ConsoleHandler())

    print("\nLogging messages:")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    print("\nNote: Error went to Slack, all went to Console")


def example_2_service_routing():
    """Example 2: Route different services to different handlers."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Service-Based Routing")
    print("="*60)

    class MockPaymentHandler:
        def emit(self, log_str):
            print(f"  [PAYMENT_SLACK] {log_str}")

    class MockAuthHandler:
        def emit(self, log_str):
            print(f"  [AUTH_WEBHOOK] {log_str}")

    # Create loggers for different services
    payment_logger = Logger(config=LoggerConfig(service="payment"))
    auth_logger = Logger(config=LoggerConfig(service="auth"))

    # Clear and setup handlers
    for logger in [payment_logger, auth_logger]:
        logger.clear_handlers()

    # Payment → Slack
    payment_config = RoutingConfig([
        RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
    ])
    payment_logger.add_handler(MockPaymentHandler(), payment_config)

    # Auth → Webhook
    auth_config = RoutingConfig([
        RoutingRule(RoutingRuleType.EXACT, key="service", value="auth")
    ])
    auth_logger.add_handler(MockAuthHandler(), auth_config)

    # All → Console
    for logger in [payment_logger, auth_logger]:
        logger.add_handler(ConsoleHandler())

    print("\nLogging messages:")
    payment_logger.info("Payment processed")
    auth_logger.info("User authenticated")
    print("\nNote: Payment went to Payment handler, Auth to Auth handler, both to Console")


def example_3_regex_routing():
    """Example 3: Route based on message patterns."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Regex-Based Routing")
    print("="*60)

    class MockDBHandler:
        def emit(self, log_str):
            print(f"  [DB_ALERTS] {log_str}")

    class MockAPIHandler:
        def emit(self, log_str):
            print(f"  [API_ALERTS] {log_str}")

    logger = Logger()
    logger.clear_handlers()

    # Database errors
    db_config = RoutingConfig([
        RoutingRule(
            RoutingRuleType.REGEX,
            key="message",
            pattern=r"(?i)database|sql|query|connection"
        )
    ])
    logger.add_handler(MockDBHandler(), db_config)

    # API errors
    api_config = RoutingConfig([
        RoutingRule(
            RoutingRuleType.REGEX,
            key="message",
            pattern=r"(?i)api|endpoint|http|timeout"
        )
    ])
    logger.add_handler(MockAPIHandler(), api_config)

    # All
    logger.add_handler(ConsoleHandler())

    print("\nLogging messages:")
    logger.error("Database connection failed")
    logger.error("API endpoint timeout")
    logger.error("General error")
    print("\nNote: DB error to DB handler, API error to API handler, all to Console")


def example_4_complex_routing():
    """Example 4: Complex routing with AND/OR logic."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Complex Routing (AND/OR Logic)")
    print("="*60)

    class MockCriticalHandler:
        def emit(self, log_str):
            print(f"  [CRITICAL_ALERT] {log_str}")

    logger = Logger(config=LoggerConfig(service="payment"))
    logger.clear_handlers()

    # Critical payments: ERROR level AND payment service (AND mode)
    critical_config = RoutingConfig(
        [
            RoutingRule(RoutingRuleType.LEVEL, value="ERROR"),
            RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"),
        ],
        match_mode="all",
        name="critical_payments"
    )
    logger.add_handler(MockCriticalHandler(), critical_config)

    logger.add_handler(ConsoleHandler())

    print("\nLogging messages:")
    logger.info("Payment processed successfully")
    logger.error("Auth service error")  # Error but not payment
    logger.error("Payment failed")  # Error AND payment
    print("\nNote: Only ERROR from payment service goes to Critical handler")


def example_5_custom_function_routing():
    """Example 5: Routing with custom functions."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Custom Function Routing")
    print("="*60)

    class MockHighPriorityHandler:
        def emit(self, log_str):
            print(f"  [HIGH_PRIORITY_QUEUE] {log_str}")

    logger = Logger()
    logger.clear_handlers()

    def is_high_priority(log_entry):
        """Custom filter function."""
        return log_entry.get("priority") == "high"

    # High priority only
    priority_config = RoutingConfig([
        RoutingRule(RoutingRuleType.FUNCTION, func=is_high_priority)
    ])
    logger.add_handler(MockHighPriorityHandler(), priority_config)

    logger.add_handler(ConsoleHandler())

    print("\nLogging messages:")
    logger.info("Normal operation", priority="normal")
    logger.info("Important task", priority="high")
    logger.error("Critical issue", priority="high")
    print("\nNote: Only high priority logs go to Priority handler")


def example_6_sensitive_data_exclusion():
    """Example 6: Exclude sensitive data from external systems."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Sensitive Data Exclusion")
    print("="*60)

    class MockExternalHandler:
        def emit(self, log_str):
            print(f"  [EXTERNAL_MONITORING] {log_str}")

    logger = Logger()
    logger.clear_handlers()

    def is_not_sensitive(log_entry):
        """Check if log doesn't contain sensitive words."""
        message = log_entry.get("message", "").lower()
        sensitive_words = ["password", "token", "secret", "api_key", "ssn"]
        return not any(word in message for word in sensitive_words)

    # External: Non-sensitive logs only
    external_config = RoutingConfig([
        RoutingRule(RoutingRuleType.FUNCTION, func=is_not_sensitive)
    ])
    logger.add_handler(MockExternalHandler(), external_config)

    logger.add_handler(ConsoleHandler())

    print("\nLogging messages:")
    logger.info("User created successfully")
    logger.error("Invalid password provided")
    logger.warning("Request timeout")
    print("\nNote: Sensitive logs stay in Console, non-sensitive go to External")


def example_7_multi_rule_or_logic():
    """Example 7: Multiple rules with OR logic (any mode)."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Multiple Rules - OR Logic (Any Mode)")
    print("="*60)

    class MockAlertHandler:
        def emit(self, log_str):
            print(f"  [ALERT] {log_str}")

    logger = Logger()
    logger.clear_handlers()

    # Alert on: payment OR auth service (OR logic)
    alert_config = RoutingConfig(
        [
            RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"),
            RoutingRule(RoutingRuleType.EXACT, key="service", value="auth"),
        ],
        match_mode="any",  # OR logic
        name="critical_services"
    )
    logger.add_handler(MockAlertHandler(), alert_config)

    logger.add_handler(ConsoleHandler())

    print("\nLogging messages:")
    logger.info("Payment processed", service="payment")
    logger.info("User authenticated", service="auth")
    logger.info("Cache cleared", service="cache")
    print("\nNote: Payment AND Auth logs go to Alert handler")


def example_8_monitoring_levels():
    """Example 8: Different handlers for different alert levels."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Monitoring Levels")
    print("="*60)

    class MockWarningHandler:
        def emit(self, log_str):
            print(f"  [WARN_MONITOR] {log_str}")

    class MockErrorHandler:
        def emit(self, log_str):
            print(f"  [ERROR_MONITOR] {log_str}")

    logger = Logger()
    logger.clear_handlers()

    # Warning and above
    warn_config = RoutingConfig([
        RoutingRule(RoutingRuleType.LEVEL, value="WARNING")
    ])
    logger.add_handler(MockWarningHandler(), warn_config)

    # Error and above (stricter)
    error_config = RoutingConfig([
        RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
    ])
    logger.add_handler(MockErrorHandler(), error_config)

    logger.add_handler(ConsoleHandler())

    print("\nLogging messages:")
    logger.info("Normal operation")
    logger.warning("High memory usage")
    logger.error("Database unavailable")
    logger.critical("System failure")
    print("\nNote: WARNING goes to Warn Monitor, ERROR/CRITICAL go to both monitors")


if __name__ == "__main__":
    # Run all examples
    example_1_error_level_routing()
    example_2_service_routing()
    example_3_regex_routing()
    example_4_complex_routing()
    example_5_custom_function_routing()
    example_6_sensitive_data_exclusion()
    example_7_multi_rule_or_logic()
    example_8_monitoring_levels()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)

