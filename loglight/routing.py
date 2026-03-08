# loglight/routing.py
"""
Handler routing mechanism for loglight.

Allows flexible routing of logs to different handlers based on configurable rules.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class RoutingRuleType(Enum):
    """Types of routing rules."""

    EXACT = "exact"  # Exact match of a key-value pair
    CONTAINS = "contains"  # Value contains a substring
    REGEX = "regex"  # Value matches a regex pattern
    FUNCTION = "function"  # Custom function returns True
    LEVEL = "level"  # Log level threshold


class RoutingRule:
    """Represents a single routing rule for log filtering."""

    def __init__(
        self,
        rule_type: RoutingRuleType,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        pattern: Optional[str] = None,
        func: Optional[Callable[[Dict], bool]] = None,
        name: Optional[str] = None,
    ):
        """Initialize a routing rule.

        Args:
            rule_type: Type of rule (EXACT, CONTAINS, REGEX, FUNCTION, LEVEL)
            key: The key in log_entry to check (not needed for FUNCTION)
            value: The expected value for EXACT matching or level for LEVEL
            pattern: Regex pattern for REGEX matching
            func: Custom function for FUNCTION matching
            name: Optional name for the rule (for debugging)
        """
        self.rule_type = rule_type
        self.key = key
        self.value = value
        self.pattern = pattern
        self.func = func
        self.name = name or f"{rule_type.value}_{key}"

    def matches(self, log_entry: Dict) -> bool:
        """Check if the log entry matches this rule.

        Args:
            log_entry: The log entry dictionary

        Returns:
            True if the log entry matches, False otherwise
        """
        if self.rule_type == RoutingRuleType.EXACT:
            return log_entry.get(self.key) == self.value

        elif self.rule_type == RoutingRuleType.CONTAINS:
            entry_value = log_entry.get(self.key, "")
            return str(self.value) in str(entry_value)

        elif self.rule_type == RoutingRuleType.REGEX:
            import re

            entry_value = log_entry.get(self.key, "")
            try:
                return bool(re.search(self.pattern, str(entry_value)))
            except Exception:
                return False

        elif self.rule_type == RoutingRuleType.FUNCTION:
            try:
                return self.func(log_entry)
            except Exception:
                return False

        elif self.rule_type == RoutingRuleType.LEVEL:
            levels = {
                "DEBUG": 10,
                "INFO": 20,
                "WARNING": 30,
                "ERROR": 40,
                "CRITICAL": 50,
            }
            log_level = log_entry.get("level", "INFO").upper()
            log_level_value = levels.get(log_level, 20)
            threshold_value = (
                levels.get(self.value.upper(), 20)
                if isinstance(self.value, str)
                else self.value
            )
            return log_level_value >= threshold_value

        return False

    def __repr__(self) -> str:
        return f"RoutingRule({self.name})"


class RoutingConfig:
    """Configuration for routing logs to handlers based on rules."""

    def __init__(
        self,
        rules: Optional[List[RoutingRule]] = None,
        match_mode: str = "any",
        name: Optional[str] = None,
    ):
        """Initialize a routing configuration.

        Args:
            rules: List of RoutingRule objects to match
            match_mode: "any" (OR logic) or "all" (AND logic) for multiple rules
            name: Optional name for this routing config
        """
        self.rules = rules or []
        self.match_mode = match_mode  # "any" or "all"
        self.name = name

    def should_route(self, log_entry: Dict) -> bool:
        """Check if the log entry should be routed based on rules.

        Args:
            log_entry: The log entry dictionary

        Returns:
            True if the log entry matches the routing rules, False otherwise
        """
        if not self.rules:
            # No rules means route everything
            return True

        if self.match_mode == "any":
            # OR logic: match if ANY rule matches
            return any(rule.matches(log_entry) for rule in self.rules)
        else:
            # AND logic: match only if ALL rules match
            return all(rule.matches(log_entry) for rule in self.rules)

    def add_rule(self, rule: RoutingRule) -> "RoutingConfig":
        """Add a routing rule.

        Args:
            rule: RoutingRule to add

        Returns:
            Self for method chaining
        """
        self.rules.append(rule)
        return self

    def __repr__(self) -> str:
        return f"RoutingConfig({self.name or 'unnamed'}, rules={len(self.rules)})"


class RouterHandler:
    """Handler wrapper that routes logs based on RoutingConfig."""

    def __init__(self, handler, routing_config: Optional[RoutingConfig] = None):
        """Initialize a handler with routing configuration.

        Args:
            handler: The actual handler to use
            routing_config: RoutingConfig to determine when to use this handler
        """
        self.handler = handler
        self.routing_config = (
            routing_config or RoutingConfig()
        )  # Default: route everything

    def should_handle(self, log_entry: Dict) -> bool:
        """Check if this handler should process the log entry.

        Args:
            log_entry: The log entry dictionary

        Returns:
            True if the handler should process this log
        """
        return self.routing_config.should_route(log_entry)

    def emit(self, log_str: str, log_entry: Optional[Dict] = None):
        """Emit the log if routing rules match.

        Args:
            log_str: The serialized log string
            log_entry: The log entry dictionary (for routing checks)
        """
        # If we have the log_entry, use it for routing decision
        if log_entry is not None:
            if not self.should_handle(log_entry):
                return

        # Delegate to the actual handler
        try:
            if hasattr(self.handler, "emit"):
                self.handler.emit(log_str)
        except Exception as e:
            # Log to stderr but don't raise
            import sys

            print(
                f"Error in handler {self.handler.__class__.__name__}: {e}",
                file=sys.stderr,
            )

    def __repr__(self) -> str:
        return f"RouterHandler({self.handler.__class__.__name__}, routing={self.routing_config.name or 'default'})"
