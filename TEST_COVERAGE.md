# Test Coverage for auto-uv

## Test Suite Summary

**Total Tests:** 9  
**Status:** ✅ All passing  

## Critical Bug Prevention Tests

### 1. ✅ **test_no_infinite_loop()**
**What it tests:** UV_RUN_ACTIVE prevents infinite re-execution  
**Why critical:** Without this, auto-uv would re-execute itself forever  
**How it works:**
- Creates a script that counts executions
- Verifies execution count stays low (no loop)
- Has 5-second timeout to catch runaway loops

**Prevents:**
```python
# BAD: Without UV_RUN_ACTIVE check
python script.py
  → uv run script.py
    → uv run uv run script.py
      → uv run uv run uv run script.py
        → ∞ INFINITE LOOP
```

### 2. ✅ **test_no_site_initialization_crash()**
**What it tests:** No sys.exit() during site initialization  
**Why critical:** sys.exit() during import crashes Python  
**Regression:** v0.1.1 bug - "Fatal Python error: init_import_site"

**Prevents:**
```python
# BAD: v0.1.1 code
def auto_use_uv():
    result = subprocess.run(["uv", "run"] + sys.argv)
    sys.exit(result.returncode)  # ← CRASHES during import!
```

**Fixed in v0.1.2:**
```python
# GOOD: v0.1.2 code
def auto_use_uv():
    if __main__.__file__ != sys.argv[0]:  # ← Check if we're in main
        return  # Don't intercept during import
    os.execve(uv_path, cmd, os.environ)  # ← Replace process, don't exit
```

### 3. ✅ **test_no_interception_during_import()**
**What it tests:** __main__.__file__ check prevents import interception  
**Why critical:** Intercepting during import causes crashes  
**How it works:**
- Imports auto_uv module
- Verifies no interception happens
- Checks import completes successfully

**Prevents:**
```python
# BAD: Intercepting during import
import auto_uv  # ← This should NOT trigger re-execution
```

### 4. ✅ **test_installed_package_not_intercepted()**
**What it tests:** Scripts in site-packages are NOT intercepted  
**Why critical:** Intercepting dbt, pip, pytest causes crashes  
**Regression:** v0.1.0 bug - dbt debug crashed

**Prevents:**
```bash
# BAD: v0.1.0 behavior
$ dbt debug
Fatal Python error: init_import_site: Failed to import the site module
```

### 5. ✅ **test_path_normalization()**
**What it tests:** Relative vs absolute path comparison works  
**Why critical:** Prevents incorrect interception decisions  
**How it works:**
- Tests with relative path (./script.py)
- Tests with absolute path (/full/path/script.py)
- Verifies both are normalized before comparison

**Prevents:**
```python
# BAD: Without normalization
__main__.__file__ = "script.py"  # relative
sys.argv[0] = "/full/path/script.py"  # absolute
# These don't match! → Incorrect interception
```

## Feature Tests

### 6. ✅ **test_project_detection()**
**What it tests:** Detects pyproject.toml, .venv, uv.lock  
**Coverage:**
- Directory with pyproject.toml
- Directory with .venv
- Directory with uv.lock
- Directory with no markers (should return False)
- Subdirectory of project (walks up tree)

### 7. ✅ **test_should_use_uv()**
**What it tests:** Decision logic for when to intercept  
**Coverage:**
- UV_RUN_ACTIVE=1 → don't intercept
- AUTO_UV_DISABLE=1 → don't intercept
- uv available → intercept
- uv not available → don't intercept

### 8. ✅ **test_script_execution()**
**What it tests:** Basic script execution works  
**Coverage:**
- Script runs successfully
- Returns correct exit code
- Output is captured correctly

### 9. ✅ **test_disable_flag()**
**What it tests:** AUTO_UV_DISABLE=1 works  
**Coverage:**
- Script runs without UV_RUN_ACTIVE when disabled
- Environment variable is respected

## Edge Cases Covered

✅ Empty sys.argv[0]  
✅ No __main__.__file__ (frozen executables)  
✅ Relative vs absolute paths  
✅ Site-packages exclusion  
✅ dist-packages exclusion  
✅ bin/ directory exclusion  
✅ Scripts/ directory exclusion  
✅ sys.prefix exclusion  
✅ sys.base_prefix exclusion  
✅ System directories (/usr/bin, etc.)  
✅ Project detection (pyproject.toml, .venv, uv.lock)  
✅ Parent directory search (up to 10 levels)  
✅ UV_RUN_ACTIVE loop prevention  
✅ AUTO_UV_DISABLE flag  
✅ Import-time safety  

## What's NOT Tested Yet

⚠️ **Windows-specific paths:**
- Scripts\ vs Scripts/ separator
- uv.exe vs uv.cmd vs uv.bat detection
- Windows system directories (C:\Windows\System32)

⚠️ **Symlink handling:**
- Symlinks to scripts
- Symlinks in project detection

⚠️ **Permission errors:**
- uv executable not executable
- Script file not readable

⚠️ **Race conditions:**
- Script deleted between check and exec
- Project markers changed during execution

⚠️ **Python -m module execution:**
- python -m pytest
- python -m pip
- User modules vs installed modules

## Running Tests

```bash
# Run all tests
make test

# Run with verbose output
AUTO_UV_DISABLE=1 PYTHONPATH=src uv run pytest tests/ -v

# Run specific test
AUTO_UV_DISABLE=1 PYTHONPATH=src uv run pytest tests/test_auto_uv.py::test_no_infinite_loop -v

# Run with coverage
AUTO_UV_DISABLE=1 uv run pytest tests/ --cov=auto_uv --cov-report=term-missing
```

## Test Philosophy

1. **Regression tests** - Every bug gets a test
2. **Edge case coverage** - Test boundary conditions
3. **Integration tests** - Test end-to-end behavior
4. **Unit tests** - Test individual functions
5. **Safety first** - Test that we don't break things

## Adding New Tests

When adding a test:
1. **Name it descriptively:** `test_<feature>_<scenario>`
2. **Add docstring:** Explain what and why
3. **Use Arrange-Act-Assert:** Clear structure
4. **Clean up:** Use context managers
5. **Add to __main__:** Include in manual test runner

