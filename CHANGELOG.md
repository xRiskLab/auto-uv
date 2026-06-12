# v0.1.2 - Critical Bug Fixes and Comprehensive Edge Case Coverage

## Critical Fixes

### 1. **Site Initialization Crash (v0.1.1 bug)**
- **Problem**: `sys.exit()` during site initialization caused "Fatal Python error: init_import_site"
- **Solution**: 
  - Use `os.execve()` instead of `subprocess.run()` + `sys.exit()` to replace process
  - Check `__main__.__file__` to only intercept actual script execution, not imports
  - Normalize paths (absolute vs relative) before comparison
- **Impact**: Python no longer crashes on startup when auto-uv is installed

### 2. **Project Detection**
- **Problem**: When in a folder with `.venv`, running `python script.py` didn't use uv
- **Solution**: Walk up directory tree looking for project markers:
  - `pyproject.toml`
  - `.venv/` directory
  - `uv.lock` file
  - Searches up to 10 parent directories
- **Impact**: `python script.py` now automatically uses `uv run` in project directories

### 3. **Windows Support**
- **Problem**: Only looked for `uv` executable, not `uv.exe`
- **Solution**: Check for `uv.exe`, `uv.cmd`, `uv.bat` on Windows
- **Impact**: Works correctly on Windows systems

### 4. **System Directory Scripts**
- **Problem**: Didn't exclude scripts in `/usr/bin`, `/usr/local/bin`, etc.
- **Solution**: Added system directory exclusion list
- **Impact**: System scripts are no longer intercepted

### 5. **Path Boundary Checks**
- **Problem**: Path checks didn't catch scripts ending with `/bin` or `/Scripts`
- **Solution**: Added comprehensive path boundary checks
- **Impact**: Better detection of system vs user scripts

## Test Coverage

Added **3 critical regression tests**:

1. **`test_no_infinite_loop()`** - Prevents infinite re-execution
   - Verifies UV_RUN_ACTIVE prevents loops
   - Has 5-second timeout to catch runaway processes

2. **`test_no_interception_during_import()`** - Prevents import crashes
   - Verifies `__main__.__file__` check works
   - Ensures auto-uv doesn't intercept during site initialization

3. **`test_path_normalization()`** - Prevents path comparison bugs
   - Tests relative vs absolute path handling
   - Ensures correct interception decisions

**Total test suite: 9 tests, all passing** ✅

## What Works Now

```bash
# In a project directory with .venv or pyproject.toml:
python script.py          # ✅ Automatically uses uv run

# Installed packages work normally:
dbt debug                 # ✅ No interference
pytest                    # ✅ No interference
pip install pkg           # ✅ No interference

# Windows:
python script.py          # ✅ Finds uv.exe

# System scripts:
/usr/bin/python script.py # ✅ No interference
```

## Edge Cases Covered

✅ Empty sys.argv[0]  
✅ No `__main__.__file__` (frozen executables)  
✅ Relative vs absolute paths  
✅ Site-packages exclusion  
✅ dist-packages exclusion  
✅ bin/ directory exclusion  
✅ Scripts/ directory exclusion  
✅ sys.prefix exclusion  
✅ System directories (/usr/bin, etc.)  
✅ Project detection (pyproject.toml, .venv, uv.lock)  
✅ Parent directory search  
✅ UV_RUN_ACTIVE loop prevention  
✅ AUTO_UV_DISABLE flag  
✅ Import-time safety  

## Installation

```bash
pip install --upgrade auto-uv
```

## Breaking Changes

None - fully backward compatible with v0.1.1

## Contributors

Thanks to all who reported issues and helped test!

---

**Full Changelog**: https://github.com/xRiskLab/auto-uv/compare/v0.1.1...v0.1.2

