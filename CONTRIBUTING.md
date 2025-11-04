# Contributing to FastAPI CQRS Observability

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/fastapi-cqrs-observability.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `make test`
6. Commit your changes: `git commit -m "Add: your feature description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## 📝 Code Style

This project follows Python best practices:

- **Formatting**: Use `black` for code formatting
- **Import sorting**: Use `isort` for organizing imports
- **Type hints**: Add type hints to all functions
- **Docstrings**: Document all public functions and classes

Run before committing:
```bash
black app/ tests/
isort app/ tests/
mypy app/
```

## 🧪 Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Maintain or improve code coverage
- Include both unit and integration tests when applicable

```bash
pytest tests/ -v --cov=app
```

## 📋 Commit Messages

Use clear, descriptive commit messages following this format:

```
Type: Brief description

Detailed explanation (if needed)
```

Types:
- `Add:` New feature
- `Fix:` Bug fix
- `Update:` Changes to existing functionality
- `Refactor:` Code refactoring
- `Docs:` Documentation changes
- `Test:` Test additions or changes

Examples:
- `Add: idempotency middleware for signup endpoint`
- `Fix: duplicate user creation race condition`
- `Update: improve error handling in user repository`

## 🔍 Pull Request Process

1. Update the README.md with details of changes if applicable
2. Ensure all tests pass
3. Update documentation for any API changes
4. The PR will be merged once approved by maintainers

## 🐛 Reporting Bugs

When reporting bugs, please include:

- Python version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages or logs
- Environment details (OS, Docker version, etc.)

## 💡 Suggesting Features

Feature suggestions are welcome! Please:

- Check if the feature has already been requested
- Provide a clear use case
- Explain how it aligns with the project goals
- Consider implementation complexity

## 📚 Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples
- Improve code comments
- Translate documentation

## ❓ Questions

If you have questions:

- Check existing issues and discussions
- Review the README and documentation
- Open a new issue with the "question" label

## 🙏 Thank You

Your contributions make this project better for everyone!
