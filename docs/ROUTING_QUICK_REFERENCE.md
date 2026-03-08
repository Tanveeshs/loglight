# Quick Reference: Log Routing

## Your Original Question

**Can I send different kinds of logs to Slack, different kinds to Webhook, and different kinds to Console?**

**Answer: YES! ✅**

---

## Quick Examples

### Example 1: Errors to Slack, All to Console
```python
from loglight import log
from loglight.handlers import SlackHandler
from loglight.routing import RoutingRule, RoutingRuleType, RoutingConfig

log.clear_handlers()

# Slack: Errors only
slack_config = RoutingConfig([
    RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
])
log.add_handler(SlackHandler(webhook_url="..."), slack_config)

# Console: Everything
log.add_handler(ConsoleHandler())

log.info("info")      # → Console only
log.error("error")    # → Slack + Console
```

---

### Example 2: By Service
```python
log.clear_handlers()

# Payment service → Slack
payment_config = RoutingConfig([
    RoutingRule(RoutingRuleType.EXACT, key="service", value="payment")
])
log.add_handler(SlackHandler(...), payment_config)

# Auth service → Webhook
auth_config = RoutingConfig([
    RoutingRule(RoutingRuleType.EXACT, key="service", value="auth")
])
log.add_handler(WebhookHandler(...), auth_config)

# All → Console
log.add_handler(ConsoleHandler())

log.info("payment msg", service="payment")  # → Slack + Console
log.info("auth msg", service="auth")        # → Webhook + Console
```

---

### Example 3: By Message Pattern
```python
log.clear_handlers()

# Database errors → Special handler
db_config = RoutingConfig([
    RoutingRule(
        RoutingRuleType.REGEX,
        key="message",
        pattern=r"(?i)database|sql"
    )
])
log.add_handler(db_handler, db_config)

# API errors → Different handler
api_config = RoutingConfig([
    RoutingRule(
        RoutingRuleType.REGEX,
        key="message",
        pattern=r"(?i)api|http"
    )
])
log.add_handler(api_handler, api_config)

log.error("Database error")  # → db_handler
log.error("API error")        # → api_handler
```

---

### Example 4: Complex Logic (AND)
```python
log.clear_handlers()

# Only route ERROR logs from payment service
critical_config = RoutingConfig(
    [
        RoutingRule(RoutingRuleType.LEVEL, value="ERROR"),
        RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"),
    ],
    match_mode="all"  # AND logic: both rules must match
)
log.add_handler(slack_handler, critical_config)

log.error("payment error", service="payment")  # ✅ Routes to handler
log.error("auth error", service="auth")        # ❌ Doesn't route
log.info("payment info", service="payment")    # ❌ Doesn't route
```

---

### Example 5: Custom Function
```python
def is_high_priority(log_entry):
    return log_entry.get("priority") == "high"

config = RoutingConfig([
    RoutingRule(RoutingRuleType.FUNCTION, func=is_high_priority)
])
log.add_handler(handler, config)

log.info("normal", priority="low")    # ❌ Doesn't route
log.info("urgent", priority="high")   # ✅ Routes to handler
```

---

## Routing Rule Types

| Type | Usage | Example |
|------|-------|---------|
| **EXACT** | Exact field match | `key="service", value="payment"` |
| **CONTAINS** | Substring in field | `key="message", value="error"` |
| **REGEX** | Pattern matching | `pattern=r"db\|sql"` |
| **LEVEL** | Log level threshold | `value="ERROR"` routes ERROR and CRITICAL |
| **FUNCTION** | Custom logic | `func=lambda log: log.get("id") == "123"` |

---

## Match Modes

```python
# ANY mode (default) - OR logic
match_mode="any"  # Route if ANY rule matches

# ALL mode - AND logic  
match_mode="all"  # Route if ALL rules match
```

---

## API Methods

```python
# Add a handler with routing
log.add_handler(handler, routing_config)

# Remove a handler
log.remove_handler(handler)

# Clear all handlers
log.clear_handlers()
```

---

## Test Coverage

✅ 49 comprehensive tests pass
- 24 tests: Routing rules
- 18 tests: Handler integration
- 7 tests: Real-world scenarios

Run tests:
```bash
pytest tests/test_routing*.py -v
```

---

## Files to Reference

1. **docs/ROUTING.md** - Full documentation with 10+ examples
2. **examples/routing_demo.py** - 8 working code examples
3. **tests/test_routing_scenarios.py** - Real-world test cases
4. **ROUTING_IMPLEMENTATION.md** - Implementation summary

---

## Key Points

✅ **Multiple handlers**: Add as many handlers as needed  
✅ **Flexible routing**: Use any combination of rules  
✅ **Simple API**: `add_handler(handler, config)`  
✅ **Error safe**: Exceptions in handlers don't crash logger  
✅ **Backward compatible**: Old code still works  
✅ **Well tested**: 49 tests verify all scenarios  

---

## Common Patterns

### Pattern 1: Log Levels
```python
RoutingConfig([RoutingRule(RoutingRuleType.LEVEL, value="ERROR")])
```
Routes: ERROR, CRITICAL

### Pattern 2: Multiple Services (OR)
```python
RoutingConfig(
    [
        RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"),
        RoutingRule(RoutingRuleType.EXACT, key="service", value="auth"),
    ],
    match_mode="any"
)
```
Routes: payment OR auth service

### Pattern 3: Service + Level (AND)
```python
RoutingConfig(
    [
        RoutingRule(RoutingRuleType.LEVEL, value="ERROR"),
        RoutingRule(RoutingRuleType.EXACT, key="service", value="payment"),
    ],
    match_mode="all"
)
```
Routes: ERROR level AND payment service

### Pattern 4: Exclude Sensitive
```python
def is_safe(log_entry):
    msg = log_entry.get("message", "").lower()
    return not any(word in msg for word in ["password", "token"])

RoutingConfig([RoutingRule(RoutingRuleType.FUNCTION, func=is_safe)])
```
Routes: Logs without sensitive words

---

## Summary

**Your logging system now has flexible, production-ready routing!**

Different log types can be sent to:
- 🔴 **Slack** (e.g., errors from payment service)
- 🔗 **Webhook** (e.g., all auth service logs)
- 💻 **Console** (e.g., everything)
- 📁 **File** (e.g., specific patterns)
- Any other handler you create

All based on **configurable rules** without code changes!

