# loglight/masking.py
"""
Field masking and redaction module for LogLight.

Provides comprehensive data protection by automatically masking sensitive fields
in log statements. Supports built-in patterns, custom patterns, and configuration.
"""

import re
from typing import Any, Dict, List, Optional, Pattern, Union
from enum import Enum


class MaskingStrategy(Enum):
    """Different strategies for masking sensitive data."""
    FULL = "***"  # Replace with asterisks
    PARTIAL = "PARTIAL"  # Show first/last few chars
    HASH = "HASH"  # Replace with hash representation
    NULLIFY = "null"  # Replace with null
    FIRST_LAST = "FIRST_LAST"  # Show first and last char: a***z


class FieldMasker:
    """
    Comprehensive field masking engine for protecting sensitive data in logs.

    Features:
    - Built-in patterns for common sensitive fields
    - Custom regex patterns for advanced matching
    - Multiple masking strategies
    - Nested object support
    - Configuration flags for control
    """

    # Built-in patterns for common sensitive fields
    BUILT_IN_PATTERNS = {
        # Authentication & Credentials
        'password': r'(?i)^(password|passwd|pwd)$',
        'api_key': r'(?i)^(api_key|apikey|api-key)$',
        'secret': r'(?i)^(secret|client_secret)$',
        'token': r'(?i)^(token|auth_token|access_token|refresh_token)$',
        'bearer': r'(?i)^(bearer|authorization)$',

        # Personal Information
        'ssn': r'(?i)^(ssn|social_security_number)$',
        'email': r'(?i)^(email|email_address|e_mail)$',
        'phone': r'(?i)^(phone|phone_number|mobile|cell)$',

        # Financial Information
        'credit_card': r'(?i)^(credit_card|cc_number|card_number|creditcard)$',
        'cvv': r'(?i)^(cvv|cvc|card_code)$',
        'routing': r'(?i)^(routing_number|route_number)$',
        'account': r'(?i)^(account_number|account_id)$',

        # Other Sensitive Data
        'pin': r'(?i)^(pin|personal_id_number)$',
        'passport': r'(?i)^(passport|passport_number)$',
        'driver_license': r'(?i)^(driver_license|drivers_license|dl_number)$',
        'oauth': r'(?i)^(oauth|oauth_token)$',
        'private_key': r'(?i)^(private_key|privatekey)$',
    }

    def __init__(self,
                 enable_masking: bool = True,
                 strategy: Union[MaskingStrategy, str] = MaskingStrategy.FULL,
                 custom_patterns: Optional[Dict[str, str]] = None,
                 patterns_to_use: Optional[List[str]] = None,
                 enable_pattern_matching: bool = True,
                 enable_nested_masking: bool = True,
                 partial_keep_chars: int = 2,
                 ):
        """
        Initialize the field masker.

        Args:
            enable_masking: Whether to enable field masking globally
            strategy: Masking strategy to use (FULL, PARTIAL, HASH, NULLIFY, FIRST_LAST)
            custom_patterns: Custom regex patterns {name: regex_pattern}
            patterns_to_use: Which built-in patterns to enable (None = all)
            enable_pattern_matching: Whether to use regex pattern matching
            enable_nested_masking: Whether to mask fields in nested objects
            partial_keep_chars: How many chars to keep when using PARTIAL strategy
        """
        self.enable_masking = enable_masking
        self.strategy = self._parse_strategy(strategy)
        self.enable_pattern_matching = enable_pattern_matching
        self.enable_nested_masking = enable_nested_masking
        self.partial_keep_chars = partial_keep_chars

        # Compile patterns
        self.compiled_patterns: Dict[str, Pattern] = {}

        # Add built-in patterns
        patterns_to_use = patterns_to_use or list(self.BUILT_IN_PATTERNS.keys())
        for pattern_name in patterns_to_use:
            if pattern_name in self.BUILT_IN_PATTERNS:
                pattern = self.BUILT_IN_PATTERNS[pattern_name]
                self.compiled_patterns[pattern_name] = re.compile(pattern)

        # Add custom patterns
        if custom_patterns:
            for name, pattern in custom_patterns.items():
                self.compiled_patterns[name] = re.compile(pattern)

    @staticmethod
    def _parse_strategy(strategy: Union[MaskingStrategy, str]) -> MaskingStrategy:
        """Parse strategy from string or enum."""
        if isinstance(strategy, MaskingStrategy):
            return strategy
        return MaskingStrategy[strategy.upper()]

    def should_mask(self, field_name: str) -> bool:
        """
        Determine if a field should be masked.

        Args:
            field_name: The name of the field

        Returns:
            True if field should be masked, False otherwise
        """
        if not self.enable_masking:
            return False

        if not self.enable_pattern_matching:
            return False

        field_name_lower = field_name.lower()

        # Check if any pattern matches
        for pattern in self.compiled_patterns.values():
            if pattern.match(field_name_lower):
                return True

        return False

    def mask_value(self, value: Any) -> Any:
        """
        Mask a value according to the configured strategy.

        Args:
            value: The value to mask

        Returns:
            The masked value
        """
        if not self.enable_masking:
            return value

        if value is None:
            return None

        value_str = str(value)

        if self.strategy == MaskingStrategy.FULL:
            return "***"
        elif self.strategy == MaskingStrategy.NULLIFY:
            return None
        elif self.strategy == MaskingStrategy.HASH:
            return f"<hash:{hash(value_str) % 10000}>"
        elif self.strategy == MaskingStrategy.PARTIAL:
            return self._partial_mask(value_str)
        elif self.strategy == MaskingStrategy.FIRST_LAST:
            return self._first_last_mask(value_str)

        return "***"  # Default fallback

    def _partial_mask(self, value: str) -> str:
        """Show first and last few characters."""
        if len(value) <= self.partial_keep_chars * 2:
            return "*" * len(value)

        keep = self.partial_keep_chars
        return value[:keep] + "*" * (len(value) - keep * 2) + value[-keep:]

    def _first_last_mask(self, value: str) -> str:
        """Show only first and last character."""
        if len(value) <= 2:
            return "*" * len(value)
        return value[0] + "*" * (len(value) - 2) + value[-1]

    def mask_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive fields in a dictionary.

        Args:
            data: Dictionary potentially containing sensitive fields

        Returns:
            Dictionary with sensitive fields masked
        """
        if not self.enable_masking:
            return data

        masked_data = {}

        for key, value in data.items():
            if self.should_mask(key):
                masked_data[key] = self.mask_value(value)
            elif self.enable_nested_masking and isinstance(value, dict):
                masked_data[key] = self.mask_fields(value)
            elif self.enable_nested_masking and isinstance(value, list):
                masked_data[key] = [
                    self.mask_fields(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                masked_data[key] = value

        return masked_data

    def add_custom_pattern(self, name: str, pattern: Union[str, Pattern]) -> None:
        """
        Add a custom pattern at runtime.

        Args:
            name: Name of the pattern
            pattern: Regex pattern string or compiled pattern
        """
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        self.compiled_patterns[name] = pattern

    def remove_pattern(self, name: str) -> None:
        """Remove a pattern."""
        self.compiled_patterns.pop(name, None)

    def get_active_patterns(self) -> List[str]:
        """Get list of active patterns."""
        return list(self.compiled_patterns.keys())


class ValuePatternMasker(FieldMasker):
    """
    Extended masker that can mask based on value patterns, not just field names.

    For example, mask anything that looks like a credit card number or email,
    regardless of field name.
    """

    # Value patterns for common sensitive data
    VALUE_PATTERNS = {
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'api_key': r'(?i)(api_key|apikey)["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{32,}',
        'ipv4': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
    }

    def __init__(self, *args, enable_value_masking: bool = False,
                 value_patterns: Optional[Dict[str, str]] = None, **kwargs):
        """
        Initialize with value pattern masking.

        Args:
            enable_value_masking: Whether to mask values based on patterns
            value_patterns: Custom value patterns to check
        """
        super().__init__(*args, **kwargs)
        self.enable_value_masking = enable_value_masking

        # Compile value patterns
        self.compiled_value_patterns: Dict[str, Pattern] = {}
        for name, pattern in self.VALUE_PATTERNS.items():
            self.compiled_value_patterns[name] = re.compile(pattern)

        # Add custom value patterns
        if value_patterns:
            for name, pattern in value_patterns.items():
                self.compiled_value_patterns[name] = re.compile(pattern)

    def should_mask_value(self, value: Any) -> bool:
        """
        Check if a value should be masked based on value patterns.

        Args:
            value: The value to check

        Returns:
            True if value matches any pattern
        """
        if not self.enable_value_masking or not self.enable_masking:
            return False

        if value is None:
            return False

        value_str = str(value)

        # Check if any value pattern matches
        for pattern in self.compiled_value_patterns.values():
            if pattern.search(value_str):
                return True

        return False

    def mask_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask sensitive fields and values in a dictionary.

        Args:
            data: Dictionary potentially containing sensitive fields

        Returns:
            Dictionary with sensitive fields and values masked
        """
        if not self.enable_masking:
            return data

        masked_data = {}

        for key, value in data.items():
            should_mask_by_name = self.should_mask(key)
            should_mask_by_value = self.should_mask_value(value)

            if should_mask_by_name or should_mask_by_value:
                masked_data[key] = self.mask_value(value)
            elif self.enable_nested_masking and isinstance(value, dict):
                masked_data[key] = self.mask_fields(value)
            elif self.enable_nested_masking and isinstance(value, list):
                masked_data[key] = [
                    self.mask_fields(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                masked_data[key] = value

        return masked_data


