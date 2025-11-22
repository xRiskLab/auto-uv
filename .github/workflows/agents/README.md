# GitHub Copilot Agents for auto-uv

This directory contains specialized AI agents for working with the auto-uv Python package. Each agent has a specific role and expertise.

## Available Agents

### 📝 [@docs-agent](./docs-agent.md)
**Expert technical writer for auto-uv**

- **What it does:** Maintains README.md, creates changelogs, documents features
- **Commands:** `make pre-commit`, markdown linting
- **Boundaries:** Updates documentation, never modifies source code
- **Use when:** Adding features, fixing bugs, updating documentation

### 🧪 [@test-agent](./test-agent.md)
**QA engineer specializing in Python testing**

- **What it does:** Writes pytest tests, covers edge cases, prevents regressions
- **Commands:** `make test`, `AUTO_UV_DISABLE=1 uv run pytest tests/ -v`
- **Boundaries:** Writes to `tests/`, never removes failing tests without approval
- **Use when:** Adding features, fixing bugs, improving test coverage

### 🎨 [@lint-agent](./lint-agent.md)
**Code quality specialist for Python**

- **What it does:** Fixes formatting, enforces style, runs linters
- **Commands:** `make lint`, `make format`, `make pre-commit`
- **Boundaries:** Fixes style only, never changes code logic
- **Use when:** Cleaning up code, fixing linter errors, formatting

### 🚀 [@release-agent](./release-agent.md)
**Release manager for versioning and publishing**

- **What it does:** Manages versions, creates changelogs, handles PyPI releases
- **Commands:** `git tag`, `gh release create`, `uv build`
- **Boundaries:** Manages releases, asks before major changes
- **Use when:** Preparing releases, bumping versions, publishing to PyPI

## How to Use Agents

### In GitHub Copilot Chat

Simply mention the agent in your chat:

```
@docs-agent Update README.md with the new project detection feature

@test-agent Write a test for Windows uv.exe detection

@lint-agent Fix all formatting issues in src/auto_uv.py

@release-agent Prepare a patch release for the bug fix
```

### Agent Workflow Examples

**Adding a new feature:**
1. Write the code
2. `@test-agent` - Write tests for the feature
3. `@docs-agent` - Document the feature in README.md
4. `@lint-agent` - Clean up code style
5. `@release-agent` - Prepare release notes

**Fixing a bug:**
1. Fix the bug
2. `@test-agent` - Add regression test
3. `@docs-agent` - Update troubleshooting section
4. `@release-agent` - Create patch release

**Improving code quality:**
1. `@lint-agent` - Fix all linting issues
2. `@test-agent` - Improve test coverage
3. `@docs-agent` - Update code examples

## Agent Capabilities

### What Agents Know

All agents understand:
- Python 3.9+ and modern Python practices
- The auto-uv codebase structure
- uv package manager
- pytest testing framework
- GitHub Actions workflows
- Semantic versioning

### What Agents Can Do

- ✅ Read code from `src/` and `tests/`
- ✅ Write/modify documentation and tests
- ✅ Run commands (make, uv, pytest, git)
- ✅ Suggest improvements and best practices
- ✅ Explain code and decisions

### What Agents Won't Do

- 🚫 Modify code without explicit request
- 🚫 Remove failing tests to make CI pass
- 🚫 Commit secrets or API tokens
- 🚫 Force-push or destructive git operations
- 🚫 Publish releases without verification

## Agent Boundaries

Each agent has clear boundaries defined in their respective `.md` files:

- **Always do** - Safe operations the agent performs automatically
- **Ask first** - Operations requiring user approval
- **Never do** - Forbidden operations

## Project Context

**auto-uv** is a Python package that automatically intercepts `python script.py` and runs it with `uv run` for seamless dependency management.

**Key features:**
- Automatic project detection (pyproject.toml, .venv, uv.lock)
- Smart filtering (excludes installed packages, system scripts)
- Cross-platform support (Unix and Windows)
- Zero configuration required

**Current version:** 0.1.2 (check `pyproject.toml` for latest)

## Quick Commands

```bash
# Testing
make test                  # Run all tests
make act-test             # Test CI locally

# Code quality
make lint                 # Run linters
make format               # Auto-format code
make pre-commit           # Run pre-commit hooks

# Development
make dev                  # Setup dev environment
make commit               # Format, lint, test

# Building
make build                # Build package
make clean                # Clean artifacts

# Releasing
git tag v0.1.2            # Create version tag
gh release create v0.1.2  # Create GitHub release
```

## Contributing to Agents

To improve or add agents:

1. **Understand the pattern:** Each agent has YAML frontmatter, persona, knowledge, commands, and boundaries
2. **Keep it specific:** Agents work best with focused roles
3. **Document commands:** Include exact commands the agent can run
4. **Define boundaries:** Be explicit about what the agent can and cannot do
5. **Test the agent:** Use it in Copilot Chat to verify it works as expected

## Useful Agent Combinations

**Full feature workflow:**
```
@test-agent Write comprehensive tests for the new feature
@lint-agent Fix all style issues
@docs-agent Document the feature in README.md
@release-agent Prepare a minor version release
```

**Bug fix workflow:**
```
@test-agent Add a regression test for this bug
@lint-agent Clean up the fix
@docs-agent Update troubleshooting section
@release-agent Prepare a patch release
```

**Code quality sprint:**
```
@lint-agent Fix all linting errors
@test-agent Improve test coverage to 95%
@docs-agent Add more code examples
```

## Learn More

- [GitHub Copilot Agents Documentation](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-agents)
- [auto-uv README](../../../README.md)
- [Contributing Guidelines](../../../CONTRIBUTING.md)

## Questions?

If an agent doesn't behave as expected:
1. Check the agent's `.md` file for its capabilities
2. Be specific in your request
3. Mention the agent explicitly with `@agent-name`
4. Provide context about what you're trying to achieve

