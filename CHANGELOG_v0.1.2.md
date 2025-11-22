# v0.1.2 - Comprehensive Edge Case Fixes

## Critical Fixes

### 1. **Site Initialization Crash (v0.1.1 bug)**
- **Problem**: `sys.exit()` during site initialization caused "Fatal Python error: init_import_site"
- **Solution**: 
  - Use `os.execve()` instead of `subprocess.run()` + `sys.exit()`
  - Check `__main__.__file__` to only intercept actual script execution, not imports
  - Normalize paths (absolute vs relative) before comparison

### 2. **Project Detection**
- **Problem**: When in a folder with `.venv`, running `python script.py` didn't use uv
- **Solution**: Walk up directory tree looking for project markers:
  - `pyproject.toml`
  - `.venv/` directory
  - `uv.lock` file
  - Searches up to 10 parent directories

### 3. **Windows Support**
- **Problem**: Only looked for `uv` executable, not `uv.exe`
- **Solution**: Check for `uv.exe`, `uv.cmd`, `uv.bat` on Windows

### 4. **System Directory Scripts**
- **Problem**: Didn't exclude scripts in `/usr/bin`, `/usr/local/bin`, etc.
- **Solution**: Added system directory exclusion list:
  - `/usr/bin`, `/usr/local/bin`, `/opt/bin`
  - `/bin`, `/sbin`, `/usr/sbin`, `/usr/local/sbin`

### 5. **Path Boundary Checks**
- **Problem**: `os.path.sep + "bin" + os.path.sep` didn't catch paths ending with `/bin`
- **Solution**: Added checks for:
  - Paths ending with `/bin` or `/Scripts`
  - Paths starting with `/bin/` or `/Scripts/`

## New Tests

### Regression Tests
1. **`test_installed_package_not_intercepted()`** - Catches v0.1.0 bug
   - Verifies scripts in `site-packages` are NOT intercepted
   - Prevents `dbt debug` crashes

2. **`test_no_site_initialization_crash()`** - Catches v0.1.1 bug
   - Verifies no "Fatal Python error" during site initialization
   - Ensures Python doesn't crash on startup

3. **`test_project_detection()`** - New feature test
   - Tests detection of `pyproject.toml`, `.venv`, `uv.lock`
   - Tests parent directory search
   - Tests non-project directories return False

## Edge Cases Now Covered

✅ Interactive Python (`python -c "code"`)
✅ Python REPL (`python`)
✅ Stdin execution (`python < script.py`)
✅ Python -m module (`python -m pytest`)
✅ Symlinks to scripts
✅ Relative vs absolute paths
✅ Scripts in .venv but not in bin/Scripts
✅ Windows uv.exe
✅ Frozen executables (PyInstaller)
✅ Debuggers (pdb, ipdb)
✅ Test runners (pytest, nose)
✅ Jupyter/IPython
✅ User home bin (~/.local/bin/)
✅ System directories (/usr/bin, etc.)
✅ Empty script paths
✅ Race conditions (script deleted)
✅ Permission denied on uv
✅ Multiple uv executables in PATH
✅ Path comparison with relative vs absolute
✅ Scripts ending with /bin or /Scripts
✅ Project detection (pyproject.toml, .venv, uv.lock)

## What This Means

Now `auto-uv` is **production-ready** and handles:

1. ✅ `python script.py` in a project directory → uses `uv run`
2. ✅ `dbt debug` → runs normally without interference
3. ✅ `pytest` → runs normally without interference
4. ✅ `pip install pkg` → runs normally without interference
5. ✅ Works on Windows with `uv.exe`
6. ✅ Doesn't crash Python during startup
7. ✅ Detects projects by walking up directory tree
8. ✅ Excludes system scripts in `/usr/bin`, etc.

## Installation

```bash
pip install --upgrade auto-uv
```

## For LLMs and Automation

The key feature: **When in a project directory with `.venv` or `pyproject.toml`, just run `python script.py`** and auto-uv will automatically use the project's environment via `uv run`.

No need to:
- Activate virtual environments
- Remember to use `uv run`
- Manually manage Python paths

Just `cd` into your project and run `python script.py` - it works! 🎯

