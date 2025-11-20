# Contributing to auto-uv

Thank you for considering contributing to auto-uv! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, uv version)
- Any error messages or logs

### Suggesting Enhancements

Enhancement suggestions are welcome! Please open an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Potential implementation approach (if you have ideas)

### Pull Requests

1. **Fork the repository** and create a new branch for your feature/fix
2. **Make your changes** with clear, descriptive commit messages
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description of changes

## Development Setup

### Prerequisites

- Python 3.8 or higher
- uv package manager
- Git

### Setting Up Your Development Environment

1. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/auto-uv.git
   cd auto-uv
   ```

2. **Install development dependencies:**
   ```bash
   pip install -e .
   pip install pytest ruff black mypy
   ```

3. **Install build tools:**
   ```bash
   pip install build hatch-autorun
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions focused and concise
- Add docstrings to all public functions and classes

### Running Tests

Run the test suite:

```bash
python tests/test_auto_uv.py
```

Or with pytest (if available):

```bash
pytest tests/
```

### Code Formatting

Format your code with black:

```bash
black src/ tests/
```

Lint with ruff:

```bash
ruff check src/ tests/
```

Type check with mypy:

```bash
mypy src/
```

### Testing Your Changes

1. **Test with the example script:**
   ```bash
   python example.py
   ```

2. **Test with AUTO_UV_DISABLE:**
   ```bash
   AUTO_UV_DISABLE=1 python example.py
   ```

3. **Test with different Python versions:**
   ```bash
   python3.8 example.py
   python3.9 example.py
   python3.10 example.py
   # etc.
   ```

4. **Test without uv installed** (simulate by temporarily removing uv from PATH)

## Project Structure

```
uv-run-python/
├── src/
│   └── auto_uv.py          # Main module
├── tests/
│   └── test_auto_uv.py     # Tests
├── example.py               # Example script
├── main.py                  # Demo script
├── pyproject.toml          # Project configuration
├── README.md               # User documentation
├── INSTALLATION.md         # Installation guide
├── CONTRIBUTING.md         # This file
└── LICENSE                 # MIT License
```

## Key Components

### `auto_uv.py`

The main module contains:
- `should_use_uv()`: Checks if uv should be used
- `auto_use_uv()`: Main entry point that intercepts execution

### Build System

Uses `hatch-autorun` to automatically run code when the package is imported:

```toml
[tool.hatch.build.targets.wheel.hooks.autorun]
dependencies = ["hatch-autorun"]
code = "__import__('auto_uv').auto_use_uv()"
```

## Common Tasks

### Building the Package

```bash
python -m build
```

This creates wheel and source distributions in `dist/`.

### Installing Locally

```bash
pip install -e .
```

### Testing Installation

```bash
python -c "import auto_uv; print('Success!')"
```

## What to Contribute

### Good First Issues

- Improve error messages
- Add more tests
- Improve documentation
- Add platform-specific tests

### Enhancement Ideas

- Support for poetry and other package managers
- Configuration file support
- Better logging/debugging options
- Performance optimizations
- Support for more edge cases

### Areas Needing Attention

- Windows-specific testing
- Integration with CI/CD pipelines
- Handling of various Python launch scenarios
- Performance impact measurement

## Questions?

If you have questions about contributing:
1. Check existing issues and discussions
2. Open a new issue with your question
3. Tag it as "question"

## Recognition

Contributors will be recognized in:
- The CONTRIBUTORS.md file (if created)
- Release notes
- Project documentation

Thank you for contributing to auto-uv! 🚀

