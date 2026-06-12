"""auto-uv: transparently re-run ``python script.py`` as ``uv run`` in a project.

The package installs a ``hatch-autorun`` ``.pth`` file that calls
:func:`auto_use_uv` during interpreter site-initialization. When the interpreter
is starting up to run a *user script* inside a uv project, we re-exec the process
as ``uv run <script>`` so the script picks up the project's environment.

Detection runs at site-init time, where ``__main__.__file__`` is not set yet but
``sys.argv[0]`` already holds the script path (REPL -> ``''``, ``-c`` -> ``'-c'``,
``-m`` -> ``'-m'``). We therefore key off ``sys.argv[0]`` and never raise into
site initialization.
"""

import os
import subprocess
import sys

# Project markers that mean "this directory tree is a uv project".
_PROJECT_MARKERS = ("pyproject.toml", "uv.lock")
_MAX_PARENT_DEPTH = 10

# Directories whose scripts must never be hijacked (system / distro Python).
_SYSTEM_DIRS = (
    "/usr/bin", "/usr/local/bin", "/opt/bin", "/bin", "/sbin",
    "/usr/sbin", "/usr/local/sbin",
)


def _env_disables(environ):
    """True if the environment opts out of interception."""
    if environ.get("UV_RUN_ACTIVE"):
        return True  # already inside `uv run` -> never recurse
    return environ.get("AUTO_UV_DISABLE", "").lower() in ("1", "true", "yes")


def _uv_available():
    """True if a working ``uv`` is on PATH."""
    try:
        subprocess.run(
            ["uv", "--version"], capture_output=True, check=True, timeout=2
        )
        return True
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
        OSError,
    ):
        return False


def _in_uv_project(cwd):
    """True if ``cwd`` or any parent (up to a bounded depth) is a uv project."""
    check_dir = cwd
    for _ in range(_MAX_PARENT_DEPTH):
        for marker in _PROJECT_MARKERS:
            if os.path.exists(os.path.join(check_dir, marker)):
                return True
        if os.path.isdir(os.path.join(check_dir, ".venv")):
            return True
        parent = os.path.dirname(check_dir)
        if parent == check_dir:  # reached filesystem root
            break
        check_dir = parent
    return False


def should_use_uv():
    """Back-compatible helper: env + uv availability + project detection (cwd)."""
    if _env_disables(os.environ):
        return False
    if not _uv_available():
        return False
    return _in_uv_project(os.getcwd())


def _script_target(argv):
    """Return the abs path of the user script iff ``argv`` is ``python <file.py>``.

    Returns ``None`` for the REPL (``argv[0] == ''``), ``python -c`` (``'-c'``),
    ``python -m mod`` (``'-m'`` at site-init time), stdin, or any ``argv[0]`` that
    is not an existing regular file.
    """
    if not argv:
        return None
    arg0 = argv[0]
    if not arg0 or arg0 in ("-c", "-m"):
        return None
    try:
        if not os.path.isfile(arg0):
            return None
        return os.path.abspath(arg0)
    except (OSError, ValueError):
        return None


def _is_excluded_script(script_path):
    """True if ``script_path`` is an installed tool / venv / system / stdlib script.

    Prevents hijacking console entrypoints (dbt, pip, pytest, ...) and anything
    living inside ``site-packages``, a venv ``bin``/``Scripts`` dir, the Python
    installation, or a system bin directory.
    """
    sep = os.path.sep
    if "site-packages" in script_path or "dist-packages" in script_path:
        return True
    if (
        sep + "bin" + sep in script_path
        or sep + "Scripts" + sep in script_path
        or script_path.endswith(sep + "bin")
        or script_path.endswith(sep + "Scripts")
    ):
        return True
    for prefix in (getattr(sys, "prefix", ""), getattr(sys, "base_prefix", "")):
        if prefix and script_path.startswith(prefix + sep):
            return True
    for sys_dir in _SYSTEM_DIRS:
        if script_path == sys_dir or script_path.startswith(sys_dir + sep):
            return True
    return False


def _should_intercept(argv=None, cwd=None, environ=None):
    """Pure decision: should this interpreter startup be redirected to ``uv run``?

    Arguments default to the live process state but are injectable for testing.
    """
    argv = sys.argv if argv is None else argv
    cwd = os.getcwd() if cwd is None else cwd
    environ = os.environ if environ is None else environ

    if _env_disables(environ):
        return False
    script = _script_target(argv)
    if script is None:
        return False
    if _is_excluded_script(script):
        return False
    if not _uv_available():
        return False
    return _in_uv_project(cwd)


def _find_uv():
    """Locate the ``uv`` executable on PATH (handles Windows suffixes)."""
    names = ("uv", "uv.exe", "uv.cmd", "uv.bat")
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        for name in names:
            candidate = os.path.join(path_dir, name)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
    return None


def auto_use_uv():
    """Re-exec ``python <script.py>`` as ``uv run <script.py>`` inside a uv project.

    Invoked from the ``.pth`` autorun hook during site-initialization, so the
    entire body is guarded: it must never raise into interpreter startup.
    """
    try:
        if not _should_intercept():
            return
        uv_path = _find_uv()
        if uv_path is None:
            return
        # Guard against infinite re-execution; the child sees UV_RUN_ACTIVE=1.
        os.environ["UV_RUN_ACTIVE"] = "1"
        cmd = [uv_path, "run", *sys.argv]
        os.execve(uv_path, cmd, os.environ)
    except Exception as exc:  # never crash interpreter startup
        try:
            sys.stderr.write(f"auto-uv: skipped interception ({exc})\n")
        except Exception:
            pass
        return
