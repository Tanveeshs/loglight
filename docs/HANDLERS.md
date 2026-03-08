# Handler Documentation

## Overview

LogLight provides multiple handler types to send logs to different destinations. Each handler extends the `BaseHandler` class and implements the `emit()` method.

## Handler Types

### ConsoleHandler

Outputs logs to the console (stdout by default).

**Parameters:**
- `stream` (optional): Output stream (default: `sys.stdout`)

**Example:**
```python
from loglight.handlers import ConsoleHandler

handler = ConsoleHandler()
log.add_handler(handler)
```

**Output:**
```json
{"timestamp": "2025-06-22T20:02:30.123Z", "level": "info", "message": "User login"}
```

---

### FileHandler

Writes logs to a file.

**Parameters:**
- `filepath` (required): Path to the log file
- `encoding` (optional): File encoding (default: `utf-8`)

**Example:**
```python
from loglight.handlers import FileHandler

handler = FileHandler(filepath="/var/log/app.log")
log.add_handler(handler)
```

---

### RotatingFileHandler

Automatically rotates log files based on size.

**Parameters:**
- `filepath` (required): Path to the log file
- `max_bytes` (required): Maximum file size before rotation (in bytes)
- `backup_count` (required): Number of backup files to keep

**Example:**
```python
from loglight.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    filepath="/var/log/app.log",
    max_bytes=10 * 1024 * 1024,  # 10 MB
    backup_count=5
)
log.add_handler(handler)
```

**Generated Files:**
- `app.log` - Current log file
- `app.log.1` - First backup
- `app.log.2` - Second backup
- etc.

---

### SlackHandler

Sends logs to a Slack channel via webhook.

**Parameters:**
- `webhook_url` (required): Slack webhook URL
- `min_level` (optional): Minimum log level to send (default: `ERROR`)
- `channel` (optional): Slack channel name or ID
- `username` (optional): Bot username (default: `LogLight`)

**Example:**
```python
from loglight.handlers import SlackHandler

handler = SlackHandler(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    min_level="ERROR"
)
log.add_handler(handler)
```

---

### WebhookHandler

Sends logs to a custom webhook endpoint.

**Parameters:**
- `url` (required): Webhook URL
- `method` (optional): HTTP method (default: `POST`)
- `headers` (optional): Custom HTTP headers
- `timeout` (optional): Request timeout in seconds

**Example:**
```python
from loglight.handlers import WebhookHandler

handler = WebhookHandler(
    url="https://webhook.example.com/logs",
    headers={"Authorization": "Bearer token123"}
)
log.add_handler(handler)
```

---

### HTTPHandler

Sends logs to an HTTP endpoint with advanced options.

**Parameters:**
- `url` (required): HTTP endpoint URL
- `method` (optional): HTTP method (default: `POST`)
- `headers` (optional): Custom headers
- `auth` (optional): Authentication tuple (username, password)
- `timeout` (optional): Request timeout
- `verify_ssl` (optional): Verify SSL certificates (default: `True`)

**Example:**
```python
from loglight.handlers import HTTPHandler

handler = HTTPHandler(
    url="https://api.example.com/logs",
    method="POST",
    headers={"Content-Type": "application/json"},
    auth=("user", "password")
)
log.add_handler(handler)
```

---

### S3Handler

Stores logs in AWS S3.

**Parameters:**
- `bucket` (required): S3 bucket name
- `prefix` (optional): S3 key prefix (default: empty)
- `region` (optional): AWS region (default: from AWS config)
- `access_key` (optional): AWS access key ID
- `secret_key` (optional): AWS secret access key

**Example:**
```python
from loglight.handlers import S3Handler

handler = S3Handler(
    bucket="my-logs-bucket",
    prefix="app-logs/",
    region="us-east-1"
)
log.add_handler(handler)
```

---

### KafkaHandler

Sends logs to Apache Kafka topics.

**Parameters:**
- `bootstrap_servers` (required): Kafka broker addresses
- `topic` (required): Kafka topic name
- `sasl_mechanism` (optional): SASL mechanism for authentication
- `sasl_plain_username` (optional): Username for SASL
- `sasl_plain_password` (optional): Password for SASL

**Example:**
```python
from loglight.handlers import KafkaHandler

handler = KafkaHandler(
    bootstrap_servers="localhost:9092",
    topic="app-logs"
)
log.add_handler(handler)
```

---

### ElasticsearchHandler

Sends logs to Elasticsearch.

**Parameters:**
- `hosts` (required): Elasticsearch host(s)
- `index` (required): Elasticsearch index name
- `doc_type` (optional): Document type (default: `_doc`)
- `username` (optional): Elasticsearch username
- `password` (optional): Elasticsearch password

**Example:**
```python
from loglight.handlers import ElasticsearchHandler

handler = ElasticsearchHandler(
    hosts="localhost:9200",
    index="app-logs"
)
log.add_handler(handler)
```

---

### SyslogHandler

Sends logs to syslog.

**Parameters:**
- `address` (optional): Syslog address (default: `/dev/log`)
- `facility` (optional): Syslog facility

**Example:**
```python
from loglight.handlers import SyslogHandler

handler = SyslogHandler(
    address="/dev/log"
)
log.add_handler(handler)
```

---

### AsyncQueueHandler

A wrapper for asynchronous log processing using a queue.

**Parameters:**
- `target_handler` (required): The underlying handler to wrap
- `queue_size` (optional): Queue size (default: 1000)

**Example:**
```python
from loglight.handlers import AsyncQueueHandler, FileHandler

file_handler = FileHandler(filepath="/var/log/app.log")
async_handler = AsyncQueueHandler(target_handler=file_handler)
log.add_handler(async_handler)
```

---

## Handler Configuration

### Minimum Log Level

Set a minimum log level for a handler:

```python
handler = SlackHandler(
    webhook_url="https://hooks.slack.com/...",
    min_level="ERROR"
)
```

Only logs with level `ERROR` or higher will be sent to Slack.

### Chaining Multiple Handlers

```python
from loglight.handlers import ConsoleHandler, FileHandler, SlackHandler

# Console for all logs
log.add_handler(ConsoleHandler())

# File for all logs
log.add_handler(FileHandler(filepath="/var/log/app.log"))

# Slack only for errors
log.add_handler(SlackHandler(
    webhook_url="https://hooks.slack.com/...",
    min_level="ERROR"
))
```

---

## Custom Handler Implementation

Create a custom handler by extending `BaseHandler`:

```python
from loglight.handlers import BaseHandler
import json

class CustomHandler(BaseHandler):
    def __init__(self, custom_param):
        super().__init__()
        self.custom_param = custom_param
    
    def emit(self, record):
        """
        Emit a log record.
        
        Args:
            record: JSON log record as a string
        """
        # Parse the JSON
        log_data = json.loads(record)
        
        # Process the log
        self.process_log(log_data)
    
    def process_log(self, log_data):
        # Custom logic here
        print(f"Custom: {log_data}")
```

---

## Error Handling

Handlers include built-in error handling:

```python
handler = HTTPHandler(
    url="https://api.example.com/logs",
    timeout=5
)
log.add_handler(handler)

# If the HTTP request fails, the log is queued for retry
log.error("This will be retried if delivery fails")
```

---

## Performance Considerations

### File Handlers
- Use `RotatingFileHandler` for long-running applications
- Configure appropriate `max_bytes` and `backup_count`

### Network Handlers
- Consider using `AsyncQueueHandler` for better performance
- Set appropriate timeouts to prevent blocking

### High-Volume Logging
- Use batch processing where available
- Consider log sampling for non-critical logs
- Monitor queue size for async handlers

---

## Migration Guide

### From Python's logging module

**Before:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("User login")
```

**After:**
```python
from loglight import log
log.info("User login", user_id="123")
```

### From other JSON logging libraries

**Before:**
```python
json_logger.info({"event": "login", "user_id": "123"})
```

**After:**
```python
from loglight import log
log.info("User login", user_id="123")
```

LogLight automatically converts keyword arguments to structured JSON.

