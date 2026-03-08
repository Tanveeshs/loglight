# Contributing to LogLight

## Overview

We welcome contributions from the community! This guide will help you get started with contributing to LogLight.

## Getting Started

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:

```bash
git clone https://github.com/tanveeshs/loglight.git
cd loglight
```

### Set Up Development Environment

```bash
# Install in development mode with all optional dependencies
pip install -e ".[http,s3,kafka]"

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### Verify Installation

```bash
pytest
```

All tests should pass.

---

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use clear, descriptive branch names:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation
- `refactor/` for code refactoring

### Making Changes

1. Make your changes in the appropriate files
2. Write or update tests
3. Run tests to ensure everything works:

```bash
pytest
```

4. Format your code:

```bash
black loglight/ tests/
```

5. Run linting:

```bash
flake8 loglight/ tests/
```

6. Type checking (optional):

```bash
mypy loglight/
```

### Committing Changes

Write clear commit messages:

```bash
git commit -m "feat: add new handler for X"
git commit -m "fix: resolve issue with Y"
git commit -m "docs: update handler documentation"
```

### Pushing and Creating a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what was changed and why
- Reference to any related issues

---

## Code Style Guide

### Python Style

We follow PEP 8. Use `black` for formatting:

```bash
black loglight/ tests/
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `ConsoleHandler`)
- **Functions**: `snake_case` (e.g., `emit_log`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- **Private methods**: `_leading_underscore` (e.g., `_validate_config`)

### Documentation

All public classes and methods should have docstrings:

```python
class MyHandler(BaseHandler):
    """Handle log records and emit them somewhere.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Raises:
        ValueError: Description of when this is raised
    
    Example:
        >>> handler = MyHandler(param1="value")
        >>> handler.emit(log_record)
    """
    
    def emit(self, record):
        """Emit a log record.
        
        Args:
            record: JSON log record as a string
        """
        pass
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=loglight

# Run specific test file
pytest tests/test_logger.py

# Run specific test
pytest tests/test_logger.py::test_info_logging
```

### Writing Tests

Tests should be in the `tests/` directory with the same structure as the source code.

**Example test file** (`tests/handlers/test_custom_handler.py`):

```python
import pytest
from io import StringIO
from loglight.handlers import CustomHandler

def test_custom_handler_basic():
    """Test basic custom handler functionality"""
    handler = CustomHandler()
    
    handler.emit('{"message": "test"}')
    # Assert expected behavior

def test_custom_handler_with_config():
    """Test custom handler with configuration"""
    handler = CustomHandler(param="value")
    
    handler.emit('{"message": "test"}')
    # Assert expected behavior

@pytest.mark.parametrize("input,expected", [
    ('{"a": 1}', True),
    ('invalid', False),
])
def test_custom_handler_validation(input, expected):
    """Test handler input validation"""
    handler = CustomHandler()
    # Test various inputs
```

### Test Coverage

- Aim for > 80% code coverage
- Test both happy paths and error cases
- Use fixtures for common setup

---

## Adding a New Handler

### Step 1: Create the Handler File

Create a new file in `loglight/handlers/` following the naming convention:

```python
# loglight/handlers/MyHandler.py

from loglight.handlers import BaseHandler
import json

class MyHandler(BaseHandler):
    """Description of what this handler does."""
    
    def __init__(self, param1, param2=None):
        """Initialize the handler.
        
        Args:
            param1: Required parameter
            param2: Optional parameter
        """
        super().__init__()
        self.param1 = param1
        self.param2 = param2
    
    def emit(self, record):
        """Emit a log record.
        
        Args:
            record: JSON log record as a string
        """
        try:
            log_data = json.loads(record)
            # Process the log
            self._send_log(log_data)
        except Exception as e:
            self._handle_error(e)
    
    def _send_log(self, log_data):
        """Send the log somewhere."""
        pass
```

### Step 2: Add to `__init__.py`

```python
# loglight/handlers/__init__.py

from .MyHandler import MyHandler

__all__ = [
    'BaseHandler',
    'ConsoleHandler',
    'FileHandler',
    # ...
    'MyHandler',  # Add here
]
```

### Step 3: Write Tests

```python
# tests/handlers/test_my_handler.py

import pytest
from loglight.handlers import MyHandler

def test_my_handler_initialization():
    handler = MyHandler(param1="value")
    assert handler.param1 == "value"

def test_my_handler_emit():
    handler = MyHandler(param1="value")
    handler.emit('{"message": "test"}')
    # Assert behavior
```

### Step 4: Update Documentation

Add documentation to `docs/HANDLERS.md`:

```markdown
### MyHandler

Description of the handler.

**Parameters:**
- `param1` (required): Description
- `param2` (optional): Description

**Example:**
\`\`\`python
handler = MyHandler(param1="value")
log.add_handler(handler)
\`\`\`
```

---

## Reporting Bugs

### Before Submitting

- Check if the bug has already been reported
- Try to reproduce the issue with a minimal example
- Check the latest version to see if it's already fixed

### Bug Report Template

```markdown
**Description**
Brief description of the bug

**Reproduction Steps**
1. Step 1
2. Step 2
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Python version: 3.x
- LogLight version: 0.x.x
- Operating system: ...

**Additional Context**
Any other relevant information
```

---

## Suggesting Features

### Feature Request Template

```markdown
**Description**
Clear description of the feature

**Problem It Solves**
Explain the problem or use case

**Proposed Solution**
How you envision this working

**Alternatives Considered**
Other approaches you've thought of

**Additional Context**
Examples, mockups, or other information
```

---

## Documentation Contributions

### Updating Docs

- Documentation files are in the `docs/` directory
- Use clear, concise language
- Include code examples where helpful
- Update the main README if needed

### Building Docs Locally

```bash
# If we use Sphinx in the future:
cd docs
make html
```

---

## Pull Request Process

1. **Update the README** if you've changed user-facing functionality
2. **Update CHANGELOG** (if applicable)
3. **Ensure tests pass**: `pytest`
4. **Check code style**: `black` and `flake8`
5. **Update documentation** if needed
6. **Link related issues** in the PR description

### PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`black`)
- [ ] No linting errors (`flake8`)
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No unnecessary dependencies added

---

## Code Review Process

When your PR is reviewed:

1. A maintainer will review your code
2. They may request changes
3. Make requested changes in new commits
4. Mark conversations as resolved after addressing feedback
5. Your PR will be merged once approved

---

## Branching Model

We use a simplified Git flow:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature branches
- `fix/*`: Bug fix branches
- `docs/*`: Documentation branches

---

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes

Release checklist:
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Merge to `main`
4. Create GitHub release
5. Publish to PyPI

---

## Community Guidelines

- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on the code, not the person
- Help others learn and grow
- Follow the Code of Conduct (if applicable)

---

## Questions?

- Check existing GitHub issues
- Open a new GitHub discussion
- Contact maintainers directly

Thank you for contributing to LogLight! 🎉

