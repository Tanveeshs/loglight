# Middleware Integration Guide

## Overview

LogLight provides middleware for popular Python web frameworks to automatically capture request information and add it to logs.

## Flask Integration

### Installation

```bash
pip install loglight[http]
pip install flask
```

### Basic Setup

```python
from flask import Flask
from loglight import log
from loglight.middleware.flask import LogLightMiddleware

app = Flask(__name__)

# Add the LogLight middleware
LogLightMiddleware(app)

@app.route('/users/<user_id>')
def get_user(user_id):
    log.info("Fetching user", user_id=user_id)
    return {"user_id": user_id}

if __name__ == '__main__':
    app.run()
```

### Features

- Automatic request ID tracking
- Request/response logging
- Execution time tracking
- Error logging with context

### Sample Log Output

```json
{
  "timestamp": "2025-06-22T20:02:30.123Z",
  "level": "info",
  "message": "GET /users/123",
  "request_id": "abc-def-ghi",
  "method": "GET",
  "path": "/users/123",
  "status_code": 200,
  "duration_ms": 45.2,
  "user_id": "123"
}
```

---

## FastAPI Integration

### Installation

```bash
pip install loglight[http]
pip install fastapi uvicorn
```

### Basic Setup

```python
from fastapi import FastAPI
from loglight import log
from loglight.middleware.fastapi import LogLightMiddleware

app = FastAPI()

# Add the LogLight middleware
app.add_middleware(LogLightMiddleware)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    log.info("Fetching user", user_id=user_id)
    return {"user_id": user_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Features

- Automatic request ID generation
- Async-safe logging
- Request/response metadata
- Exception logging
- Performance tracking

### Advanced Setup

```python
from fastapi import FastAPI
from loglight import log
from loglight.config import Config
from loglight.middleware.fastapi import LogLightMiddleware
from loglight.handlers import ConsoleHandler, FileHandler

# Configure loglight
config = Config(
    service_name="user-api",
    env="production",
    log_level="INFO"
)
log.configure(config)

# Add handlers
log.add_handler(ConsoleHandler())
log.add_handler(FileHandler(filepath="/var/log/user-api.log"))

app = FastAPI()
app.add_middleware(LogLightMiddleware)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    log.info("User fetch request", user_id=user_id)
    return {"user_id": user_id}
```

---

## Django Integration

### Installation

```bash
pip install loglight[http]
pip install django
```

### Configuration

1. Add to `settings.py`:

```python
INSTALLED_APPS = [
    # ... your apps ...
]

MIDDLEWARE = [
    # ... other middleware ...
    'loglight.middleware.django.LogLightMiddleware',
]

LOGLIGHT = {
    'SERVICE_NAME': 'my-django-app',
    'ENV': 'production',
    'LOG_LEVEL': 'INFO',
}
```

2. Initialize in your app:

```python
# In your Django app's __init__.py
from loglight import log
from loglight.config import Config

config = Config(
    service_name="my-django-app",
    env="production",
    log_level="INFO"
)
log.configure(config)
```

### Usage in Views

```python
from django.http import JsonResponse
from loglight import log

def get_user(request, user_id):
    log.info("Fetching user", user_id=user_id)
    return JsonResponse({"user_id": user_id})
```

### Features

- Request/response logging
- User tracking
- Session information
- Error and exception logging
- Request ID propagation

---

## Request ID Propagation

All middleware implementations support automatic request ID tracking:

```python
from loglight import log
from flask import request

@app.route('/api/users/<user_id>')
def get_user(user_id):
    # Request ID is automatically available in logs
    log.info("User accessed", user_id=user_id)
    # Request ID is included automatically
    return {"user_id": user_id}
```

### Custom Request ID

```python
from loglight import log

log.info("Custom event", request_id="custom-123")
```

---

## Excluding Paths

Exclude certain paths from logging:

```python
from loglight.middleware.fastapi import LogLightMiddleware

LogLightMiddleware(
    app,
    exclude_paths=["/health", "/metrics", "/static/*"]
)
```

---

## Sensitive Data Redaction

Automatically redact sensitive fields:

```python
from loglight import log
from loglight.config import Config

config = Config(
    service_name="api",
    sensitive_fields=[
        "password",
        "api_key",
        "credit_card",
        "ssn"
    ]
)
log.configure(config)

# These fields will be masked
log.info("Login", password="secret123")  # password will be redacted
```

---

## Error Handling

Middleware automatically captures errors:

```python
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        # Your logic
        return get_user_from_db(user_id)
    except Exception as e:
        # Automatically logged by middleware
        log.error("Failed to fetch user", user_id=user_id, error=str(e))
        raise
```

---

## Performance Considerations

### Async Logging

Use async logging for better performance:

```python
from loglight import log
from loglight.config import Config

config = Config(
    service_name="api",
    async_mode=True,
    queue_size=5000
)
log.configure(config)
```

### Log Sampling

Sample logs in high-traffic scenarios:

```python
from loglight import log

# Log only 10% of INFO level messages
log.info("Request processed", sample_rate=0.1)
```

---

## Multiple Framework Example

Using LogLight in a microservices architecture:

```python
# service1.py - FastAPI
from fastapi import FastAPI
from loglight import log
from loglight.middleware.fastapi import LogLightMiddleware

app1 = FastAPI()
app1.add_middleware(LogLightMiddleware)

# service2.py - Flask
from flask import Flask
from loglight import log
from loglight.middleware.flask import LogLightMiddleware

app2 = Flask(__name__)
LogLightMiddleware(app2)

# Both services will have consistent logging
# Request IDs are propagated across services
```

---

## Troubleshooting

### Middleware not capturing logs

Ensure middleware is added before route definitions:

```python
# ❌ Wrong
app = FastAPI()

@app.get("/")
def home():
    return {}

app.add_middleware(LogLightMiddleware)  # Too late!

# ✅ Correct
app = FastAPI()
app.add_middleware(LogLightMiddleware)  # Add first

@app.get("/")
def home():
    return {}
```

### Request ID not propagating

Ensure the middleware is properly initialized and request context is available in your logging calls.

### Performance issues

- Use `async_mode=True` in configuration
- Exclude high-frequency paths
- Consider log sampling

