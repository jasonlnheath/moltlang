# Contributing to MoltLang

First off, thank you for considering contributing to MoltLang! It's people like you that make open-source projects thrive.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)

## Code of Conduct

This project and everyone participating in it is governed by our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**

```markdown
**Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. Windows 11, macOS 14, Ubuntu 22.04]
- Python Version: [e.g. 3.11]
- Project Version: [e.g. v0.1.0]

**Additional Context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most MoltLang users
- **List some examples** of how this feature would be used
- **Include mock-ups** if applicable

### Pull Requests

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Virtual environment (recommended)

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/moltlang.git
cd moltlang

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
```

## Pull Request Process

### 1. Ensure an issue exists for your change

If you'd like to work on an issue that doesn't exist yet, please open an issue for discussion first.

### 2. Set up your local repository

```bash
git remote add upstream https://github.com/moltlang/moltlang.git
git fetch upstream
```

### 3. Create a branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make your changes

- Write clean, documented code
- Add tests for new functionality
- Update documentation as needed
- Follow our coding standards

### 5. Commit your changes

```bash
git add .
git commit -m "feat: add amazing feature"
```

**Commit Message Format:**

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### 6. Push and create PR

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub.

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Coding Standards

### Python Code Style

We follow PEP 8 and use:
- **Ruff** for linting
- **Black** for formatting
- **isort** for import sorting
- **mypy** for type checking

```bash
# Format code
black .

# Sort imports
isort .

# Lint
ruff check .

# Type check
mypy src/
```

### Documentation

- All public functions must have docstrings
- Use Google style docstrings
- Include type hints
- Add examples for complex functions

```python
def translate_to_molt(text: str) -> str:
    """Translate English text to MoltLang.

    Args:
        text: The English text to translate.

    Returns:
        The MoltLang representation of the input text.

    Examples:
        >>> translate_to_molt("Fetch data from API")
        '[OP:FETCH][SRC:API]'
    """
    ...
```

### Testing

- Write tests for all new functionality
- Aim for >80% code coverage
- Use pytest for testing
- Mock external dependencies

```python
def test_translate_to_molt():
    """Test English to MoltLang translation."""
    result = translate_to_molt("Fetch data from API")
    assert result == "[OP:FETCH][SRC:API]"
```

## Adding New Tokens

The language specification is community-driven. To propose new tokens:

1. Open an issue with your proposal
2. Include: token name, semantic meaning, example usage
3. Get community feedback
4. Submit PR with implementation

## Questions?

Feel free to open an issue for any questions!

---

Again, thank you for contributing to MoltLang! 🚀
