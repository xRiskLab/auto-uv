import sys
import os
import subprocess


def _find_project_root(start_dir, max_depth=10):
    """
    Walk up from start_dir looking for uv project markers.

    Returns the project root directory if found, None otherwise.
    """
    check_dir = os.path.abspath(start_dir)
    for _ in range(max_depth):
        # Check for uv project markers
        if (os.path.isfile(os.path.join(check_dir, "pyproject.toml")) or
            os.path.isdir(os.path.join(check_dir, ".venv")) or
            os.path.isfile(os.path.join(check_dir, "uv.lock"))):
            return check_dir

        # Move up one directory
        parent = os.path.dirname(check_dir)
        if parent == check_dir:  # Reached root
            break
        check_dir = parent

    return None


def should_use_uv(script_path=None):
    """Check if we should intercept and use uv run."""
    # Don't intercept if we're already running under uv
    if os.environ.get("UV_RUN_ACTIVE"):
        return False

    # Don't intercept if AUTO_UV is explicitly disabled
    if os.environ.get("AUTO_UV_DISABLE", "").lower() in ("1", "true", "yes"):
        return False

    # Check if uv is available
    try:
        subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            check=True,
            timeout=2
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

    # Check if we're in a uv project (has pyproject.toml or .venv or uv.lock)
    # First, try to find project root from the script's directory (if provided)
    # This handles the case: "cd /some/dir && python /path/to/project/script.py"
    # Then fall back to current working directory for backwards compatibility
    project_root = None

    if script_path:
        script_dir = os.path.dirname(os.path.abspath(script_path))
        project_root = _find_project_root(script_dir)

    if not project_root:
        project_root = _find_project_root(os.getcwd())

    return project_root is not None


def auto_use_uv():
    """
    Automatically re-execute the current script with 'uv run' if conditions are met.
    
    This function checks if:
    1. We're not already running under uv
    2. UV_RUN_ACTIVE environment variable is not set
    3. uv is available in the system
    4. We're running a user script (not a package/tool script)
    5. We're in the main execution context (not during import/site initialization)
    
    If all conditions are met, it replaces the current process with 'uv run'.
    
    Note: This function intelligently skips interception for:
    - Installed packages (site-packages, dist-packages)
    - Virtual environment executables (bin/, Scripts/)
    - Python installation scripts
    This prevents interference with tools like dbt, pytest, pip, etc.
    """
    # CRITICAL: Don't intercept during site initialization or imports
    # Only intercept when __name__ == '__main__' in the actual script being run
    # We check if sys.argv[0] matches the file being executed
    if not sys.argv or not sys.argv[0]:
        return
    
    # Don't intercept if we're being imported (not the main script)
    # This prevents interception during site.py initialization
    try:
        import __main__
        if not hasattr(__main__, '__file__'):
            return
        # Normalize both paths to absolute for comparison (handles relative vs absolute)
        main_file = os.path.abspath(__main__.__file__) if __main__.__file__ else None
        argv_file = os.path.abspath(sys.argv[0]) if sys.argv[0] else None
        if main_file != argv_file:
            return
    except (ImportError, AttributeError):
        return
    
    # Only intercept if running a script file
    if os.path.isfile(sys.argv[0]):
        script_path = os.path.abspath(sys.argv[0])
        
        # Don't intercept if script is in site-packages or installed packages
        # This prevents interference with tools like dbt, pip, etc.
        if "site-packages" in script_path or "dist-packages" in script_path:
            return
        
        # Don't intercept if script is in a virtual environment's bin/Scripts directory
        # Also check if path ends with /bin or /Scripts (e.g., /usr/bin, /usr/local/bin)
        if (os.path.sep + "bin" + os.path.sep in script_path or 
            os.path.sep + "Scripts" + os.path.sep in script_path or
            script_path.endswith(os.path.sep + "bin") or
            script_path.endswith(os.path.sep + "Scripts") or
            script_path.startswith(os.path.sep + "bin" + os.path.sep) or
            script_path.startswith(os.path.sep + "Scripts" + os.path.sep)):
            return
        
        # Don't intercept if script is in Python installation directory
        if sys.prefix in script_path or sys.base_prefix in script_path:
            return
        
        # Don't intercept if script is in system-wide directories
        system_dirs = ["/usr/bin", "/usr/local/bin", "/opt/bin", "/bin", "/sbin", 
                       "/usr/sbin", "/usr/local/sbin"]
        for sys_dir in system_dirs:
            if script_path.startswith(sys_dir + os.path.sep) or script_path == sys_dir:
                return
        
        if should_use_uv(script_path):
            # Set environment variable to prevent infinite loop
            os.environ["UV_RUN_ACTIVE"] = "1"
            
            # Build the uv run command
            cmd = ["uv", "run"] + sys.argv
            
            # Replace the current process with uv run (no subprocess, no exit)
            # This is cleaner and doesn't cause site initialization issues
            try:
                # Find uv in PATH (handle both Unix and Windows)
                uv_path = None
                uv_names = ["uv"]
                
                # On Windows, also check for .exe, .cmd, .bat
                if sys.platform == "win32":
                    uv_names.extend(["uv.exe", "uv.cmd", "uv.bat"])
                
                for path_dir in os.environ.get("PATH", "").split(os.pathsep):
                    for uv_name in uv_names:
                        candidate = os.path.join(path_dir, uv_name)
                        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                            uv_path = candidate
                            break
                    if uv_path:
                        break
                
                if uv_path:
                    # Use os.execve to replace the current process
                    os.execve(uv_path, cmd, os.environ)
                else:
                    # Fallback: uv not found, continue normally
                    return
            except Exception as e:
                # If exec fails, continue with normal execution
                print(f"Warning: Failed to exec uv: {e}", file=sys.stderr)
                return

