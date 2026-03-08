# loglight/logger.py
import contextvars
import random
import threading
import time
from datetime import datetime

from loglight.config import LoggerConfig
from loglight.handlers.ConsoleHandler import ConsoleHandler
from loglight.masking import MaskingStrategy, ValuePatternMasker
from loglight.routing import RouterHandler, RoutingConfig


class Logger:
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    # Context variable for request_id
    request_id_context: contextvars.ContextVar = contextvars.ContextVar(
        "request_id", default=None
    )

    def __init__(self, config: LoggerConfig = None, handler=None):
        self.config = config or LoggerConfig()
        self.level = self.LEVELS.get(self.config.level, 20)

        # Support both single handler (backward compatible) and multiple handlers
        self.handlers = []
        if handler:
            self.handlers.append(handler)
        else:
            self.handlers.append(ConsoleHandler(self.config.output))

        self._log_count = 0
        self._last_reset = time.time()
        self._lock = threading.Lock()
        self._metrics = {"logs": 0, "errors": 0}

        # Initialize field masker
        self.field_masker = ValuePatternMasker(
            enable_masking=self.config.enable_field_masking,
            strategy=self.config.masking_strategy,
            custom_patterns=self.config.custom_masking_patterns,
            patterns_to_use=self.config.patterns_to_use,
            enable_pattern_matching=self.config.enable_pattern_matching,
            enable_nested_masking=self.config.enable_nested_masking,
            enable_value_masking=self.config.enable_value_masking,
            partial_keep_chars=self.config.partial_keep_chars,
        )

    @property
    def handler(self):
        """Backward-compatible access to the primary handler."""
        return self.handlers[0] if self.handlers else None

    def add_handler(self, handler, routing_config: RoutingConfig = None) -> None:
        """Add a handler with optional routing configuration.

        Args:
            handler: Handler instance to add
            routing_config: RoutingConfig to determine when to use this handler.
                           If None, handler receives all logs.

        Example:
            # Handler for all logs
            logger.add_handler(ConsoleHandler())

            # Handler only for ERROR and CRITICAL
            error_config = RoutingConfig([
                RoutingRule(RoutingRuleType.LEVEL, value="ERROR")
            ])
            logger.add_handler(SlackHandler(webhook_url="..."), error_config)
        """
        if routing_config is not None:
            handler = RouterHandler(handler, routing_config)
        self.handlers.append(handler)

    def remove_handler(self, handler) -> bool:
        """Remove a handler.

        Args:
            handler: Handler instance to remove

        Returns:
            True if handler was removed, False if not found
        """
        try:
            self.handlers.remove(handler)
            return True
        except ValueError:
            return False

    def clear_handlers(self) -> None:
        """Clear all handlers."""
        self.handlers.clear()

    def log(self, level, event, details=None, **extra):
        lvl_value = self.LEVELS.get(level.upper(), 20)
        if lvl_value < self.level:
            return

        # Sampling
        if random.random() > self.config.sampling_rate:
            return

        # Rate limiting
        with self._lock:
            current_time = time.time()
            if current_time - self._last_reset > 1:
                self._log_count = 0
                self._last_reset = current_time
            if 0 < self.config.rate_limit <= self._log_count:
                return
            self._log_count += 1

        self._metrics["logs"] += 1
        if level.upper() in ["ERROR", "CRITICAL"]:
            self._metrics["errors"] += 1

        log_entry = {
            "level": level.lower(),
            "message": event,
        }
        if self.config.include_timestamp:
            log_entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
        if self.config.service:
            log_entry["service"] = self.config.service
        if self.config.env:
            log_entry["env"] = self.config.env
        request_id = self.config.request_id or self.request_id_context.get()
        if request_id:
            log_entry["request_id"] = request_id
        # Flatten extra fields into top level
        log_entry.update(extra)
        # If details provided, merge into top level too
        if details:
            log_entry.update(details)

        # Apply field masking
        log_entry = self.field_masker.mask_fields(log_entry)

        # Legacy: Apply simple redaction rules (deprecated, superseded by field masking)
        for field in self.config.redaction_rules:
            if field in log_entry:
                log_entry[field] = "***"

        serialized = self.config.serializer(log_entry)

        # Emit to all handlers
        for handler in self.handlers:
            try:
                # Pass log_entry for routing-aware handlers
                if isinstance(handler, RouterHandler):
                    handler.emit(serialized, log_entry)
                else:
                    handler.emit(serialized)
            except Exception as e:
                # Log handler errors to stderr
                import sys

                print(
                    f"Error in handler {handler.__class__.__name__}: {e}",
                    file=sys.stderr,
                )

    def debug(self, event, details=None, **extra):
        self.log("DEBUG", event, details, **extra)

    def info(self, event, details=None, **extra):
        self.log("INFO", event, details, **extra)

    def warning(self, event, details=None, **extra):
        self.log("WARNING", event, details, **extra)

    def error(self, event, details=None, **extra):
        self.log("ERROR", event, details, **extra)

    def critical(self, event, details=None, **extra):
        self.log("CRITICAL", event, details, **extra)

    # Field masking helper methods
    def add_masking_pattern(self, name: str, pattern: str) -> None:
        """Add a custom masking pattern at runtime.

        Args:
            name: Name of the pattern
            pattern: Regex pattern to match field names

        Example:
            log.add_masking_pattern('custom_secret', r'(?i)^custom_secret_.*$')
        """
        self.field_masker.add_custom_pattern(name, pattern)

    def remove_masking_pattern(self, name: str) -> None:
        """Remove a masking pattern.

        Args:
            name: Name of the pattern to remove
        """
        self.field_masker.remove_pattern(name)

    def get_active_masking_patterns(self) -> list:
        """Get list of active masking patterns.

        Returns:
            List of active pattern names
        """
        return self.field_masker.get_active_patterns()

    def enable_masking(self) -> None:
        """Enable field masking globally."""
        self.field_masker.enable_masking = True

    def disable_masking(self) -> None:
        """Disable field masking globally."""
        self.field_masker.enable_masking = False

    def set_masking_strategy(self, strategy: str) -> None:
        """Change masking strategy at runtime.

        Args:
            strategy: Masking strategy (FULL, PARTIAL, HASH, NULLIFY, FIRST_LAST)

        Example:
            log.set_masking_strategy('PARTIAL')
        """
        self.field_masker.strategy = ValuePatternMasker._parse_strategy(strategy)

    def get_metrics(self) -> dict:
        """Get logger metrics.

        Returns:
            Dictionary with logs count and errors count
        """
        return self._metrics.copy()

    def configure(self, config: LoggerConfig) -> None:
        """Reconfigure the logger with a new configuration.

        Args:
            config: New LoggerConfig to apply

        Example:
            config = LoggerConfig(masking_strategy='PARTIAL')
            log.configure(config)
        """
        self.config = config
        self.level = self.LEVELS.get(self.config.level, 20)

        # Reinitialize field masker with new config
        self.field_masker = ValuePatternMasker(
            enable_masking=self.config.enable_field_masking,
            strategy=self.config.masking_strategy,
            custom_patterns=self.config.custom_masking_patterns,
            patterns_to_use=self.config.patterns_to_use,
            enable_pattern_matching=self.config.enable_pattern_matching,
            enable_nested_masking=self.config.enable_nested_masking,
            enable_value_masking=self.config.enable_value_masking,
            partial_keep_chars=self.config.partial_keep_chars,
        )
