# Examples

## Basic Usage

### Simple Logging

```python
from loglight import log

log.info("Application started")
log.warning("Low memory")
log.error("Database connection failed")
log.debug("Debug information")
```

### Structured Logging with Context

```python
from loglight import log

log.info(
    "User created",
    user_id="user_123",
    email="user@example.com",
    role="admin"
)
```

### Output

```json
{
  "timestamp": "2025-06-22T20:02:30.123Z",
  "level": "info",
  "message": "User created",
  "user_id": "user_123",
  "email": "user@example.com",
  "role": "admin"
}
```

---

## Application Examples

### FastAPI User Service

```python
from fastapi import FastAPI, HTTPException
from loglight import log
from loglight.config import Config
from loglight.middleware.fastapi import LogLightMiddleware
from loglight.handlers import ConsoleHandler, SlackHandler

# Configure logging
config = Config(
    service_name="user-service",
    env="production",
    log_level="INFO"
)
log.configure(config)

# Add handlers
log.add_handler(ConsoleHandler())
log.add_handler(SlackHandler(
    webhook_url="https://hooks.slack.com/...",
    min_level="ERROR"
))

# Create FastAPI app
app = FastAPI()
app.add_middleware(LogLightMiddleware)

# Routes
@app.post("/users")
async def create_user(name: str, email: str):
    log.info("Creating user", name=name, email=email)
    
    try:
        # Create user logic
        user_id = "user_" + str(hash(email))
        log.info("User created successfully", user_id=user_id, email=email)
        return {"user_id": user_id, "name": name}
    except Exception as e:
        log.error("Failed to create user", email=email, error=str(e))
        raise HTTPException(status_code=400, detail="Failed to create user")

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    log.info("Fetching user", user_id=user_id)
    
    # Fetch user logic
    user = {"id": user_id, "name": "John Doe"}
    
    log.info("User fetched", user_id=user_id, found=True)
    return user
```

---

### Flask E-commerce Service

```python
from flask import Flask, request, jsonify
from loglight import log
from loglight.middleware.flask import LogLightMiddleware
from loglight.handlers import FileHandler, RotatingFileHandler

# Initialize Flask app
app = Flask(__name__)

# Add LogLight middleware
LogLightMiddleware(app)

# Add file handlers
log.add_handler(FileHandler(filepath="/var/log/ecommerce.log"))
log.add_handler(RotatingFileHandler(
    filepath="/var/log/ecommerce-rotating.log",
    max_bytes=50 * 1024 * 1024,
    backup_count=10
))

# Routes
@app.route('/products/<product_id>')
def get_product(product_id):
    log.info("Fetching product", product_id=product_id)
    
    # Database lookup
    product = {
        "id": product_id,
        "name": "Sample Product",
        "price": 99.99
    }
    
    log.info("Product fetched", product_id=product_id, price=product["price"])
    return jsonify(product)

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data.get('user_id')
    items = data.get('items', [])
    
    log.info("Creating order", user_id=user_id, item_count=len(items))
    
    try:
        # Process order
        order_id = "order_12345"
        total = sum(item['price'] for item in items)
        
        log.info(
            "Order created successfully",
            user_id=user_id,
            order_id=order_id,
            total=total,
            item_count=len(items)
        )
        
        return jsonify({"order_id": order_id, "total": total})
    except Exception as e:
        log.error(
            "Failed to create order",
            user_id=user_id,
            error=str(e),
            item_count=len(items)
        )
        return jsonify({"error": "Order creation failed"}), 400

if __name__ == '__main__':
    log.info("Starting e-commerce service")
    app.run(debug=False)
```

---

### Django API with Request Tracking

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'loglight.middleware.django.LogLightMiddleware',
]

# views.py
from django.http import JsonResponse
from loglight import log

def list_articles(request):
    log.info("Listing articles")
    
    articles = [
        {"id": 1, "title": "Article 1"},
        {"id": 2, "title": "Article 2"},
    ]
    
    log.info("Articles listed", count=len(articles))
    return JsonResponse({"articles": articles})

def create_article(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        title = data.get('title')
        
        log.info("Creating article", title=title)
        
        try:
            # Create article logic
            article_id = 1
            log.info("Article created", article_id=article_id, title=title)
            return JsonResponse({"id": article_id, "title": title})
        except Exception as e:
            log.error("Failed to create article", title=title, error=str(e))
            return JsonResponse({"error": "Failed to create article"}, status=400)

def get_article(request, article_id):
    log.info("Fetching article", article_id=article_id)
    
    article = {"id": article_id, "title": "Sample Article", "content": "..."}
    
    log.info("Article fetched", article_id=article_id)
    return JsonResponse(article)
```

---

## Advanced Patterns

### Error Handling and Logging

```python
from loglight import log
import traceback

def process_payment(order_id, amount):
    log.info("Processing payment", order_id=order_id, amount=amount)
    
    try:
        # Payment processing logic
        if amount < 0:
            raise ValueError("Amount must be positive")
        
        # Simulate payment processing
        result = charge_credit_card(order_id, amount)
        
        log.info(
            "Payment processed successfully",
            order_id=order_id,
            amount=amount,
            transaction_id=result['transaction_id']
        )
        return result
    
    except ValueError as e:
        log.error(
            "Payment validation error",
            order_id=order_id,
            amount=amount,
            error=str(e)
        )
        raise
    
    except Exception as e:
        log.critical(
            "Payment processing failed",
            order_id=order_id,
            amount=amount,
            error=str(e),
            traceback=traceback.format_exc()
        )
        raise
```

### Context Management

```python
from loglight import log
from contextlib import contextmanager

@contextmanager
def log_operation(operation_name, **context):
    """Context manager for structured operation logging"""
    log.info(f"Starting {operation_name}", **context)
    
    try:
        yield
        log.info(f"Completed {operation_name}", **context)
    except Exception as e:
        log.error(f"Failed {operation_name}", **context, error=str(e))
        raise

# Usage
with log_operation("database_migration", version="1.0.0"):
    # Migration logic
    pass
```

### Request/Response Logging

```python
from loglight import log
from functools import wraps
import json
import time

def log_endpoint(func):
    """Decorator to log endpoint calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        log.info(
            f"Endpoint called: {func.__name__}",
            args=str(args),
            kwargs=str(kwargs)
        )
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            log.info(
                f"Endpoint completed: {func.__name__}",
                duration_ms=duration * 1000
            )
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            log.error(
                f"Endpoint failed: {func.__name__}",
                duration_ms=duration * 1000,
                error=str(e)
            )
            raise
    
    return wrapper

@log_endpoint
def get_user_data(user_id):
    # Fetch user data
    return {"id": user_id, "name": "John"}
```

### Performance Monitoring

```python
from loglight import log
import time

class DatabaseConnection:
    def __init__(self):
        self.connection = None
    
    def query(self, sql, **params):
        start_time = time.time()
        
        log.debug("Executing query", sql=sql, params=params)
        
        try:
            # Execute query
            result = self.execute(sql, params)
            duration = time.time() - start_time
            
            log.info(
                "Query executed",
                sql=sql,
                duration_ms=duration * 1000,
                rows_affected=len(result)
            )
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            log.error(
                "Query failed",
                sql=sql,
                duration_ms=duration * 1000,
                error=str(e)
            )
            raise
    
    def execute(self, sql, params):
        # Actual execution logic
        return []
```

---

## Log Aggregation Example

```python
from loglight import log
from loglight.handlers import (
    ConsoleHandler,
    FileHandler,
    ElasticsearchHandler,
    SlackHandler
)

# Setup multiple handlers for different purposes
log.add_handler(ConsoleHandler())  # Development output

log.add_handler(FileHandler(  # All logs to file
    filepath="/var/log/app.log"
))

log.add_handler(ElasticsearchHandler(  # Central logging
    hosts="elasticsearch.example.com:9200",
    index="app-logs"
))

log.add_handler(SlackHandler(  # Alert on errors
    webhook_url="https://hooks.slack.com/...",
    min_level="ERROR"
))

# All logs go to all appropriate handlers
log.info("Application started")
log.error("Something went wrong")  # Also goes to Slack
```

---

## Testing with LogLight

```python
import pytest
from io import StringIO
from loglight import log
from loglight.handlers import ConsoleHandler

@pytest.fixture
def log_capture():
    """Capture logs during tests"""
    captured = StringIO()
    handler = ConsoleHandler(stream=captured)
    log.add_handler(handler)
    
    yield captured
    
    # Cleanup
    log.handlers.remove(handler)

def test_user_creation(log_capture):
    # Test code
    log.info("Creating user", user_id="test_123")
    
    # Verify log output
    output = log_capture.getvalue()
    assert "Creating user" in output
    assert "user_id" in output
```

---

## Configuration Examples

### Development

```python
from loglight import log
from loglight.config import Config
from loglight.handlers import ConsoleHandler

config = Config(
    service_name="myapp",
    env="development",
    log_level="DEBUG"
)
log.configure(config)
log.add_handler(ConsoleHandler())
```

### Production

```python
from loglight import log
from loglight.config import Config
from loglight.handlers import (
    RotatingFileHandler,
    ElasticsearchHandler,
    SlackHandler
)

config = Config(
    service_name="myapp",
    env="production",
    log_level="INFO"
)
log.configure(config)

log.add_handler(RotatingFileHandler(
    filepath="/var/log/myapp.log",
    max_bytes=100 * 1024 * 1024,
    backup_count=20
))

log.add_handler(ElasticsearchHandler(
    hosts="logs.example.com",
    index="myapp-logs"
))

log.add_handler(SlackHandler(
    webhook_url="https://hooks.slack.com/...",
    min_level="ERROR"
))
```

