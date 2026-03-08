# tests/test_routing.py
"""
Unit tests for the loglight routing system.

Tests cover routing rules and configurations.
"""

import pytest
from unittest.mock import Mock
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig


class TestRoutingRule:
    """Test individual routing rules."""

    def test_exact_match_success(self):
        """Test EXACT rule matching with matching value."""
        rule = RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
        log_entry = {"service": "payment", "message": "test"}
        assert rule.matches(log_entry) is True

    def test_exact_match_failure(self):
        """Test EXACT rule matching with non-matching value."""
        rule = RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
        log_entry = {"service": "auth", "message": "test"}
        assert rule.matches(log_entry) is False

    def test_exact_match_missing_key(self):
        """Test EXACT rule when key is missing."""
        rule = RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
        log_entry = {"message": "test"}
        assert rule.matches(log_entry) is False

    def test_contains_match_success(self):
        """Test CONTAINS rule matching."""
        rule = RoutingRule(RoutingRuleType.CONTAINS, key="message", value="error")
        log_entry = {"message": "database error occurred"}
        assert rule.matches(log_entry) is True

    def test_contains_match_failure(self):
        """Test CONTAINS rule when substring not found."""
        rule = RoutingRule(RoutingRuleType.CONTAINS, key="message", value="error")
        log_entry = {"message": "success message"}
        assert rule.matches(log_entry) is False

    def test_contains_case_sensitive(self):
        """Test CONTAINS is case sensitive."""
        rule = RoutingRule(RoutingRuleType.CONTAINS, key="message", value="ERROR")
        log_entry = {"message": "error occurred"}
        assert rule.matches(log_entry) is False

    def test_regex_match_success(self):
        """Test REGEX rule with matching pattern."""
        rule = RoutingRule(RoutingRuleType.REGEX, key="user_id", pattern=r"user_\d+")
        log_entry = {"user_id": "user_123"}
        assert rule.matches(log_entry) is True

    def test_regex_match_failure(self):
        """Test REGEX rule with non-matching pattern."""
        rule = RoutingRule(RoutingRuleType.REGEX, key="user_id", pattern=r"user_\d+")
        log_entry = {"user_id": "admin_123"}
        assert rule.matches(log_entry) is False

    def test_regex_match_invalid_pattern(self):
        """Test REGEX rule with invalid regex pattern."""
        rule = RoutingRule(RoutingRuleType.REGEX, key="message", pattern=r"[invalid(")
        log_entry = {"message": "test"}
        assert rule.matches(log_entry) is False

    def test_function_match_success(self):
        """Test FUNCTION rule with matching function."""
        def custom_filter(log_entry):
            return log_entry.get("level") == "error"

        rule = RoutingRule(RoutingRuleType.FUNCTION, func=custom_filter)
        log_entry = {"level": "error", "message": "test"}
        assert rule.matches(log_entry) is True

    def test_function_match_failure(self):
        """Test FUNCTION rule with non-matching function."""
        def custom_filter(log_entry):
            return log_entry.get("level") == "error"

        rule = RoutingRule(RoutingRuleType.FUNCTION, func=custom_filter)
        log_entry = {"level": "info", "message": "test"}
        assert rule.matches(log_entry) is False

    def test_function_exception_handling(self):
        """Test FUNCTION rule when function raises exception."""
        def bad_filter(log_entry):
            raise ValueError("Filter error")

        rule = RoutingRule(RoutingRuleType.FUNCTION, func=bad_filter)
        log_entry = {"message": "test"}
        assert rule.matches(log_entry) is False

    def test_level_match_error(self):
        """Test LEVEL rule for ERROR threshold."""
        rule = RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
        assert rule.matches({"level": "critical"}) is True
        assert rule.matches({"level": "error"}) is True
        assert rule.matches({"level": "warning"}) is False
        assert rule.matches({"level": "info"}) is False

    def test_level_match_warning(self):
        """Test LEVEL rule for WARNING threshold."""
        rule = RoutingRule(RoutingRuleType.LEVEL, value="WARNING")
        assert rule.matches({"level": "critical"}) is True
        assert rule.matches({"level": "error"}) is True
        assert rule.matches({"level": "warning"}) is True
        assert rule.matches({"level": "info"}) is False

    def test_level_match_case_insensitive(self):
        """Test LEVEL rule is case insensitive."""
        rule = RoutingRule(RoutingRuleType.LEVEL, value="error")
        assert rule.matches({"level": "ERROR"}) is True
        assert rule.matches({"level": "Error"}) is True

    def test_level_default_log_level(self):
        """Test LEVEL rule with missing log level."""
        rule = RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
        assert rule.matches({}) is False

    def test_rule_name(self):
        """Test rule naming."""
        rule1 = RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
        assert "exact" in rule1.name

        rule2 = RoutingRule(
            RoutingRuleType.EXACT, key="service", value="payment", name="payment_rule"
        )
        assert rule2.name == "payment_rule"


class TestRoutingConfig:
    """Test routing configurations."""

    def test_empty_rules_route_all(self):
        """Test config with no rules routes all logs."""
        config = RoutingConfig()
        log_entry = {"level": "info", "message": "test"}
        assert config.should_route(log_entry) is True

    def test_single_rule_any_mode(self):
        """Test config with single rule in any mode."""
        rule = RoutingRule(RoutingRuleType.EXACT, key="level", value="error")
        config = RoutingConfig([rule], match_mode="any")
        assert config.should_route({"level": "error"}) is True
        assert config.should_route({"level": "info"}) is False

    def test_multiple_rules_any_mode(self):
        """Test multiple rules with OR logic (any mode)."""
        rule1 = RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
        rule2 = RoutingRule(RoutingRuleType.EXACT, key="service", value="auth")
        config = RoutingConfig([rule1, rule2], match_mode="any")

        assert config.should_route({"service": "payment"}) is True
        assert config.should_route({"service": "auth"}) is True
        assert config.should_route({"service": "user"}) is False

    def test_multiple_rules_all_mode(self):
        """Test multiple rules with AND logic (all mode)."""
        rule1 = RoutingRule(RoutingRuleType.EXACT, key="level", value="error")
        rule2 = RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
        config = RoutingConfig([rule1, rule2], match_mode="all")

        assert config.should_route({"level": "error", "service": "payment"}) is True
        assert config.should_route({"level": "error", "service": "auth"}) is False
        assert config.should_route({"level": "info", "service": "payment"}) is False

    def test_add_rule_method(self):
        """Test adding rules dynamically."""
        config = RoutingConfig()
        assert len(config.rules) == 0

        rule = RoutingRule(RoutingRuleType.EXACT, key="level", value="error")
        config.add_rule(rule)
        assert len(config.rules) == 1
        assert config.should_route({"level": "error"}) is True

    def test_add_rule_method_chaining(self):
        """Test method chaining with add_rule."""
        config = (
            RoutingConfig()
            .add_rule(RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"))
            .add_rule(RoutingRule(RoutingRuleType.LEVEL, value="ERROR"))
        )
        assert len(config.rules) == 2

    def test_routing_config_naming(self):
        """Test routing config naming."""
        config1 = RoutingConfig()
        assert config1.name is None

        config2 = RoutingConfig(name="error_routes")
        assert config2.name == "error_routes"

