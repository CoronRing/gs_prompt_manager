# Contributing to gs_prompt_manager

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/CoronRing/gs_prompt_manager.git
cd gs_prompt_manager
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

### 3. Install Development Dependencies

```bash
# Install package in editable mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Verify Installation

```bash
# Run tests to ensure everything works
pytest test/ -v
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/gs_prompt_manager

# Run specific test file
pytest test/test_prompt_base.py

# Run specific test
pytest test/test_prompt_base.py::TestPromptBase::test_basic_instantiation

# Run with verbose output
pytest -v
```

### Code Quality

Before committing, ensure code quality:

```bash
# Format code with Black
black src/ test/

# Sort imports with isort
isort src/ test/

# Check code style with flake8
flake8 src/ test/

# Type checking with mypy (if configured)
mypy src/
```

### Test Coverage

Maintain high test coverage:

```bash
# Generate coverage report
pytest --cov=src/gs_prompt_manager --cov-report=html

# Open coverage report
# Open htmlcov/index.html in your browser
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clear, readable code
- Follow existing code style
- Add docstrings to functions and classes
- Keep changes focused and atomic

### 3. Add Tests

- Write tests for new features
- Update tests for bug fixes
- Ensure all tests pass
- Maintain or improve code coverage

### 4. Update Documentation

- Update README.md if adding features
- Add docstrings to new code
- Update examples if needed

### 5. Commit Changes

Write clear commit messages:

```bash
git add .
git commit -m "feat: Add new feature"
# or
git commit -m "fix: Fix bug in PromptManager"
```

Commit message prefixes:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted (black, isort)
- [ ] No linting errors (flake8)
- [ ] Documentation is updated
- [ ] Commit messages are clear

### PR Description

Include in your PR:

1. **What**: What changes were made
2. **Why**: Why these changes are needed
3. **How**: How the changes work (if complex)
4. **Testing**: How you tested the changes

Example:

```markdown
## What

Added support for nested prompt templates

## Why

Users requested the ability to compose prompts from other prompts

## How

- Extended PromptBase with `associated_prompt` field
- Updated PromptManager to handle prompt dependencies
- Added recursive resolution of nested prompts

## Testing

- Added test_nested_prompts.py with 10 test cases
- All existing tests still pass
- Manual testing with sample use cases
```

## Code Style Guidelines

### Python Style

Follow PEP 8 and these guidelines:

```python
# Use clear, descriptive names
def get_prompt_by_name(name: str) -> PromptBase:
    """Get a prompt instance by its name."""
    pass

# Add type hints
def process_prompt(prompt: PromptBase, pieces: dict = None) -> str:
    """Process prompt with given pieces."""
    pass

# Use docstrings (Google style)
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
    """
    pass
```

### Test Style

```python
class TestFeatureName:
    """Test suite for feature."""

    def test_basic_functionality(self):
        """Test basic use case."""
        # Arrange
        prompt = SimplePrompt()

        # Act
        result = prompt.get_prompt_chat()

        # Assert
        assert result == "expected value"

    def test_error_handling(self):
        """Test error is raised correctly."""
        with pytest.raises(ValueError, match="error message"):
            invalid_operation()
```

## Project Structure

```
gs_prompt_manager/
├── src/
│   └── gs_prompt_manager/
│       ├── __init__.py
│       ├── prompt_base.py      # Base class for prompts
│       └── prompt_manager.py   # Prompt discovery and management
├── test/
│   ├── __init__.py
│   ├── conftest.py            # Shared fixtures
│   ├── test_prompt_base.py    # PromptBase tests
│   ├── test_prompt_manager.py # PromptManager tests
│   └── sample_prompts/        # Sample prompts for testing
├── .github/
│   └── workflows/
│       ├── tests.yml          # CI tests
│       └── publish-to-pypi.yml # PyPI publishing
├── pyproject.toml             # Package configuration
├── pytest.ini                 # Pytest configuration
├── requirements-dev.txt       # Dev dependencies
└── README.md                  # User documentation
```

## Adding New Features

### Example: Adding a New Method to PromptBase

1. **Add the method**:

```python
# In src/gs_prompt_manager/prompt_base.py
def new_feature(self, param: str) -> str:
    """
    Description of new feature.

    Args:
        param: Description

    Returns:
        Description of return value
    """
    # Implementation
    return result
```

2. **Add tests**:

```python
# In test/test_prompt_base.py
def test_new_feature(self):
    """Test new feature works correctly."""
    prompt = SimplePrompt()
    result = prompt.new_feature("test")
    assert result == "expected"
```

3. **Update documentation**:

````markdown
# In README.md

### New Feature

Description and example:
\```python
prompt.new_feature("example")
\```
````

## Reporting Issues

### Bug Reports

Include:

- Python version
- Package version
- Minimal code to reproduce
- Expected vs actual behavior
- Error messages/stack traces

### Feature Requests

Include:

- Use case description
- Proposed API (if applicable)
- Example usage
- Benefits to users

## Getting Help

- **Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Email**: Contact the maintainer for private inquiries

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
