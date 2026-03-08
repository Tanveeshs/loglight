# examples/masking_demo.py
"""
Demonstration of LogLight's automatic field masking capabilities.

This example shows how sensitive data is automatically protected
without any additional configuration needed.
"""

import json
from loglight import log
from loglight.config import LoggerConfig
from loglight.handlers import ConsoleHandler
from io import StringIO


def print_section(title):
    """Helper to print section titles."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def demo_default_masking():
    """Demo 1: Default masking is enabled automatically."""
    print_section("Demo 1: Default Masking (Enabled by Default)")

    from loglight.logger import Logger
    config = LoggerConfig()
    logger = Logger(config=config)
    output = StringIO()
    logger.handler.emit = lambda x: output.write(x)

    print("\nLogging with sensitive fields:")
    print('log.info("User login", username="john", password="secret123")')

    logger.info("User login", username="john", password="secret123")

    log_output = output.getvalue().strip()
    if log_output:
        result = json.loads(log_output)
        print("\nOutput:")
        print(json.dumps(result, indent=2))
        print("\n✅ Notice: password field is automatically masked!")
    else:
        print("\n❌ ERROR: No output from logger")


def demo_multiple_sensitive_fields():
    """Demo 2: Multiple sensitive fields are masked."""
    print_section("Demo 2: Multiple Sensitive Fields")

    from loglight.logger import Logger
    config = LoggerConfig(enable_field_masking=True)
    logger = Logger(config=config)
    output = StringIO()
    logger.handler.emit = lambda x: output.write(x)

    print("\nLogging multiple sensitive fields:")
    print("""log.info("API Request",
    username="john",
    api_key="sk_live_abc123def456",
    password="super_secret",
    credit_card="4111-1111-1111-1111",
    email="john@example.com"
)""")

    logger.info("API Request",
        username="john",
        api_key="sk_live_abc123def456",
        password="super_secret",
        credit_card="4111-1111-1111-1111",
        email="john@example.com"
    )

    log_output = output.getvalue().strip()
    if log_output:
        result = json.loads(log_output)
        print("\nOutput:")
        print(json.dumps(result, indent=2))
        print("\n✅ All sensitive fields automatically masked!")
    else:
        print("\n❌ ERROR: No output from logger")


def demo_partial_strategy():
    """Demo 3: Partial masking shows first/last characters."""
    print_section("Demo 3: Partial Masking Strategy")

    from loglight.logger import Logger
    config = LoggerConfig(
        enable_field_masking=True,
        masking_strategy='PARTIAL',
        partial_keep_chars=3
    )
    logger = Logger(config=config)
    output = StringIO()
    logger.handler.emit = lambda x: output.write(x + '\n')

    print("\nUsing PARTIAL strategy (shows first 3 and last 3 chars):")
    print('log.info("Auth", email="john@example.com", token="token_xyz789123")')

    logger.info("Auth", email="john@example.com", token="token_xyz789123")

    result = json.loads(output.getvalue())
    print("\nOutput:")
    print(json.dumps(result, indent=2))
    print("\n✅ Partial masking shows some context while protecting sensitive data")


def demo_nested_masking():
    """Demo 4: Masking works with nested objects."""
    print_section("Demo 4: Nested Object Masking")

    from loglight.logger import Logger
    config = LoggerConfig(enable_field_masking=True, enable_nested_masking=True)
    logger = Logger(config=config)
    output = StringIO()
    logger.handler.emit = lambda x: output.write(x + '\n')

    print("\nLogging nested objects with sensitive fields:")
    print("""log.info("Update User",
    user={
        "name": "John Doe",
        "email": "john@example.com",
        "password": "secret123"
    }
)""")

    logger.info("Update User",
        user={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secret123"
        }
    )

    result = json.loads(output.getvalue())
    print("\nOutput:")
    print(json.dumps(result, indent=2))
    print("\n✅ Sensitive fields masked even in nested objects!")


def demo_custom_patterns():
    """Demo 5: Add custom masking patterns."""
    print_section("Demo 5: Custom Masking Patterns")

    from loglight.logger import Logger
    config = LoggerConfig(enable_field_masking=True)
    logger = Logger(config=config)
    output = StringIO()
    logger.handler.emit = lambda x: output.write(x + '\n')

    print("\nAdding custom pattern for 'internal_secret':")
    print('log.add_masking_pattern("internal", r"(?i)^internal_.*$")')
    logger.add_masking_pattern("internal", r"(?i)^internal_.*$")

    print("\nLogging with custom sensitive fields:")
    print("""log.info("Event",
    internal_id="secret_id_12345",
    internal_token="secret_token_xyz",
    public_id="public_123"
)""")

    logger.info("Event",
        internal_id="secret_id_12345",
        internal_token="secret_token_xyz",
        public_id="public_123"
    )

    result = json.loads(output.getvalue())
    print("\nOutput:")
    print(json.dumps(result, indent=2))
    print("\n✅ Custom patterns work perfectly!")


def demo_disable_masking():
    """Demo 6: Masking can be disabled when needed."""
    print_section("Demo 6: Disable Masking (for Debugging)")

    from loglight.logger import Logger
    config = LoggerConfig(enable_field_masking=True)
    logger = Logger(config=config)
    output = StringIO()
    logger.handler.emit = lambda x: output.write(x + '\n')

    print("\nDisabling masking for debugging:")
    print("log.disable_masking()")
    logger.disable_masking()

    print('log.info("Debug", password="secret123")')
    logger.info("Debug", password="secret123")

    result = json.loads(output.getvalue())
    print("\nOutput:")
    print(json.dumps(result, indent=2))
    print("\n⚠️  Password is NOT masked (masking disabled)")

    print("\nRe-enabling masking:")
    print("log.enable_masking()")
    logger.enable_masking()

    output.truncate(0)
    output.seek(0)

    print('log.info("Normal", password="secret123")')
    logger.info("Normal", password="secret123")

    result = json.loads(output.getvalue())
    print("\nOutput:")
    print(json.dumps(result, indent=2))
    print("\n✅ Password is masked again!")


def demo_get_patterns():
    """Demo 7: View active masking patterns."""
    print_section("Demo 7: View Active Masking Patterns")

    from loglight.logger import Logger
    config = LoggerConfig(enable_field_masking=True)
    logger = Logger(config=config)

    patterns = logger.get_active_masking_patterns()
    print(f"\nActive masking patterns ({len(patterns)} total):")

    # Group patterns by category
    categories = {
        'Authentication': ['password', 'api_key', 'secret', 'token', 'bearer', 'oauth', 'private_key'],
        'Personal': ['email', 'phone', 'ssn'],
        'Financial': ['credit_card', 'cvv', 'routing', 'account'],
        'Other': ['pin', 'passport', 'driver_license']
    }

    for category, names in categories.items():
        active = [name for name in names if name in patterns]
        if active:
            print(f"\n{category}:")
            for name in active:
                print(f"  ✓ {name}")


def demo_all_strategies():
    """Demo 8: Show all masking strategies."""
    print_section("Demo 8: All Masking Strategies")

    from loglight.logger import Logger
    strategies = ['FULL', 'PARTIAL', 'HASH', 'NULLIFY', 'FIRST_LAST']
    secret_value = "super_secret_password_12345"

    print(f"\nMasking '{secret_value}' with different strategies:\n")

    for strategy in strategies:
        config = LoggerConfig(
            enable_field_masking=True,
            masking_strategy=strategy,
            partial_keep_chars=2
        )
        logger = Logger(config=config)
        output = StringIO()
        logger.handler.emit = lambda x: output.write(x)

        logger.info("Test", password=secret_value)
        result = json.loads(output.getvalue())
        masked_value = result['password']

        print(f"{strategy:12} → {masked_value}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  LogLight Field Masking Demonstration")
    print("="*60)
    print("\nAutomatic protection of sensitive data in logs!")

    # Run all demos
    demo_default_masking()
    demo_multiple_sensitive_fields()
    demo_partial_strategy()
    demo_nested_masking()
    demo_custom_patterns()
    demo_disable_masking()
    demo_get_patterns()
    demo_all_strategies()

    print("\n" + "="*60)
    print("  ✅ All demonstrations complete!")
    print("="*60)
    print("\nFor more information, see: docs/MASKING.md")
    print("\n")

