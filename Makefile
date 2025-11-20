# Makefile for auto-uv development

.PHONY: help install dev-install test lint format clean build publish act-test pre-commit

# Load .env file if it exists
-include .env
export

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package (for testing after build)
	uv pip install dist/*.whl

dev-install: ## Install package with development dependencies
	@echo "Installing auto-uv with dev dependencies..."
	uv pip install -e ".[dev]"
	pre-commit install
	@echo "✅ Development environment ready!"

test: ## Run tests
	python tests/test_auto_uv.py
	python example.py

test-pytest: ## Run tests with pytest
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=term --cov-report=html

lint: ## Run linters
	ruff check src/ tests/ example.py
	mypy src/
	bandit -r src/

format: ## Format code
	black src/ tests/ example.py
	isort src/ tests/ example.py

format-check: ## Check formatting without fixing
	black --check src/ tests/ example.py
	isort --check-only src/ tests/ example.py

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean ## Build package
	uv build

build-check: build ## Build and check distribution
	uv build --check

publish-test: build ## Publish to Test PyPI (reads UV_PUBLISH_TOKEN from .env)
	@if [ -z "$$UV_PUBLISH_TOKEN" ]; then \
		echo "❌ UV_PUBLISH_TOKEN not set. Add to .env file"; \
		exit 1; \
	fi
	@echo "📦 Publishing to Test PyPI..."
	uv publish --publish-url https://test.pypi.org/legacy/

publish: build ## Publish to PyPI (reads UV_PUBLISH_TOKEN from .env)
	@if [ -z "$$UV_PUBLISH_TOKEN" ]; then \
		echo "❌ UV_PUBLISH_TOKEN not set. Add to .env file"; \
		exit 1; \
	fi
	@echo "📦 Publishing to PyPI..."
	uv publish

act-test: ## Test workflows with act (test job only)
	act -j test --matrix os:ubuntu-latest --matrix python-version:3.11

act-lint: ## Test lint workflow with act
	act -j lint

act-all: ## Test all workflows with act
	act push

act-list: ## List all act jobs
	act -l

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	pre-commit autoupdate

version-patch: ## Bump patch version (0.1.0 -> 0.1.1)
	@echo "Bumping patch version..."
	@CURRENT=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	echo "Current version: $$CURRENT"; \
	read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		pip install bump2version; \
		bump2version patch; \
	fi

version-minor: ## Bump minor version (0.1.0 -> 0.2.0)
	@echo "Bumping minor version..."
	@CURRENT=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	echo "Current version: $$CURRENT"; \
	read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		pip install bump2version; \
		bump2version minor; \
	fi

version-major: ## Bump major version (0.1.0 -> 1.0.0)
	@echo "Bumping major version..."
	@CURRENT=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	echo "Current version: $$CURRENT"; \
	read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		pip install bump2version; \
		bump2version major; \
	fi

check: lint format-check test ## Run all checks (lint, format, test)

ci: clean pre-commit lint test build-check ## Run full CI pipeline locally

quick-test: format lint ## Quick format and lint (pre-commit)
	@echo "✅ Quick checks passed!"

full-test: ci act-test ## Full local test including act
	@echo "✅ All tests passed!"

# Development workflow shortcuts
dev: dev-install pre-commit ## Setup complete dev environment
	@echo "✅ Development environment ready!"

commit: format lint test ## Format, lint, test before commit
	@echo "✅ Ready to commit!"
	@echo "Run: git add . && git commit -m 'Your message'"

release: clean build build-check ## Prepare release
	@echo "✅ Release artifacts ready in dist/"
	@echo "Next steps:"
	@echo "  1. Test: pip install dist/*.whl"
	@echo "  2. Push: git push origin main --tags"
	@echo "  3. Publish: make publish-test OR make publish"

