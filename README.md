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

---

## 📦 Installation

```bash
pip install loglight

```
## 🧪 Usage
```python

from loglight import log
log.info("User created", request_id="abc123", user_id="user_1", metadata={"role": "admin"})

```
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
- Base JSON logger
- Async queue writer
- FastAPI + Flask middleware
- Django middleware
- S3 / syslog / remote sinks
- Auto-log decorators
- Field redaction
- Structured exception tracing