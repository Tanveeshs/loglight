# tests/test_masking.py
"""Tests for field masking functionality."""

import pytest
from loglight.masking import FieldMasker, ValuePatternMasker, MaskingStrategy
from loglight.config import LoggerConfig
from loglight.logger import Logger
from io import StringIO
import json


class TestFieldMasker:
    """Test FieldMasker basic functionality."""

    def test_masker_initialization(self):
        """Test masker can be initialized."""
        masker = FieldMasker()
        assert masker.enable_masking is True
        assert masker.strategy == MaskingStrategy.FULL

    def test_should_mask_password(self):
        """Test password field detection."""
        masker = FieldMasker()
        assert masker.should_mask("password") is True
        assert masker.should_mask("Password") is True
        assert masker.should_mask("PASSWORD") is True
        assert masker.should_mask("username") is False

    def test_should_mask_api_key(self):
        """Test API key field detection."""
        masker = FieldMasker()
        assert masker.should_mask("api_key") is True
        assert masker.should_mask("apikey") is True
        assert masker.should_mask("api-key") is True

    def test_should_mask_credit_card(self):
        """Test credit card field detection."""
        masker = FieldMasker()
        assert masker.should_mask("credit_card") is True
        assert masker.should_mask("card_number") is True
        assert masker.should_mask("cc_number") is True

    def test_should_mask_email(self):
        """Test email field detection."""
        masker = FieldMasker()
        assert masker.should_mask("email") is True
        assert masker.should_mask("email_address") is True

    def test_mask_value_full_strategy(self):
        """Test FULL masking strategy."""
        masker = FieldMasker(strategy=MaskingStrategy.FULL)
        assert masker.mask_value("secret123") == "***"
        assert masker.mask_value("password") == "***"

    def test_mask_value_nullify_strategy(self):
        """Test NULLIFY masking strategy."""
        masker = FieldMasker(strategy=MaskingStrategy.NULLIFY)
        assert masker.mask_value("secret123") is None

    def test_mask_value_partial_strategy(self):
        """Test PARTIAL masking strategy."""
        masker = FieldMasker(strategy=MaskingStrategy.PARTIAL, partial_keep_chars=2)
        result = masker.mask_value("password123")
        assert result.startswith("pa")
        assert result.endswith("23")
        assert "***" in result

    def test_mask_value_first_last_strategy(self):
        """Test FIRST_LAST masking strategy."""
        masker = FieldMasker(strategy=MaskingStrategy.FIRST_LAST)
        result = masker.mask_value("password123")
        assert result[0] == "p"
        assert result[-1] == "3"
        assert result.count("*") == len("password123") - 2

    def test_mask_value_hash_strategy(self):
        """Test HASH masking strategy."""
        masker = FieldMasker(strategy=MaskingStrategy.HASH)
        result = masker.mask_value("secret123")
        assert "<hash:" in result
        assert ">" in result

    def test_mask_fields_simple(self):
        """Test masking dictionary with simple fields."""
        masker = FieldMasker()
        data = {"username": "john", "password": "secret123"}
        masked = masker.mask_fields(data)

        assert masked["username"] == "john"
        assert masked["password"] == "***"

    def test_mask_fields_multiple(self):
        """Test masking multiple sensitive fields."""
        masker = FieldMasker()
        data = {
            "username": "john",
            "password": "secret123",
            "api_key": "key_abc123",
            "token": "token_xyz789",
        }
        masked = masker.mask_fields(data)

        assert masked["username"] == "john"
        assert masked["password"] == "***"
        assert masked["api_key"] == "***"
        assert masked["token"] == "***"

    def test_mask_fields_nested(self):
        """Test masking in nested dictionaries."""
        masker = FieldMasker(enable_nested_masking=True)
        data = {"user": {"name": "john", "password": "secret123"}}
        masked = masker.mask_fields(data)

        assert masked["user"]["name"] == "john"
        assert masked["user"]["password"] == "***"

    def test_mask_fields_list_of_dicts(self):
        """Test masking in lists of dictionaries."""
        masker = FieldMasker(enable_nested_masking=True)
        data = {
            "users": [
                {"name": "john", "password": "secret1"},
                {"name": "jane", "password": "secret2"},
            ]
        }
        masked = masker.mask_fields(data)

        assert masked["users"][0]["password"] == "***"
        assert masked["users"][1]["password"] == "***"

    def test_masking_disabled(self):
        """Test that masking can be disabled."""
        masker = FieldMasker(enable_masking=False)
        data = {"password": "secret123"}
        masked = masker.mask_fields(data)

        assert masked["password"] == "secret123"

    def test_custom_pattern(self):
        """Test custom masking patterns."""
        masker = FieldMasker(custom_patterns={"custom_secret": r"(?i)^secret_.*$"})
        data = {"secret_key": "value123", "other": "value456"}
        masked = masker.mask_fields(data)

        assert masked["secret_key"] == "***"
        assert masked["other"] == "value456"

    def test_add_pattern_at_runtime(self):
        """Test adding patterns at runtime."""
        masker = FieldMasker()
        assert masker.should_mask("custom_field") is False

        masker.add_custom_pattern("custom", r"(?i)^custom_.*$")
        assert masker.should_mask("custom_field") is True

    def test_remove_pattern(self):
        """Test removing patterns."""
        masker = FieldMasker()
        assert masker.should_mask("password") is True

        masker.remove_pattern("password")
        assert masker.should_mask("password") is False

    def test_get_active_patterns(self):
        """Test getting active pattern list."""
        masker = FieldMasker(patterns_to_use=["password", "api_key"])
        patterns = masker.get_active_patterns()

        assert "password" in patterns
        assert "api_key" in patterns
        assert "email" not in patterns


class TestValuePatternMasker:
    """Test ValuePatternMasker for value-based masking."""

    def test_enable_value_masking(self):
        """Test value pattern masking can be enabled."""
        masker = ValuePatternMasker(enable_value_masking=True)
        assert masker.enable_value_masking is True

    def test_mask_email_value(self):
        """Test masking based on email pattern."""
        masker = ValuePatternMasker(enable_value_masking=True)
        assert masker.should_mask_value("user@example.com") is True
        assert masker.should_mask_value("notanemail") is False

    def test_mask_credit_card_value(self):
        """Test masking based on credit card pattern."""
        masker = ValuePatternMasker(enable_value_masking=True)
        assert masker.should_mask_value("1234-5678-9012-3456") is True
        assert masker.should_mask_value("1234567890123456") is True

    def test_mask_fields_by_value(self):
        """Test masking fields by their values."""
        masker = ValuePatternMasker(enable_value_masking=True)
        data = {"contact": "user@example.com", "card": "1234-5678-9012-3456"}
        masked = masker.mask_fields(data)

        assert masked["contact"] == "***"
        assert masked["card"] == "***"


class TestLoggerMasking:
    """Test masking integration with Logger."""

    def test_logger_masks_password(self):
        """Test logger masks password fields."""
        output = StringIO()
        config = LoggerConfig(enable_field_masking=True)
        logger = Logger(config=config, handler=None)

        logger.handlers[0].emit = lambda x: output.write(x + "\n")

        logger.info("User login", password="secret123")

        log_line = output.getvalue()
        log_data = json.loads(log_line)

        assert log_data["password"] == "***"

    def test_logger_masks_api_key(self):
        """Test logger masks API keys."""
        output = StringIO()
        config = LoggerConfig(enable_field_masking=True)
        logger = Logger(config=config, handler=None)
        logger.handlers[0].emit = lambda x: output.write(x + "\n")

        logger.info("API call", api_key="key_abc123")

        log_line = output.getvalue()
        log_data = json.loads(log_line)

        assert log_data["api_key"] == "***"

    def test_logger_masking_disabled(self):
        """Test logger can disable masking."""
        output = StringIO()
        config = LoggerConfig(enable_field_masking=False)
        logger = Logger(config=config, handler=None)
        logger.handlers[0].emit = lambda x: output.write(x + "\n")

        logger.info("User login", password="secret123")

        log_line = output.getvalue()
        log_data = json.loads(log_line)

        assert log_data["password"] == "secret123"

    def test_logger_partial_masking(self):
        """Test logger with partial masking strategy."""
        output = StringIO()
        config = LoggerConfig(enable_field_masking=True, masking_strategy="PARTIAL")
        logger = Logger(config=config, handler=None)
        logger.handlers[0].emit = lambda x: output.write(x + "\n")

        logger.info("Login", password="secret123")

        log_line = output.getvalue()
        log_data = json.loads(log_line)

        assert log_data["password"].startswith("se")
        assert log_data["password"].endswith("23")

    def test_logger_add_pattern(self):
        """Test adding pattern to logger at runtime."""
        output = StringIO()
        config = LoggerConfig(enable_field_masking=True)
        logger = Logger(config=config, handler=None)
        logger.handlers[0].emit = lambda x: output.write(x + "\n")

        # Add custom pattern for 'internal_id'
        logger.add_masking_pattern("internal_id", r"(?i)^internal_id$")

        logger.info("Data", internal_id="id_secret123")

        log_line = output.getvalue()
        log_data = json.loads(log_line)

        assert log_data["internal_id"] == "***"

    def test_logger_remove_pattern(self):
        """Test removing pattern from logger."""
        output = StringIO()
        config = LoggerConfig(enable_field_masking=True)
        logger = Logger(config=config, handler=None)
        logger.handlers[0].emit = lambda x: output.write(x + "\n")

        # Remove password pattern
        logger.remove_masking_pattern("password")

        logger.info("Login", password="secret123")

        log_line = output.getvalue()
        log_data = json.loads(log_line)

        assert log_data["password"] == "secret123"

    def test_logger_enable_disable_masking(self):
        """Test enabling/disabling masking at runtime."""
        output = StringIO()
        config = LoggerConfig(enable_field_masking=True)
        logger = Logger(config=config, handler=None)
        logger.handlers[0].emit = lambda x: output.write(x + "\n")

        # Test enabled
        logger.info("Test1", password="secret1")
        log1 = json.loads(output.getvalue().split("\n")[0])
        assert log1["password"] == "***"

        # Disable
        output.truncate(0)
        output.seek(0)
        logger.disable_masking()
        logger.info("Test2", password="secret2")
        log2 = json.loads(output.getvalue())
        assert log2["password"] == "secret2"

        # Re-enable
        output.truncate(0)
        output.seek(0)
        logger.enable_masking()
        logger.info("Test3", password="secret3")
        log3 = json.loads(output.getvalue())
        assert log3["password"] == "***"

    def test_logger_set_strategy(self):
        """Test changing masking strategy at runtime."""
        output = StringIO()
        config = LoggerConfig(enable_field_masking=True, masking_strategy="FULL")
        logger = Logger(config=config, handler=None)
        logger.handlers[0].emit = lambda x: output.write(x + "\n")

        logger.set_masking_strategy("NULLIFY")
        logger.info("Test", password="secret")

        log_line = output.getvalue()
        log_data = json.loads(log_line)

        assert log_data["password"] is None

    def test_logger_get_active_patterns(self):
        """Test getting active patterns from logger."""
        config = LoggerConfig(enable_field_masking=True)
        logger = Logger(config=config, handler=None)

        patterns = logger.get_active_masking_patterns()
        assert "password" in patterns
        assert "api_key" in patterns
