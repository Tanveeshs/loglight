# Field Masking & Data Protection Guide

## Overview

LogLight includes a comprehensive field masking system that automatically protects sensitive data in log statements. This is a **flag-driven system** that prevents developers from accidentally logging passwords, API keys, credit cards, and other sensitive information.

## Why Field Masking?

When logging application data, developers often forget to mask sensitive information. Field masking:

- ✅ **Automatically protects** sensitive fields without code changes
- ✅ **Pattern-based** detection for common sensitive fields
- ✅ **Configurable** strategies for different masking needs
- ✅ **Nested object support** for complex data structures
- ✅ **Value-based masking** for detecting sensitive data regardless of field name
- ✅ **Runtime configuration** to enable/disable on-the-fly

---

## Quick Start

### Enable Masking (Default)

```python
from loglight import log

# Masking is ENABLED by default
log.info("User login", username="john", password="secret123")
# Output: {"message": "User login", "username": "john", "password": "***"}
```

### Disable Masking (if needed)

```python
from loglight.config import LoggerConfig
from loglight import log

config = LoggerConfig(enable_field_masking=False)
log.configure(config)

log.info("Debug info", password="secret123")
# Output: {"message": "Debug info", "password": "secret123"}
```

---

## Configuration

### Environment Variables

Control masking via environment variables:

```bash
# Enable/disable masking globally
export LOG_ENABLE_MASKING=true

# Set masking strategy
export LOG_MASKING_STRATEGY=FULL  # FULL, PARTIAL, HASH, NULLIFY, FIRST_LAST

# Enable value-based masking (email, CC patterns)
export LOG_ENABLE_VALUE_MASKING=false

# Enable nested object masking
export LOG_ENABLE_NESTED_MASKING=true

# Chars to keep in PARTIAL strategy
export LOG_PARTIAL_KEEP_CHARS=2
```

### Python Configuration

```python
from loglight.config import LoggerConfig
from loglight import log

config = LoggerConfig(
    # Master switch for all masking
    enable_field_masking=True,
    
    # Masking strategy
    masking_strategy='FULL',  # FULL, PARTIAL, HASH, NULLIFY, FIRST_LAST
    
    # Pattern matching options
    enable_pattern_matching=True,  # Use regex for field names
    enable_nested_masking=True,    # Mask nested objects
    enable_value_masking=False,    # Mask based on value patterns
    
    # PARTIAL strategy settings
    partial_keep_chars=2,
    
    # Custom patterns
    custom_masking_patterns={
        'internal_secret': r'(?i)^internal_secret_.*$',
        'custom_token': r'(?i)^custom_token$'
    },
    
    # Which built-in patterns to use (None = all)
    patterns_to_use=['password', 'api_key', 'token']
)

log.configure(config)
```

---

## Masking Strategies

### 1. FULL (Default)

Replace entire value with `***`

```python
log.info("Login", password="secret123")
# Output: {"password": "***"}
```

### 2. PARTIAL

Show first and last N characters

```python
config = LoggerConfig(
    masking_strategy='PARTIAL',
    partial_keep_chars=2
)

log.info("Login", password="secret123")
# Output: {"password": "se***23"}
```

### 3. NULLIFY

Replace with `null`

```python
config = LoggerConfig(masking_strategy='NULLIFY')

log.info("Login", password="secret123")
# Output: {"password": null}
```

### 4. HASH

Replace with hash representation

```python
config = LoggerConfig(masking_strategy='HASH')

log.info("Login", password="secret123")
# Output: {"password": "<hash:1234>"}
```

### 5. FIRST_LAST

Show only first and last character

```python
config = LoggerConfig(masking_strategy='FIRST_LAST')

log.info("Login", password="secret123")
# Output: {"password": "s*********3"}
```

---

## Built-in Patterns

LogLight comes with pre-configured patterns for common sensitive fields:

### Authentication & Credentials
- `password` - password, passwd, pwd
- `api_key` - api_key, apikey, api-key
- `secret` - secret, client_secret
- `token` - token, auth_token, access_token, refresh_token
- `bearer` - bearer, authorization
- `oauth` - oauth, oauth_token
- `private_key` - private_key, privatekey

### Personal Information
- `email` - email, email_address, e_mail
- `phone` - phone, phone_number, mobile, cell
- `ssn` - ssn, social_security_number

### Financial Information
- `credit_card` - credit_card, cc_number, card_number, creditcard
- `cvv` - cvv, cvc, card_code
- `routing` - routing_number, route_number
- `account` - account_number, account_id

### Other
- `pin` - pin, personal_id_number
- `passport` - passport, passport_number
- `driver_license` - driver_license, drivers_license, dl_number

---

## Usage Examples

### Basic Usage

```python
from loglight import log

# These fields are automatically masked
log.info("User created",
    username="john_doe",
    email="john@example.com",      # ✅ Masked
    password="super_secret",       # ✅ Masked
    api_key="sk_live_abc123",      # ✅ Masked
    role="admin"                   # Not masked
)

# Output:
# {
#   "message": "User created",
#   "username": "john_doe",
#   "email": "***",
#   "password": "***",
#   "api_key": "***",
#   "role": "admin"
# }
```

### Nested Objects

```python
from loglight import log

log.info("Profile update",
    user={
        "name": "John",
        "password": "secret123",    # ✅ Masked in nested object
        "credit_card": "1234-5678"  # ✅ Masked in nested object
    }
)

# Output:
# {
#   "message": "Profile update",
#   "user": {
#     "name": "John",
#     "password": "***",
#     "credit_card": "***"
#   }
# }
```

### Custom Patterns

```python
from loglight import log

# Add custom pattern at runtime
log.add_masking_pattern('internal_id', r'(?i)^internal_id_.*$')

log.info("Internal event",
    internal_id_user="id_secret123",    # ✅ Masked
    internal_id_org="org_secret456",    # ✅ Masked
    public_id="public_123"              # Not masked
)

# Output:
# {
#   "internal_id_user": "***",
#   "internal_id_org": "***",
#   "public_id": "public_123"
# }
```

### Value-Based Masking

Detect and mask sensitive data regardless of field name:

```python
from loglight.config import LoggerConfig
from loglight import log

config = LoggerConfig(
    enable_value_masking=True
)
log.configure(config)

log.info("Contact info",
    user_contact="john@example.com",    # ✅ Masked by email pattern
    alternate="jane@example.com"        # ✅ Masked by email pattern
)

# Output:
# {
#   "user_contact": "***",
#   "alternate": "***"
# }
```

### Partial Masking Strategy

```python
from loglight.config import LoggerConfig
from loglight import log

config = LoggerConfig(
    masking_strategy='PARTIAL',
    partial_keep_chars=3
)
log.configure(config)

log.info("Login attempt",
    email="john@example.com",
    credit_card="4111111111111111"
)

# Output:
# {
#   "email": "joh***@example.com",      # Shows first 3 and last 3
#   "credit_card": "411***1111"
# }
```

---

## Runtime Management

### Enable/Disable Masking

```python
from loglight import log

# Disable temporarily (for debugging)
log.disable_masking()
log.info("Debug", password="secret")  # password is NOT masked

# Re-enable
log.enable_masking()
log.info("Normal", password="secret")  # password IS masked
```

### Change Strategy at Runtime

```python
from loglight import log

log.set_masking_strategy('PARTIAL')
log.info("Data", password="secret123")  # Uses PARTIAL strategy

log.set_masking_strategy('NULLIFY')
log.info("Data", password="secret123")  # Uses NULLIFY strategy
```

### Add Custom Patterns at Runtime

```python
from loglight import log

# Add pattern for custom sensitive fields
log.add_masking_pattern('custom_secret', r'(?i)^custom_secret_.*$')
log.add_masking_pattern('api_token', r'(?i)^(api_token|apitoken)$')

log.info("Event",
    custom_secret_key="secret_value",  # ✅ Masked
    api_token="token_xyz"              # ✅ Masked
)
```

### Remove Patterns

```python
from loglight import log

# Remove a pattern if not needed
log.remove_masking_pattern('email')

log.info("Data", email="john@example.com")  # NOT masked
```

### View Active Patterns

```python
from loglight import log

patterns = log.get_active_masking_patterns()
print(patterns)
# Output: ['password', 'api_key', 'secret', 'token', 'email', ...]
```

---

## Advanced Usage

### Custom Field Masker

```python
from loglight.masking import FieldMasker, MaskingStrategy

masker = FieldMasker(
    strategy=MaskingStrategy.PARTIAL,
    custom_patterns={
        'internal_secret': r'(?i)^internal_.*$'
    }
)

data = {
    'username': 'john',
    'password': 'secret123',
    'internal_key': 'key_abc'
}

masked = masker.mask_fields(data)
print(masked)
# {'username': 'john', 'password': 'se****', 'internal_key': 'in****'}
```

### Value Pattern Masker

```python
from loglight.masking import ValuePatternMasker

masker = ValuePatternMasker(
    enable_value_masking=True,
    value_patterns={
        'custom_pattern': r'CUSTOM:\d+'
    }
)

data = {
    'any_field': 'john@example.com',  # Masked by email pattern
    'custom_field': 'CUSTOM:12345'    # Masked by custom pattern
}

masked = masker.mask_fields(data)
```

---

## Production Configuration Examples

### High Security (Bank, Healthcare)

```python
from loglight.config import LoggerConfig

config = LoggerConfig(
    enable_field_masking=True,
    masking_strategy='NULLIFY',  # No hints about values
    enable_pattern_matching=True,
    enable_nested_masking=True,
    enable_value_masking=True,   # Aggressive masking
    patterns_to_use=[
        'password', 'api_key', 'secret', 'token', 'ssn',
        'credit_card', 'cvv', 'routing', 'account', 'pin'
    ]
)
```

### Moderate Security (SaaS)

```python
config = LoggerConfig(
    enable_field_masking=True,
    masking_strategy='FULL',
    enable_pattern_matching=True,
    enable_nested_masking=True,
    enable_value_masking=False,  # Only mask known field names
    patterns_to_use=[
        'password', 'api_key', 'secret', 'token', 'credit_card'
    ]
)
```

### Development (with Debug Info)

```python
config = LoggerConfig(
    enable_field_masking=True,
    masking_strategy='PARTIAL',
    partial_keep_chars=3,  # Show more info for debugging
    enable_pattern_matching=True,
    enable_nested_masking=True,
    enable_value_masking=False
)
```

---

## Migration from Old Redaction

The old `redaction_rules` parameter is deprecated. Migration is automatic:

**Before:**
```python
config = LoggerConfig(
    redaction_rules=['password', 'api_key']
)
```

**After (Recommended):**
```python
config = LoggerConfig(
    enable_field_masking=True,
    masking_strategy='FULL',
    patterns_to_use=['password', 'api_key']
)
```

---

## Performance Considerations

1. **Pattern Matching**: Regex compilation is cached. No performance impact after first use.

2. **Nested Objects**: Slightly slower for deeply nested structures. Can be disabled:
   ```python
   config = LoggerConfig(enable_nested_masking=False)
   ```

3. **Value-Based Masking**: More CPU intensive. Only enable if needed:
   ```python
   config = LoggerConfig(enable_value_masking=True)
   ```

4. **Disable When Not Needed**: If running in a data-processing environment, disable:
   ```python
   config = LoggerConfig(enable_field_masking=False)
   ```

---

## Testing

```python
import json
from io import StringIO
from loglight import log
from loglight.config import LoggerConfig

def test_password_masked():
    output = StringIO()
    config = LoggerConfig(enable_field_masking=True)
    log.configure(config)
    log.handler.emit = lambda x: output.write(x)
    
    log.info("Test", password="secret123")
    
    result = json.loads(output.getvalue())
    assert result['password'] == '***'
```

---

## Troubleshooting

### Fields Not Being Masked

Check that:
1. `enable_field_masking=True` is set
2. `enable_pattern_matching=True` is set
3. Pattern exists in `get_active_masking_patterns()`
4. Field name matches the pattern (case-insensitive for built-in patterns)

```python
log.get_active_masking_patterns()  # Check if your field pattern is there
```

### Custom Pattern Not Working

Make sure the regex is valid:

```python
import re

# Test your regex
pattern = r'(?i)^my_secret_.*$'
assert re.match(pattern, 'my_secret_key')  # Should pass

log.add_masking_pattern('my_secret', pattern)
```

### Performance Issues

If you're seeing performance degradation:

```python
# Disable value masking (most expensive)
log.field_masker.enable_value_masking = False

# Disable nested masking (slightly expensive)
log.field_masker.enable_nested_masking = False
```

---

## Best Practices

1. ✅ **Always enable** masking in production
2. ✅ **Use NULLIFY or FULL** strategies in production
3. ✅ **Test** your patterns before deployment
4. ✅ **Review logs** for sensitive data before release
5. ✅ **Use value masking** for extra protection in high-security environments
6. ✅ **Document** any custom patterns your team adds

---

## See Also

- [Configuration Guide](./CONFIGURATION.md)
- [Examples](./EXAMPLES.md)
- [Contributing](./CONTRIBUTING.md)

