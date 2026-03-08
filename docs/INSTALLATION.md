# Installation Guide

## Requirements

- Python 3.7 or higher
- pip package manager

## Basic Installation

```bash
pip install loglight
```

## Installation with Optional Dependencies

LogLight supports optional dependencies for specific handlers:

### HTTP Handlers (Slack, Webhook, HTTP)
```bash
pip install loglight[http]
```

This includes the `requests` library needed for:
- SlackHandler
- WebhookHandler
- HTTPHandler

### AWS S3 Handler
```bash
pip install loglight[s3]
```

This includes the `boto3` library needed for:
- S3Handler

### Kafka Handler
```bash
pip install loglight[kafka]
```

This includes the `kafka-python` library needed for:
- KafkaHandler

### All Optional Dependencies
```bash
pip install loglight[http,s3,kafka]
```

## Development Installation

If you want to contribute to LogLight development:

```bash
git clone https://github.com/yourusername/loglight.git
cd loglight
pip install -e ".[http,s3,kafka]"
pip install pytest pytest-cov black flake8
```

## Verification

To verify the installation:

```python
from loglight import log

# Test basic logging
log.info("Installation successful!", version="0.1.0")
```

You should see JSON output in your console.

## Troubleshooting

### Import Error: ModuleNotFoundError: No module named 'loglight'
- Ensure you've run `pip install loglight`
- Check that you're using the correct Python environment

### Handler Not Found Error
- Install the corresponding optional dependencies
- For example, for Slack: `pip install loglight[http]`

### Missing boto3 Error
- Install S3 dependencies: `pip install loglight[s3]`

### Missing kafka-python Error
- Install Kafka dependencies: `pip install loglight[kafka]`

## Upgrading LogLight

To upgrade to the latest version:

```bash
pip install --upgrade loglight
```

## Uninstalling

To remove LogLight:

```bash
pip uninstall loglight
```

