# LogLight Documentation Index

Welcome to the LogLight documentation! This is your starting point for exploring all available resources.

## 📚 Documentation Structure

### Getting Started
- **[Quick Start Guide](./QUICKSTART.md)** ⭐ *Start here!*
  - Installation basics
  - Your first log
  - Structured logging
  - Common setup patterns
  
- **[Installation Guide](./INSTALLATION.md)**
  - Detailed installation instructions
  - Optional dependencies
  - Development setup
  - Troubleshooting

### Core Concepts
- **[Configuration Guide](./CONFIGURATION.md)**
  - Environment and Python configuration
  - Log levels and global options
  - Complete configuration examples
  - Environment-based setup

- **[Handler Documentation](./HANDLERS.md)**
  - All 10+ handler types explained
  - Parameters and examples
  - Custom handler implementation
  - Performance considerations

### Integration & Usage
- **[Middleware Integration](./MIDDLEWARE.md)**
  - FastAPI, Flask, Django setup
  - Request tracking
  - Error handling
  - Best practices

- **[Examples](./EXAMPLES.md)**
  - Real-world application examples
  - Advanced patterns
  - Testing strategies
  - Production configurations

### Development
- **[Contributing Guide](./CONTRIBUTING.md)**
  - Development setup
  - Code style guidelines
  - Testing best practices
  - Adding new handlers
  - Pull request process

### Project Vision
- **[Roadmap](./ROADMAP.md)**
  - Short-term plans (v0.2)
  - Medium-term plans (v0.3-v0.4)
  - Long-term vision (v1.0+)
  - Community contribution

---

## 🎯 Quick Navigation by Use Case

### "I'm new to LogLight"
1. Read: [Quick Start Guide](./QUICKSTART.md)
2. Install: [Installation Guide](./INSTALLATION.md)
3. Explore: [Examples](./EXAMPLES.md)

### "I want to integrate with my framework"
1. [Middleware Integration](./MIDDLEWARE.md) - Choose your framework
2. [Examples](./EXAMPLES.md) - See real-world examples
3. [Configuration Guide](./CONFIGURATION.md) - Fine-tune your setup

### "I want to send logs somewhere specific"
1. [Handler Documentation](./HANDLERS.md) - Find the right handler
2. [Configuration Guide](./CONFIGURATION.md) - Configure the handler
3. [Examples](./EXAMPLES.md) - See it in action

### "I want to contribute to LogLight"
1. [Contributing Guide](./CONTRIBUTING.md) - Get started
2. [Roadmap](./ROADMAP.md) - See what's needed
3. [Examples](./EXAMPLES.md) - Understand the codebase

### "I want to understand the project direction"
1. [Roadmap](./ROADMAP.md) - View planned features
2. [Contributing Guide](./CONTRIBUTING.md) - How to help
3. [Examples](./EXAMPLES.md) - See current capabilities

---

## 📋 Handler Quick Reference

| Handler | Purpose | Best For |
|---------|---------|----------|
| ConsoleHandler | Print to stdout | Development, debugging |
| FileHandler | Write to file | Persistent logging |
| RotatingFileHandler | Rotate log files by size | Production, long-running apps |
| SlackHandler | Send to Slack | Alert on errors |
| WebhookHandler | HTTP webhook | Custom integrations |
| HTTPHandler | HTTP endpoint | API-based log services |
| S3Handler | AWS S3 storage | Cloud-based archival |
| KafkaHandler | Apache Kafka | Event streaming |
| ElasticsearchHandler | Elasticsearch | Centralized log analysis |
| SyslogHandler | System logging | Unix/Linux syslog |

---

## 🚀 Key Features Explained

### Structured Logging
```python
log.info("User created", user_id="123", email="user@example.com")
```

### Multiple Handlers
```python
log.add_handler(ConsoleHandler())
log.add_handler(FileHandler("/var/log/app.log"))
log.add_handler(SlackHandler(...))
```

### Request Tracing
Automatically tracked across your application with middleware.

### Framework Integration
```python
app.add_middleware(LogLightMiddleware)
```

---

## 📖 Quick Document Descriptions

| Document | Best For | Length |
|----------|----------|--------|
| [QUICKSTART.md](./QUICKSTART.md) | Getting started | ~5 min read |
| [INSTALLATION.md](./INSTALLATION.md) | Setting up | ~10 min read |
| [CONFIGURATION.md](./CONFIGURATION.md) | Configuring | ~20 min read |
| [HANDLERS.md](./HANDLERS.md) | Handler reference | ~30 min read |
| [MIDDLEWARE.md](./MIDDLEWARE.md) | Framework integration | ~25 min read |
| [EXAMPLES.md](./EXAMPLES.md) | Real-world usage | ~35 min read |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contributing code | ~30 min read |
| [ROADMAP.md](./ROADMAP.md) | Project vision | ~15 min read |

---

## ❓ Common Questions

**Q: Where do I start?**
A: [Quick Start Guide](./QUICKSTART.md)

**Q: How do I install?**
A: [Installation Guide](./INSTALLATION.md)

**Q: FastAPI/Flask/Django setup?**
A: [Middleware Integration](./MIDDLEWARE.md)

**Q: What handlers available?**
A: [Handler Documentation](./HANDLERS.md)

**Q: Can I contribute?**
A: [Contributing Guide](./CONTRIBUTING.md)

**Q: What's planned next?**
A: [Roadmap](./ROADMAP.md)

---

## 🎉 Ready to Get Started?

**[→ Start with Quick Start Guide](./QUICKSTART.md)**

