# loglight

**A lightweight structured logging library for Python apps**  
Minimal config, human-readable JSON logs, and automatic request tracing.

---

## 🚀 Features

- 🔹 One-line structured logging: `log.info("message", user_id=..., request_id=...)`
- 🔹 Built-in request context support (Flask, FastAPI, Django)
- 🔹 Asynchronous background log writer
- 🔹 Standard JSON schema with timestamp, level, metadata
- 🔹 Pluggable sinks (file, stdout, etc.)
- 🔹 Easily trace requests across services using request_id
- 🔹 **🔒 Automatic Field Masking**: Protect passwords, API keys, credit cards, and sensitive data
- 🔹 **Multiple Masking Strategies**: FULL, PARTIAL, HASH, NULLIFY, FIRST_LAST

---

## 📦 Installation

```bash
pip install loglight

# For HTTP handlers (Slack, Webhook, HTTP)
pip install loglight[http]

# For S3 handler
pip install loglight[s3]
```

## 🧪 Usage
```python

from loglight import log
log.info("User created", request_id="abc123", user_id="user_1", metadata={"role": "admin"})

```

## 🔒 Automatic Field Masking

LogLight automatically masks sensitive fields like passwords, API keys, and credit cards:

```python
from loglight import log

# These fields are automatically masked - no configuration needed!
log.info("User login",
    username="john_doe",
    password="super_secret",     # ✅ Automatically masked
    api_key="sk_live_abc123"     # ✅ Automatically masked
)

# Output:
# {
#   "message": "User login",
#   "username": "john_doe",
#   "password": "***",
#   "api_key": "***"
# }
```

See [Field Masking Guide](./docs/MASKING.md) for advanced configuration and strategies.


## With Middleware (FastAPI)
```python
from fastapi import FastAPI
from loglight.middleware.fastapi import LogLightMiddleware

app = FastAPI()
app.add_middleware(LogLightMiddleware)
```

## 📁 Log Output Example
```json
{
  "timestamp": "2025-06-22T20:02:30.123Z",
  "level": "info",
  "message": "User created",
  "service": "user-service",
  "request_id": "abc123",
  "user_id": "user_1",
  "env": "production",
  "metadata": {
    "role": "admin"
  }
}
```

## 🔧 Roadmap
- ✅ Base JSON logger
- ✅ Async queue writer
- ✅ FastAPI + Flask middleware
- ✅ Django middleware
- ✅ S3 / syslog / remote sinks
- ✅ Auto-log decorators
- 🚧 Field redaction
- 🚧 Structured exception tracing

## 📋 Future Plans

### Short Term (v0.2)
- **Performance Optimization**: Improve async queue handling and reduce latency
- **Enhanced Error Handling**: Better error messages and debugging for handler failures
- **Field Redaction**: Automatic masking of sensitive fields (PII, tokens, passwords)
- **Structured Exception Tracing**: Improved stack trace formatting and context preservation

### Medium Term (v0.3-v0.4)
- **Distributed Tracing**: OpenTelemetry integration for better observability
- **Log Aggregation**: Built-in support for common log aggregation services (Splunk, DataDog, New Relic)
- **Advanced Filtering**: Runtime log level and filtering based on conditions
- **Custom Formatters**: User-defined log formatting strategies
- **Rate Limiting**: Prevent log spam with intelligent rate limiting

### Long Term (v1.0+)
- **Performance Benchmarking**: Comprehensive performance metrics and optimization
- **CLI Tools**: Command-line utilities for log analysis and debugging
- **Web Dashboard**: Simple web interface for log visualization
- **Persistence Layer**: Built-in log persistence and querying capabilities
- **Multi-language Support**: SDKs for Node.js, Go, and Java

For more details, see [ROADMAP.md](./docs/ROADMAP.md)

---

## 📚 Documentation

- [Quick Start](./docs/QUICKSTART.md)
- [Installation Guide](./docs/INSTALLATION.md)
- [Configuration Guide](./docs/CONFIGURATION.md)
- [🔒 Field Masking Guide](./docs/MASKING.md) - **NEW!** Automatic data protection
- [Handler Documentation](./docs/HANDLERS.md)
- [Middleware Integration](./docs/MIDDLEWARE.md)
- [Examples](./docs/EXAMPLES.md)
- [Contributing](./docs/CONTRIBUTING.md)
