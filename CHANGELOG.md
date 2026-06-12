# v0.2.0 - Autorun hook actually fires again

## Critical Fix

### Installed `.pth` hook was a silent no-op (v0.1.2 regression)
- **Problem**: The v0.1.1 fix guarded interception with `__main__.__file__ ==
  sys.argv[0]`. But the hatch-autorun `.pth` runs during *site initialization*,
  where `__main__.__file__` is still `None` — so the guard always returned early
  and `python script.py` was **never** redirected to `uv run` when installed
  normally. Interception only happened via an explicit in-script call.
- **Solution**: Key the decision off `sys.argv[0]` (reliably set at site-init):
  intercept only when `argv[0]` is an existing user `.py` file — naturally
  skipping the REPL (`''`), `python -c` (`-c`), and `python -m` (`-m`). All
  prior guards (site-packages / venv `bin` / `sys.prefix` / system dirs /
  `UV_RUN_ACTIVE` / `AUTO_UV_DISABLE`) are preserved. The whole hook body is
  wrapped so it can never raise into interpreter startup.
- **Refactor**: Interception logic extracted into a pure, injectable
  `_should_intercept(argv, cwd, environ)` for direct unit testing.
- **Impact**: `python script.py` inside a uv project is redirected to `uv run`
  again. ⚠️ This restores active interception — set `AUTO_UV_DISABLE=1` to opt
  out.

## Tests
- Added `test_should_intercept_matrix`: hermetic unit coverage of every
  invocation shape (script, REPL, `-c`, `-m`, missing file, installed/system
  script, env opt-outs, no-uv, no-project).
- Added `test_installed_pth_actually_redirects`: integration test that builds
  the wheel, installs it (with the `.pth`) into an isolated venv, and asserts
  the hook really redirects `python app.py` while leaving `-c` and
  `AUTO_UV_DISABLE` alone — the regression guard the suite previously lacked.

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

