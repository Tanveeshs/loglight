# Handler Routing Guide

## Overview

The loglight routing system allows you to flexibly route different types of logs to different handlers based on configurable rules. Instead of sending all logs to a single handler, you can now define rules to determine which logs should go where.

## Quick Example

```python
from loglight import log
from loglight.handlers import SlackHandler, WebhookHandler, ConsoleHandler
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig
from loglight.config import LoggerConfig

# Initialize logger
logger = log

# Clear default handlers
logger.clear_handlers()

# Add Slack handler for errors only
slack_config = RoutingConfig([
    RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
])
logger.add_handler(
    SlackHandler(webhook_url="https://hooks.slack.com/..."),
    slack_config
)

# Add Webhook handler for payment service
payment_config = RoutingConfig([
    RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
])
logger.add_handler(
    WebhookHandler(url="https://webhook.example.com/logs"),
    payment_config
)

# Add Console handler for all logs
logger.add_handler(ConsoleHandler())

# Now logs are routed based on your configuration!
logger.info("General message")  # → Console only
logger.error("Error happened")  # → Slack + Console
logger.info("Payment processed", service="payment")  # → Webhook + Console
```

## Routing Rules

Routing rules determine if a log entry should be sent to a handler.

### Rule Types

#### 1. EXACT Match
Match when a field equals a specific value.

```python
rule = RoutingRule(
    RoutingRuleType.EXACT,
    key="service",
    value="payment"
)

# Matches: {"service": "payment", ...}
# Doesn't match: {"service": "auth", ...}
```

#### 2. CONTAINS Match
Match when a field contains a substring.

```python
rule = RoutingRule(
    RoutingRuleType.CONTAINS,
    key="message",
    value="database"
)

# Matches: {"message": "database connection failed"}
# Doesn't match: {"message": "api error"}
```

#### 3. REGEX Match
Match when a field matches a regex pattern (case-sensitive).

```python
rule = RoutingRule(
    RoutingRuleType.REGEX,
    key="user_id",
    pattern=r"^user_\d+$"
)

# Matches: {"user_id": "user_123"}
# Doesn't match: {"user_id": "admin_123"}
```

#### 4. LEVEL Match
Match based on log level threshold. Matches the specified level and above.

```python
rule = RoutingRule(
    RoutingRuleType.LEVEL,
    value="ERROR"
)

# Matches: ERROR, CRITICAL
# Doesn't match: WARNING, INFO, DEBUG
```

**Log Level Hierarchy:**
```
DEBUG (10) < INFO (20) < WARNING (30) < ERROR (40) < CRITICAL (50)
```

#### 5. FUNCTION Match
Match using a custom function that operates on the entire log entry.

```python
def is_high_priority(log_entry):
    return log_entry.get("priority") == "high"

rule = RoutingRule(
    RoutingRuleType.FUNCTION,
    func=is_high_priority
)

# Matches: {"priority": "high", ...}
# Doesn't match: {"priority": "low", ...}
```

## Routing Configurations

A `RoutingConfig` combines multiple rules with a match mode.

### Single Rule Config

```python
config = RoutingConfig([
    RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
])
logger.add_handler(slack_handler, config)
```

### Multiple Rules - ANY Mode (OR Logic)

Match if ANY rule matches:

```python
config = RoutingConfig(
    [
        RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"),
        RoutingRule(RoutingRuleType.EXACT, key="service", value="auth"),
    ],
    match_mode="any",  # Default
    name="payment_or_auth"
)

# Matches: service is "payment" OR "auth"
# Routes to: payment AND auth services
```

### Multiple Rules - ALL Mode (AND Logic)

Match only if ALL rules match:

```python
config = RoutingConfig(
    [
        RoutingRule(RoutingRuleType.LEVEL, value="ERROR"),
        RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"),
    ],
    match_mode="all",
    name="critical_payments"
)

# Matches: level is ERROR AND service is "payment"
# Routes to: only ERROR level messages from payment service
```

### Method Chaining

Build configs fluently:

```python
config = (
    RoutingConfig(name="api_errors")
    .add_rule(RoutingRule(RoutingRuleType.LEVEL, value="ERROR"))
    .add_rule(RoutingRule(RoutingRuleType.CONTAINS, key="endpoint", value="/api"))
)
```

## Working with Handlers

### Adding Handlers

```python
# Add handler without routing (receives all logs)
logger.add_handler(ConsoleHandler())

# Add handler with routing config
logger.add_handler(
    SlackHandler(webhook_url="..."),
    RoutingConfig([RoutingRule(RoutingRuleType.LEVEL, value="ERROR")])
)
```

### Removing Handlers

```python
# Remove specific handler
logger.remove_handler(handler_instance)

# Clear all handlers
logger.clear_handlers()
```

## Real-World Examples

### Example 1: Error Alerts to Slack, All Logs to File

```python
from loglight import log
from loglight.handlers import SlackHandler, FileHandler
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig

log.clear_handlers()

# Slack: Errors only
slack_config = RoutingConfig([
    RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
])
log.add_handler(
    SlackHandler(webhook_url="https://hooks.slack.com/..."),
    slack_config
)

# File: All logs
log.add_handler(FileHandler(filepath="/var/log/app.log"))

log.info("User created")  # → File only
log.error("Connection failed")  # → Slack + File
```

### Example 2: Service-Based Routing

```python
from loglight import log
from loglight.handlers import SlackHandler, WebhookHandler
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig
from loglight.config import LoggerConfig

log.clear_handlers()

# Payment service → Slack
payment_config = RoutingConfig([
    RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
])
log.add_handler(
    SlackHandler(webhook_url="https://hooks.slack.com/payment"),
    payment_config
)

# Auth service → Webhook
auth_config = RoutingConfig([
    RoutingRule(RoutingRuleType.EXACT, key="service", value="auth")
])
log.add_handler(
    WebhookHandler(url="https://webhook.example.com/auth"),
    auth_config
)

# All services → Console
log.add_handler(ConsoleHandler())

# Usage with service config
payment_logger = Logger(config=LoggerConfig(service="payment"))
payment_logger.handlers = log.handlers  # Share handlers

auth_logger = Logger(config=LoggerConfig(service="auth"))
auth_logger.handlers = log.handlers

payment_logger.error("Payment failed")  # → Slack + Console
auth_logger.error("Auth failed")  # → Webhook + Console
```

### Example 3: Message Pattern Based Routing

```python
import re
from loglight import log
from loglight.handlers import SlackHandler, FileHandler
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig

log.clear_handlers()

# Database errors → Slack
db_config = RoutingConfig([
    RoutingRule(
        RoutingRuleType.REGEX,
        key="message",
        pattern=r"(?i)database|sql|query|connection"
    )
])
log.add_handler(
    SlackHandler(webhook_url="https://hooks.slack.com/db"),
    db_config
)

# API errors → Different Slack channel
api_config = RoutingConfig([
    RoutingRule(
        RoutingRuleType.REGEX,
        key="message",
        pattern=r"(?i)api|endpoint|http|timeout"
    )
])
log.add_handler(
    SlackHandler(webhook_url="https://hooks.slack.com/api"),
    api_config
)

# All → File
log.add_handler(FileHandler(filepath="/var/log/app.log"))

log.error("Database connection failed")  # → DB Slack + File
log.error("API endpoint timeout")  # → API Slack + File
```

### Example 4: Complex Business Logic

```python
from loglight import log
from loglight.handlers import SlackHandler, EmailHandler, FileHandler
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig

log.clear_handlers()

def is_critical_payment_error(log_entry):
    """Custom logic for critical payment errors."""
    return (
        log_entry.get("level") == "error" and
        log_entry.get("service") == "payment" and
        log_entry.get("amount", 0) > 1000
    )

def is_sensitive_data(log_entry):
    """Detect if log contains sensitive data."""
    message = log_entry.get("message", "").lower()
    sensitive_words = ["password", "token", "secret", "key", "ssn"]
    return any(word in message for word in sensitive_words)

# Critical payments → Slack + Email (AND logic)
critical_config = RoutingConfig(
    [
        RoutingRule(RoutingRuleType.LEVEL, value="ERROR"),
        RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"),
        RoutingRule(RoutingRuleType.FUNCTION, func=lambda log: log.get("amount", 0) > 1000)
    ],
    match_mode="all",
    name="critical_payments"
)
log.add_handler(SlackHandler(webhook_url="..."), critical_config)

# Sensitive data → Encrypted channel (Slack)
sensitive_config = RoutingConfig([
    RoutingRule(RoutingRuleType.FUNCTION, func=is_sensitive_data)
])
log.add_handler(
    SlackHandler(webhook_url="https://hooks.slack.com/secure"),
    sensitive_config
)

# All → File
log.add_handler(FileHandler(filepath="/var/log/app.log"))

# Examples
log.info("User login", user_id="user123")  # → File only
log.error("Payment failed", service="payment", amount=500)  # → File only
log.error("Large payment failed", service="payment", amount=5000)  # → Slack + Email + File
log.error("Invalid password provided")  # → Slack (secure) + File
```

### Example 5: Exclusion Patterns

```python
from loglight import log
from loglight.handlers import WebhookHandler, ConsoleHandler
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig

log.clear_handlers()

def is_not_internal_debug(log_entry):
    """Exclude internal debug logs from external systems."""
    return log_entry.get("internal") != True

# External webhook: Only non-internal logs
external_config = RoutingConfig([
    RoutingRule(RoutingRuleType.FUNCTION, func=is_not_internal_debug)
])
log.add_handler(
    WebhookHandler(url="https://external-monitoring.example.com/logs"),
    external_config
)

# Console: All logs
log.add_handler(ConsoleHandler())

log.info("Processing request")  # → Webhook + Console
log.debug("Internal state", internal=True)  # → Console only
```

## Testing Handlers

Example unit test with routing:

```python
import pytest
from unittest.mock import Mock
from loglight import log
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig

def test_error_routing():
    """Test that errors go to Slack handler."""
    logger = log
    logger.clear_handlers()
    
    mock_slack = Mock()
    error_config = RoutingConfig([
        RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
    ])
    logger.add_handler(mock_slack, error_config)
    
    logger.info("info")
    assert mock_slack.emit.call_count == 0
    
    logger.error("error")
    assert mock_slack.emit.call_count == 1

def test_service_routing():
    """Test service-based routing."""
    logger = log
    logger.clear_handlers()
    
    mock_payment = Mock()
    payment_config = RoutingConfig([
        RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
    ])
    logger.add_handler(mock_payment, payment_config)
    
    logger.info("payment processed", service="payment")
    assert mock_payment.emit.called
    
    logger.info("auth processed", service="auth")
    mock_payment.emit.assert_called_once()  # Still only called once
```

## API Reference

### RoutingRule

```python
class RoutingRule:
    def __init__(
        self,
        rule_type: RoutingRuleType,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        pattern: Optional[str] = None,
        func: Optional[Callable[[Dict], bool]] = None,
        name: Optional[str] = None,
    ):
        """Create a routing rule."""
        
    def matches(self, log_entry: Dict) -> bool:
        """Check if log entry matches this rule."""
```

### RoutingConfig

```python
class RoutingConfig:
    def __init__(
        self,
        rules: Optional[List[RoutingRule]] = None,
        match_mode: str = "any",
        name: Optional[str] = None,
    ):
        """Create a routing configuration."""
        
    def should_route(self, log_entry: Dict) -> bool:
        """Check if log should be routed."""
        
    def add_rule(self, rule: RoutingRule) -> "RoutingConfig":
        """Add a rule (supports method chaining)."""
```

### Logger Methods

```python
class Logger:
    def add_handler(
        self,
        handler,
        routing_config: RoutingConfig = None
    ) -> None:
        """Add a handler with optional routing."""
        
    def remove_handler(self, handler) -> bool:
        """Remove a handler."""
        
    def clear_handlers(self) -> None:
        """Clear all handlers."""
```

## Best Practices

1. **Be Specific with Rules**: Use `match_mode="all"` when you need precise routing
2. **Name Your Configs**: Use descriptive names for debugging: `name="critical_payments"`
3. **Test Your Rules**: Write unit tests for complex routing logic
4. **Handle Exceptions**: Handler errors are caught and logged to stderr
5. **Use Regex for Flexibility**: Regex patterns allow complex message-based routing
6. **Custom Functions for Complex Logic**: Use `FUNCTION` rules for business logic
7. **Monitor Handler Performance**: Log handler failures are non-blocking

## Troubleshooting

### Logs not reaching expected handler

1. Check routing config with `print(config)` to verify rules
2. Verify log entry has expected fields: `log.info("msg", field="value")`
3. Test rule matching directly: `rule.matches(log_entry)`

### All logs going to all handlers

- Make sure you added routing configs: `logger.add_handler(handler, config)`
- Handlers without routing receive all logs

### Handler errors not visible

- Handler exceptions are logged to stderr by default
- Check stderr output for handler error details

