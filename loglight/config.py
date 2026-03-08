from dataclasses import dataclass
from typing import Callable, Optional, TextIO, Dict, List
import sys
import json
import os


@dataclass
class LoggerConfig:
    level: str = "INFO"
    output: Optional[TextIO] = sys.stdout
    include_timestamp: bool = True
    serializer: Callable = json.dumps  # function to convert dict to str
    service: str = ""
    env: str = ""
    request_id: str = ""
    redaction_rules: list = None  # list of field names to redact (deprecated, use masking options)
    sampling_rate: float = 1.0  # 1.0 means log all, 0.1 means log 10%
    rate_limit: int = 0  # logs per second, 0 means no limit

    # Field masking configuration
    enable_field_masking: bool = True  # Enable automatic field masking
    masking_strategy: str = "FULL"  # Masking strategy: FULL, PARTIAL, HASH, NULLIFY, FIRST_LAST
    custom_masking_patterns: Optional[Dict[str, str]] = None  # Custom regex patterns
    patterns_to_use: Optional[List[str]] = None  # Which built-in patterns to enable
    enable_pattern_matching: bool = True  # Enable regex pattern matching
    enable_nested_masking: bool = True  # Mask fields in nested objects
    enable_value_masking: bool = False  # Mask based on value patterns (email, CC, etc)
    partial_keep_chars: int = 2  # Chars to keep in PARTIAL strategy

    def __post_init__(self):
        self.level = os.getenv('LOG_LEVEL', self.level).upper()
        self.include_timestamp = os.getenv('LOG_INCLUDE_TIMESTAMP', str(self.include_timestamp)).lower() == 'true'
        self.service = os.getenv('LOG_SERVICE', self.service)
        self.env = os.getenv('LOG_ENV', self.env)
        self.request_id = os.getenv('LOG_REQUEST_ID', self.request_id)

        # Legacy redaction rules support
        if self.redaction_rules is None:
            redaction_str = os.getenv('LOG_REDACTION_RULES', '')
            self.redaction_rules = redaction_str.split(',') if redaction_str else []

        try:
            self.sampling_rate = float(os.getenv('LOG_SAMPLING_RATE', self.sampling_rate))
        except ValueError:
            self.sampling_rate = 1.0
        try:
            self.rate_limit = int(os.getenv('LOG_RATE_LIMIT', self.rate_limit))
        except ValueError:
            self.rate_limit = 0

        # Masking configuration from environment
        self.enable_field_masking = os.getenv('LOG_ENABLE_MASKING', str(self.enable_field_masking)).lower() == 'true'
        self.masking_strategy = os.getenv('LOG_MASKING_STRATEGY', self.masking_strategy).upper()
        self.enable_pattern_matching = os.getenv('LOG_ENABLE_PATTERN_MATCHING', str(self.enable_pattern_matching)).lower() == 'true'
        self.enable_nested_masking = os.getenv('LOG_ENABLE_NESTED_MASKING', str(self.enable_nested_masking)).lower() == 'true'
        self.enable_value_masking = os.getenv('LOG_ENABLE_VALUE_MASKING', str(self.enable_value_masking)).lower() == 'true'

        try:
            self.partial_keep_chars = int(os.getenv('LOG_PARTIAL_KEEP_CHARS', self.partial_keep_chars))
        except ValueError:
            self.partial_keep_chars = 2

