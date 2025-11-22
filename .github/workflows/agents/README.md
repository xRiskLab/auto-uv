# GitHub Copilot Agents

Specialized AI agents for Python package development.

## Available Agents

### 📝 @docs-agent
Technical writer for documentation
- Updates README.md and changelogs
- Documents features and troubleshooting
- Never modifies source code

### 🧪 @test-agent  
QA engineer for pytest testing
- Writes comprehensive tests
- Follows Arrange-Act-Assert pattern
- Never removes failing tests

### 🎨 @lint-agent
Code quality specialist
- Fixes formatting and style
- Enforces PEP 8
- Never changes code logic

### 🚀 @release-agent
Release manager
- Manages semantic versioning
- Creates changelogs and releases
- Ensures tests pass before release

## How to Use

In GitHub Copilot Chat (not terminal):

```
@docs-agent Add a FAQ section to README.md

@test-agent Write a test for the normalize_path function

@lint-agent Fix all formatting issues in src/

@release-agent What version should we bump to for this bug fix?
```

## Quick Workflows

**Adding a feature:**
1. Write the code
2. `@test-agent` Write tests
3. `@docs-agent` Document it
4. `@lint-agent` Clean up style
5. `@release-agent` Prepare release

**Fixing a bug:**
1. Fix the bug
2. `@test-agent` Add regression test
3. `@release-agent` Create patch release

## Commands

```bash
make test          # Run tests
make lint          # Check style
make format        # Fix formatting
make pre-commit    # Run all checks
make build         # Build package
```

## Agent Boundaries

All agents have clear limits:
- ✅ **Do** - Safe operations in their domain
- ⚠️ **Ask first** - Operations needing approval
- 🚫 **Never** - Forbidden operations

## Testing Agents

Use `AGENT_TEST.md` for safe, non-critical testing:

```
@docs-agent Add a FAQ section to AGENT_TEST.md
```

This won't affect production code.

## Learn More

- [GitHub Copilot Agents Docs](https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-agents)
- Individual agent files for detailed capabilities
