"""
Tests for auto-uv functionality.

These tests verify that auto-uv correctly intercepts Python script execution
and re-executes them with 'uv run'.
"""

import os
import subprocess
import sys
import tempfile


def test_should_use_uv():
    """Test the should_use_uv function."""
    # Import the module
    from auto_uv import should_use_uv

    # Save original environment
    original_env = os.environ.copy()

    try:
        _should_use_uv_test(
            "UV_RUN_ACTIVE",
            should_use_uv,
            "Should not use uv when UV_RUN_ACTIVE is set",
        )
        _should_use_uv_test(
            "AUTO_UV_DISABLE",
            should_use_uv,
            "Should not use uv when AUTO_UV_DISABLE is set",
        )
        result = should_use_uv()
        print(f"UV available on system: {result}")

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def _should_use_uv_test(arg0, should_use_uv, arg2):
    # Test 1: Should return False if UV_RUN_ACTIVE is set
    os.environ[arg0] = "1"
    assert should_use_uv() is False, arg2

    # Test 2: Should return False if AUTO_UV_DISABLE is set
    del os.environ[arg0]


def test_script_execution():
    """Test that a script can be executed with auto-uv."""
    # Create a temporary test script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
import os
import sys

# Check if running under uv
if os.environ.get('UV_RUN_ACTIVE'):
    print('RUNNING_WITH_UV')
else:
    print('RUNNING_WITHOUT_UV')

sys.exit(0)
""")
        script_path = f.name

    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, script_path], capture_output=True, text=True, check=False
        )

        print(f"Script output: {result.stdout.strip()}")
        print(f"Script stderr: {result.stderr.strip()}")
        print(f"Return code: {result.returncode}")

        # Verify it ran successfully
        assert result.returncode == 0, (
            f"Script failed with return code {result.returncode}"
        )

    finally:
        # Clean up
        os.unlink(script_path)


def test_disable_flag():
    """Test that AUTO_UV_DISABLE flag works."""
    # Create a temporary test script
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
            import os
            if os.environ.get('UV_RUN_ACTIVE'):
                print('WITH_UV')
            else:
                print('WITHOUT_UV')
    """)
        script_path = f.name

    try:
        # Run with AUTO_UV_DISABLE
        env = os.environ.copy()
        env["AUTO_UV_DISABLE"] = "1"

        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        print(f"Output with AUTO_UV_DISABLE: {result.stdout.strip()}")

    finally:
        os.unlink(script_path)


def test_installed_package_not_intercepted():
    """
    Regression test for v0.1.0 bug.
    
    Bug: auto-uv intercepted installed packages like dbt, causing:
    'Fatal Python error: init_import_site: Failed to import the site module'
    
    This test verifies that scripts in site-packages are NOT intercepted.
    """
    # Create a mock site-packages directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        site_packages = os.path.join(tmpdir, "site-packages")
        os.makedirs(site_packages)
        
        # Create a fake installed package script (like dbt)
        fake_dbt = os.path.join(site_packages, "dbt_cli.py")
        with open(fake_dbt, "w") as f:
            f.write("""
import os
import sys

# This simulates an installed package like dbt
# It should NOT be intercepted by auto-uv
if os.environ.get('UV_RUN_ACTIVE'):
    print('ERROR: auto-uv intercepted an installed package!')
    sys.exit(1)
else:
    print('SUCCESS: Installed package ran normally')
    sys.exit(0)
""")
        
        # Run the fake installed package
        env = os.environ.copy()
        # Add our fake site-packages to PYTHONPATH
        env["PYTHONPATH"] = site_packages
        
        result = subprocess.run(
            [sys.executable, fake_dbt],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        
        print(f"Installed package test output: {result.stdout.strip()}")
        print(f"Installed package test stderr: {result.stderr.strip()}")
        
        # Verify the installed package was NOT intercepted
        assert result.returncode == 0, (
            f"Installed package was incorrectly intercepted! "
            f"Output: {result.stdout}, Stderr: {result.stderr}"
        )
        assert "SUCCESS" in result.stdout, (
            "Expected installed package to run without auto-uv interception"
        )


def test_project_detection():
    """
    Test that auto-uv detects when we're in a uv project directory.
    
    This covers the use case: "I'm in a folder with .venv, run python script.py"
    auto-uv should detect the project and use uv run.
    """
    from auto_uv import should_use_uv
    
    # Save original directory and environment
    original_dir = os.getcwd()
    original_env = os.environ.copy()
    
    try:
        # Temporarily remove AUTO_UV_DISABLE to test project detection
        if "AUTO_UV_DISABLE" in os.environ:
            del os.environ["AUTO_UV_DISABLE"]
        # Create a temporary project directory with markers
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test 1: Directory with pyproject.toml
            pyproject_dir = os.path.join(tmpdir, "project_with_pyproject")
            os.makedirs(pyproject_dir)
            with open(os.path.join(pyproject_dir, "pyproject.toml"), "w") as f:
                f.write("[project]\nname = 'test'\n")
            
            os.chdir(pyproject_dir)
            result = should_use_uv()
            print(f"Project with pyproject.toml: should_use_uv = {result}")
            assert result is True, "Should detect project with pyproject.toml"
            
            # Test 2: Directory with .venv
            venv_dir = os.path.join(tmpdir, "project_with_venv")
            os.makedirs(venv_dir)
            os.makedirs(os.path.join(venv_dir, ".venv"))
            
            os.chdir(venv_dir)
            result = should_use_uv()
            print(f"Project with .venv: should_use_uv = {result}")
            assert result is True, "Should detect project with .venv"
            
            # Test 3: Directory with uv.lock
            uvlock_dir = os.path.join(tmpdir, "project_with_uvlock")
            os.makedirs(uvlock_dir)
            with open(os.path.join(uvlock_dir, "uv.lock"), "w") as f:
                f.write("# uv lock file\n")
            
            os.chdir(uvlock_dir)
            result = should_use_uv()
            print(f"Project with uv.lock: should_use_uv = {result}")
            assert result is True, "Should detect project with uv.lock"
            
            # Test 4: Directory with no project markers
            no_project_dir = os.path.join(tmpdir, "no_project")
            os.makedirs(no_project_dir)
            
            os.chdir(no_project_dir)
            result = should_use_uv()
            print(f"Directory with no project markers: should_use_uv = {result}")
            assert result is False, "Should not detect project without markers"
            
            # Test 5: Subdirectory of a project (should find parent's pyproject.toml)
            subdir = os.path.join(pyproject_dir, "subdir", "nested")
            os.makedirs(subdir)
            
            os.chdir(subdir)
            result = should_use_uv()
            print(f"Subdirectory of project: should_use_uv = {result}")
            assert result is True, "Should detect project from parent directory"
            
    finally:
        # Restore original directory and environment
        os.chdir(original_dir)
        os.environ.clear()
        os.environ.update(original_env)


def test_no_site_initialization_crash():
    """
    Regression test for v0.1.1 bug.
    
    Bug: auto-uv called sys.exit() during site initialization, causing:
    'Fatal Python error: init_import_site: Failed to import the site module
     SystemExit: 0'
    
    This test verifies that importing auto_uv during site initialization
    does NOT crash Python, even when a script is being executed.
    """
    # Create a test script that will trigger site initialization
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
import sys
import os

# This script tests that auto_uv doesn't crash during site initialization
# The bug was that auto_uv.py called sys.exit() during import via .pth file

# If we get here without crashing, the bug is fixed
print('SUCCESS: No site initialization crash')
sys.exit(0)
""")
        script_path = f.name
    
    try:
        # Run the script - this will trigger site initialization
        # In v0.1.1, this would crash with "Fatal Python error: init_import_site"
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=False,
        )
        
        print(f"Site init test output: {result.stdout.strip()}")
        print(f"Site init test stderr: {result.stderr.strip()}")
        
        # Verify Python didn't crash during site initialization
        assert result.returncode == 0, (
            f"Python crashed during site initialization! "
            f"Return code: {result.returncode}, "
            f"Stderr: {result.stderr}"
        )
        
        # Verify we didn't get the fatal error
        assert "Fatal Python error" not in result.stderr, (
            "Got 'Fatal Python error' - site initialization crashed!"
        )
        
        assert "SUCCESS" in result.stdout, (
            "Script didn't run successfully"
        )
        
    finally:
        os.unlink(script_path)


if __name__ == "__main__":
    print("Running auto-uv tests...\n")

    print("Test 1: should_use_uv()")
    try:
        test_should_use_uv()
        print("PASSED\n")
    except Exception as e:
        print(f"FAILED: {e}\n")

    print("Test 2: Script execution")
    try:
        test_script_execution()
        print("PASSED\n")
    except Exception as e:
        print(f"FAILED: {e}\n")

    print("Test 3: AUTO_UV_DISABLE flag")
    try:
        test_disable_flag()
        print("PASSED\n")
    except Exception as e:
        print(f"FAILED: {e}\n")

    print("Test 4: Installed packages not intercepted (v0.1.0 regression)")
    try:
        test_installed_package_not_intercepted()
        print("PASSED\n")
    except Exception as e:
        print(f"FAILED: {e}\n")

    print("Test 5: No site initialization crash (v0.1.1 regression)")
    try:
        test_no_site_initialization_crash()
        print("PASSED\n")
    except Exception as e:
        print(f"FAILED: {e}\n")

    print("Test 6: Project detection (pyproject.toml, .venv, uv.lock)")
    try:
        test_project_detection()
        print("PASSED\n")
    except Exception as e:
        print(f"FAILED: {e}\n")

    print("Tests complete!")
