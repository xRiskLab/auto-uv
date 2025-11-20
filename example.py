#!/usr/bin/env python3
"""
Example script to demonstrate auto-uv functionality.

With auto-uv installed, you can run this script with:
    python example.py

Instead of:
    uv run example.py

Auto-uv will automatically detect and use uv run behind the scenes!
"""

import os
import sys


def main():
    """Main function to demonstrate auto-uv functionality."""
    print("Auto-UV Example Script")

    # Check if we're running under UV
    if os.environ.get("UV_RUN_ACTIVE"):
        print("This script is running under 'uv run' (via auto-uv)")
    else:
        print("This script is running with regular Python")

    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")

    print("Environment variables set by auto-uv:")
    print(f"UV_RUN_ACTIVE: {os.environ.get('UV_RUN_ACTIVE', 'Not set')}")
    print(f"AUTO_UV_DISABLE: {os.environ.get('AUTO_UV_DISABLE', 'Not set')}")
    print()

    print("Script completed successfully!")


if __name__ == "__main__":
    main()
