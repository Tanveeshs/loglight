# Quick Start Guide

## Installation

```bash
pip install loglight
```

## Your First Log

```python
from loglight import log

log.info("Hello, LogLight!")
```

**Output:**
```json
{"timestamp": "2025-06-22T20:02:30.123Z", "level": "info", "message": "Hello, LogLight!"}
```

## Structured Logging

```python
from loglight import log

log.info(
    "User registered",
    user_id="user_123",
    email="user@example.com",
    plan="premium"
)
```

**Output:**
```json
{
  "timestamp": "2025-06-22T20:02:30.123Z",
  "level": "info",
  "message": "User registered",
  "user_id": "user_123",
  "email": "user@example.com",
  "plan": "premium"
}
```

## Different Log Levels

```python
from loglight import log

log.debug("Debugging information")
log.info("Informational message")
log.warning("Warning message")
log.error("Error message")
log.critical("Critical message")
```

## Adding Handlers

### Console Output (Default)

```python
from loglight import log
from loglight.handlers import ConsoleHandler

handler = ConsoleHandler()
log.add_handler(handler)

log.info("This goes to console")
```

### File Output

```bash
pip install loglight
```

```python
from loglight import log
from loglight.handlers import FileHandler

handler = FileHandler(filepath="/tmp/app.log")
log.add_handler(handler)

log.info("This is logged to file")
```

### Multiple Handlers

```python
from loglight import log
from loglight.handlers import ConsoleHandler, FileHandler

log.add_handler(ConsoleHandler())
log.add_handler(FileHandler(filepath="/tmp/app.log"))

log.info("This goes to both console and file!")
```

## FastAPI Integration

```bash
pip install loglight[http] fastapi uvicorn
```

```python
from fastapi import FastAPI
from loglight import log
from loglight.middleware.fastapi import LogLightMiddleware

app = FastAPI()
app.add_middleware(LogLightMiddleware)

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    log.info("Fetching user", user_id=user_id)
    return {"user_id": user_id, "name": "John"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
```

**Request Log:**
```json
{
  "timestamp": "2025-06-22T20:02:30.123Z",
  "level": "info",
  "message": "Fetching user",
  "user_id": "user_123",
  "request_id": "abc-def-ghi"
}
```

## Flask Integration

```bash
pip install loglight[http] flask
```

```python
from flask import Flask
from loglight import log
from loglight.middleware.flask import LogLightMiddleware

app = Flask(__name__)
LogLightMiddleware(app)

@app.route("/users/<user_id>")
def get_user(user_id):
    log.info("Fetching user", user_id=user_id)
    return {"user_id": user_id}

if __name__ == "__main__":
    app.run()
```

## Configuration

```python
from loglight import log
from loglight.config import Config

config = Config(
    service_name="my-app",
    env="production",
    log_level="INFO"
)
log.configure(config)

log.info("Configured!", service_name="my-app")
```

## Error Logging

```python
from loglight import log

try:
    result = 10 / 0
except Exception as e:
    log.error("Division failed", error=str(e))
```

## Next Steps

- [Installation Guide](./INSTALLATION.md) - Detailed installation instructions
- [Configuration Guide](./CONFIGURATION.md) - Configure LogLight for your needs
- [Handler Documentation](./HANDLERS.md) - Learn about all available handlers
- [Middleware Integration](./MIDDLEWARE.md) - Integrate with Flask, FastAPI, Django
- [Examples](./EXAMPLES.md) - Real-world usage examples
- [Contributing](./CONTRIBUTING.md) - Help improve LogLight
- [Roadmap](./ROADMAP.md) - Future plans for LogLight

## Common Questions

### How do I set the log level?

```python
from loglight.config import Config

config = Config(log_level="DEBUG")
```

### How do I log to Slack?

```bash
pip install loglight[http]
```

```python
from loglight.handlers import SlackHandler

slack = SlackHandler(
    webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    min_level="ERROR"
)
log.add_handler(slack)
```

### How do I use it with FastAPI?

```python
from loglight.middleware.fastapi import LogLightMiddleware
app.add_middleware(LogLightMiddleware)
```

### Can I log to multiple places?

Yes! Add multiple handlers:

```python
log.add_handler(ConsoleHandler())
log.add_handler(FileHandler(filepath="/tmp/app.log"))
log.add_handler(SlackHandler(...))
```

### How do I trace requests across services?

LogLight automatically adds `request_id` to logs through middleware. Use it in your logs:

```python
log.info("Processing", request_id="abc-123")
```

## Getting Help

- 📖 [Documentation](./README.md)
- 🐛 [Report an Issue](https://github.com/yourusername/loglight/issues)
- 💬 [Discussions](https://github.com/yourusername/loglight/discussions)

