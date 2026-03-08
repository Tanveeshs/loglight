# Configuration Guide

## Overview

LogLight uses a flexible configuration system to set up logging handlers, formatters, and global settings.

## Basic Configuration

### Environment Variables

```bash
# Set the logging level
export LOGLIGHT_LOG_LEVEL=INFO

# Set the service name
export LOGLIGHT_SERVICE_NAME=my-service

# Set the environment
export LOGLIGHT_ENV=production
```

### Python Configuration

Configure LogLight in your application startup:

```python
from loglight import log
from loglight.config import Config

# Create a configuration
config = Config(
    service_name="my-service",
    env="production",
    log_level="INFO"
)

# Configure the logger
log.configure(config)
```

## Handler Configuration

### Console Handler

Output logs to stdout:

```python
from loglight.handlers import ConsoleHandler

console_handler = ConsoleHandler()
log.add_handler(console_handler)
```

### File Handler

Write logs to a file:

```python
from loglight.handlers import FileHandler

file_handler = FileHandler(filepath="/var/log/app.log")
log.add_handler(file_handler)
```

### Rotating File Handler

Automatically rotate log files:

```python
from loglight.handlers import RotatingFileHandler

rotating_handler = RotatingFileHandler(
    filepath="/var/log/app.log",
    max_bytes=10 * 1024 * 1024,  # 10 MB
    backup_count=5  # Keep 5 backups
)
log.add_handler(rotating_handler)
```

### Slack Handler

Send logs to Slack:

```python
from loglight.handlers import SlackHandler

slack_handler = SlackHandler(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    min_level="ERROR"  # Only send ERROR and above
)
log.add_handler(slack_handler)
```

### HTTP Handler

Send logs to an HTTP endpoint:

```python
from loglight.handlers import HTTPHandler

http_handler = HTTPHandler(
    url="https://api.example.com/logs",
    method="POST",
    headers={"Authorization": "Bearer token123"}
)
log.add_handler(http_handler)
```

### Webhook Handler

Send logs to a webhook:

```python
from loglight.handlers import WebhookHandler

webhook_handler = WebhookHandler(
    url="https://webhook.example.com/logs"
)
log.add_handler(webhook_handler)
```

### S3 Handler

Store logs in AWS S3:

```python
from loglight.handlers import S3Handler

s3_handler = S3Handler(
    bucket="my-logs-bucket",
    prefix="app-logs/",
    region="us-east-1"
)
log.add_handler(s3_handler)
```

### Kafka Handler

Send logs to Apache Kafka:

```python
from loglight.handlers import KafkaHandler

kafka_handler = KafkaHandler(
    bootstrap_servers="localhost:9092",
    topic="app-logs"
)
log.add_handler(kafka_handler)
```

### Elasticsearch Handler

Send logs to Elasticsearch:

```python
from loglight.handlers import ElasticsearchHandler

es_handler = ElasticsearchHandler(
    hosts="localhost:9200",
    index="app-logs"
)
log.add_handler(es_handler)
```

### Syslog Handler

Send logs to syslog:

```python
from loglight.handlers import SyslogHandler

syslog_handler = SyslogHandler(
    address="/dev/log"
)
log.add_handler(syslog_handler)
```

## Global Configuration Options

### Log Levels

Supported log levels (in order of severity):
- `DEBUG` - Detailed information for debugging
- `INFO` - General informational messages
- `WARNING` - Warning messages for potentially harmful situations
- `ERROR` - Error messages for serious problems
- `CRITICAL` - Critical messages for very serious errors

```python
config = Config(log_level="DEBUG")
```

### Service Configuration

```python
config = Config(
    service_name="api-service",
    service_version="1.0.0",
    env="production",
    datacenter="us-east-1"
)
```

### Async Configuration

```python
config = Config(
    async_mode=True,
    queue_size=1000,
    worker_threads=2
)
```

## Example Complete Configuration

```python
from loglight import log
from loglight.config import Config
from loglight.handlers import ConsoleHandler, FileHandler, SlackHandler, S3Handler

# Create base configuration
config = Config(
    service_name="user-api",
    service_version="1.0.0",
    env="production",
    log_level="INFO"
)

# Configure the logger
log.configure(config)

# Add handlers
log.add_handler(ConsoleHandler())
log.add_handler(FileHandler(filepath="/var/log/user-api.log"))
log.add_handler(RotatingFileHandler(
    filepath="/var/log/user-api-rotating.log",
    max_bytes=50 * 1024 * 1024,
    backup_count=10
))
log.add_handler(SlackHandler(
    webhook_url="https://hooks.slack.com/...",
    min_level="ERROR"
))
log.add_handler(S3Handler(
    bucket="company-logs",
    prefix="user-api/"
))

# Start logging
log.info("Application started", version="1.0.0")
```

## Environment-Based Configuration

```python
import os
from loglight import log
from loglight.config import Config

env = os.getenv("APP_ENV", "development")

if env == "production":
    config = Config(
        service_name="api",
        env="production",
        log_level="WARNING"
    )
    # Add production handlers
else:
    config = Config(
        service_name="api",
        env="development",
        log_level="DEBUG"
    )
    # Add development handlers

log.configure(config)
```

