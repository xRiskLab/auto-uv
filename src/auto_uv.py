import sys
import os
import subprocess


def should_use_uv():
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
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def auto_use_uv():
    """
    Automatically re-execute the current script with 'uv run' if conditions are met.
    
    This function checks if:
    1. We're not already running under uv
    2. UV_RUN_ACTIVE environment variable is not set
    3. uv is available in the system
    4. We're running a user script (not a package/tool script)
    
    If all conditions are met, it re-executes the script with 'uv run'.
    
    Note: This function intelligently skips interception for:
    - Installed packages (site-packages, dist-packages)
    - Virtual environment executables (bin/, Scripts/)
    - Python installation scripts
    This prevents interference with tools like dbt, pytest, pip, etc.
    """
    # Only intercept if running a script file
    if len(sys.argv) > 0 and sys.argv[0] and os.path.isfile(sys.argv[0]):
        script_path = os.path.abspath(sys.argv[0])
        
        # Don't intercept if script is in site-packages or installed packages
        # This prevents interference with tools like dbt, pip, etc.
        if "site-packages" in script_path or "dist-packages" in script_path:
            return
        
        # Don't intercept if script is in a virtual environment's bin/Scripts directory
        if os.path.sep + "bin" + os.path.sep in script_path or os.path.sep + "Scripts" + os.path.sep in script_path:
            return
        
        # Don't intercept if script is in Python installation directory
        if sys.prefix in script_path or sys.base_prefix in script_path:
            return
        
        if should_use_uv():
            # Set environment variable to prevent infinite loop
            env = os.environ.copy()
            env["UV_RUN_ACTIVE"] = "1"
            
            # Build the uv run command
            cmd = ["uv", "run"] + sys.argv
            
            # Execute with uv run and exit
            try:
                result = subprocess.run(cmd, env=env)
                sys.exit(result.returncode)
            except Exception as e:
                # If uv run fails, continue with normal execution
                print(f"Warning: Failed to run with uv: {e}", file=sys.stderr)
                return

