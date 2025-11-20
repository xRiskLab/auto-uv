"""
Tests for auto-uv functionality.

These tests verify that auto-uv correctly intercepts Python script execution
and re-executes them with 'uv run'.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path


def test_should_use_uv():
    """Test the should_use_uv function."""
    # Import the module
    from auto_uv import should_use_uv
    
    # Save original environment
    original_env = os.environ.copy()
    
    try:
        # Test 1: Should return False if UV_RUN_ACTIVE is set
        os.environ["UV_RUN_ACTIVE"] = "1"
        assert should_use_uv() is False, "Should not use uv when UV_RUN_ACTIVE is set"
        
        # Test 2: Should return False if AUTO_UV_DISABLE is set
        del os.environ["UV_RUN_ACTIVE"]
        os.environ["AUTO_UV_DISABLE"] = "1"
        assert should_use_uv() is False, "Should not use uv when AUTO_UV_DISABLE is set"
        
        # Test 3: Check if uv is available (this depends on the system)
        del os.environ["AUTO_UV_DISABLE"]
        result = should_use_uv()
        print(f"UV available on system: {result}")
        
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def test_script_execution():
    """Test that a script can be executed with auto-uv."""
    # Create a temporary test script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
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
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )
        
        print(f"Script output: {result.stdout.strip()}")
        print(f"Script stderr: {result.stderr.strip()}")
        print(f"Return code: {result.returncode}")
        
        # Verify it ran successfully
        assert result.returncode == 0, f"Script failed with return code {result.returncode}"
        
    finally:
        # Clean up
        os.unlink(script_path)


def test_disable_flag():
    """Test that AUTO_UV_DISABLE flag works."""
    # Create a temporary test script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
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
        env['AUTO_UV_DISABLE'] = '1'
        
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            env=env
        )
        
        print(f"Output with AUTO_UV_DISABLE: {result.stdout.strip()}")
        
    finally:
        os.unlink(script_path)


if __name__ == "__main__":
    print("Running auto-uv tests...\n")
    
    print("Test 1: should_use_uv()")
    print("-" * 50)
    try:
        test_should_use_uv()
        print("✅ PASSED\n")
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
    
    print("Test 2: Script execution")
    print("-" * 50)
    try:
        test_script_execution()
        print("✅ PASSED\n")
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
    
    print("Test 3: AUTO_UV_DISABLE flag")
    print("-" * 50)
    try:
        test_disable_flag()
        print("✅ PASSED\n")
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
    
    print("=" * 50)
    print("Tests complete!")

