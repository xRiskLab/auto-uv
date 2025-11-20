# auto-uv

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Automatically use `uv run` when executing Python scripts. Just type `python script.py` instead of `uv run script.py`!

## What is This?

`auto-uv` is a Python package that intercepts script execution and automatically uses [uv](https://github.com/astral-sh/uv) to run them. Install it once, then forget about it - your scripts just work with proper dependency management.

## Installation

```bash
pip install auto-uv
```

That's it! Now when you run `python script.py`, it automatically uses `uv run` behind the scenes.

## Quick Start

```bash
# Install
pip install auto-uv

# Run any script - auto-uv handles the rest
python your_script.py

# Disable temporarily if needed
AUTO_UV_DISABLE=1 python your_script.py
```

## How It Works

When you install `auto-uv`, it uses the `hatch-autorun` plugin to automatically run code when Python starts. This code checks if:

1. You're running a script file (not interactive mode)
2. `uv` is available on your system
3. You're not already running under `uv run`

If all conditions are met, it re-executes your script with `uv run`, giving you automatic dependency management.

## Requirements

- Python 3.9+
- `uv` installed and in your PATH

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or
pip install uv
```

## Configuration

### Environment Variables

- `AUTO_UV_DISABLE`: Set to `1`, `true`, or `yes` to disable auto-uv
- `UV_RUN_ACTIVE`: Automatically set by auto-uv (don't set manually)

### Disabling auto-uv

```bash
# Temporarily disable
AUTO_UV_DISABLE=1 python script.py

# Permanently disable (add to your shell profile)
export AUTO_UV_DISABLE=1
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/xRiskLab/auto-uv.git
cd auto-uv

# Install with all dev dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Or use the Makefile
make dev
```

### Testing

```bash
# Run tests
make test

# Run tests with act (local GitHub Actions)
make act-test

# Format and lint
make format lint

# Full CI pipeline locally
make ci
```

### Available Make Targets

```bash
make help              # Show all available commands
make dev               # Setup development environment
make test              # Run tests
make lint              # Run linters
make format            # Format code
make build             # Build package with uv
make publish-test      # Publish to Test PyPI
make publish           # Publish to PyPI
make clean             # Clean build artifacts
make act-test          # Test with act (local GitHub Actions)
make pre-commit        # Run pre-commit hooks
make commit            # Format, lint, and test before commit
```

### Publishing Manually

```bash
# 1. Get token from https://pypi.org/manage/account/token/

# 2. Add to .env file (already in .gitignore)
echo "UV_PUBLISH_TOKEN=pypi-AgE..." >> .env

# 3. Build and publish (Makefile auto-loads .env)
make publish-test

# 4. If successful, publish to PyPI
make publish
```

## Testing with Act

Test GitHub Actions workflows locally before pushing:

```bash
# Install act
brew install act  # macOS
# or see: https://github.com/nektos/act

# Optional: Create .env file for secrets (if needed)
echo "GITHUB_TOKEN=your_token_here" > .env

# Test workflows
make act-test           # Quick test
make act-lint           # Test linting
make act-all            # Test everything
```

## Version Management

Bump version using GitHub Actions:

```bash
gh workflow run version-bump.yml -f version_type=patch  # 0.1.0 -> 0.1.1
gh workflow run version-bump.yml -f version_type=minor  # 0.1.0 -> 0.2.0
gh workflow run version-bump.yml -f version_type=major  # 0.1.0 -> 1.0.0
```

Or use the Makefile:

```bash
make version-patch  # Bump patch version
make version-minor  # Bump minor version
make version-major  # Bump major version
```

## CI/CD

The project includes three GitHub Actions workflows:

1. **test.yml** - Run tests on multiple Python versions (3.9-3.12) and OS (Ubuntu, macOS, Windows)
2. **workflow.yml** - Build and publish to PyPI on release (required name for PyPI)
3. **version-bump.yml** - Automated version management

## Troubleshooting

### Installing packages in a uv project

Use `uv add` to manage dependencies:

```bash
# Add runtime dependency
uv add requests

# Add development dependency
uv add --dev pytest

# Add multiple packages
uv add --dev mypy black ruff
```

### Can't install packages

If auto-uv is interfering:

```bash
# Option 1: Disable auto-uv temporarily
AUTO_UV_DISABLE=1 pip install package-name

# Option 2: Uninstall auto-uv if not needed
pip uninstall auto-uv
```

### Auto-uv not working

```bash
# Check if uv is installed
uv --version

# Check if auto-uv is installed
python -c "import auto_uv; print('Installed')"

# Test manually
python -c "import os; print('UV_RUN_ACTIVE:', os.environ.get('UV_RUN_ACTIVE'))"
```

## Contributing

Contributions welcome! Here's the quick workflow:

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/auto-uv.git
cd auto-uv

# 2. Setup
make dev

# 3. Create branch
git checkout -b feature/your-feature

# 4. Make changes and test
make commit

# 5. Test with act
make act-test

# 6. Push and create PR
git push origin feature/your-feature
gh pr create
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Why auto-uv?

### Without auto-uv:
```bash
uv run script.py  # Have to remember uv run every time
```

### With auto-uv:
```bash
python script.py  # Just works!
```

Benefits:
- ✅ Seamless workflow
- ✅ Automatic dependency management via uv
- ✅ Zero configuration
- ✅ Easy to disable when needed
- ✅ Safe fallback if uv not available

## Inspiration

Inspired by [pyauto-dotenv](https://github.com/hmiladhia/auto-dotenv) which automatically loads `.env` files.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **Repository**: https://github.com/xRiskLab/auto-uv
- **Issues**: https://github.com/xRiskLab/auto-uv/issues
- **uv**: https://github.com/astral-sh/uv
- **hatch-autorun**: https://github.com/pypa/hatch
