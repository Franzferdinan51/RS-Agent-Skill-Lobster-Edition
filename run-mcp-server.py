#!/usr/bin/env python3
"""
RS-Agent MCP Server Launcher
=============================
Wrapper script to ensure correct Python and dependencies are used.

This script:
1. Verifies Python version
2. Checks dependencies
3. Launches the MCP server

Usage:
    ./run-mcp-server.sh
    OR
    python3 run-mcp-server.py
"""

import sys
import subprocess
from pathlib import Path

REQUIRED_PYTHON_VERSION = (3, 8)
SCRIPT_DIR = Path(__file__).parent


def check_python_version():
    """Verify Python version is 3.8+"""
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        print(f"❌ Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}+ required", file=sys.stderr)
        print(f"   Current version: {sys.version_info.major}.{sys.version_info.minor}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", file=sys.stderr)


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import requests
        print(f"✅ requests version: {requests.__version__}", file=sys.stderr)
        return True
    except ImportError:
        print("❌ requests library not found!", file=sys.stderr)
        print("", file=sys.stderr)
        print("To install, run:", file=sys.stderr)
        print("  pip3 install requests --break-system-packages", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or create a virtual environment:", file=sys.stderr)
        print("  python3 -m venv venv", file=sys.stderr)
        print("  source venv/bin/activate", file=sys.stderr)
        print("  pip install requests", file=sys.stderr)
        return False


def main():
    """Launch the MCP server."""
    print("=" * 60, file=sys.stderr)
    print("RS-Agent MCP Server Launcher", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    if not check_dependencies():
        print("", file=sys.stderr)
        print("⚠️  Dependencies missing. Attempting to install...", file=sys.stderr)
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "requests", "--break-system-packages"], check=True)
            print("✅ Dependencies installed!", file=sys.stderr)
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}", file=sys.stderr)
            sys.exit(1)
    
    print("=" * 60, file=sys.stderr)
    print("Starting MCP Server...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # Launch the actual MCP server
    mcp_server = SCRIPT_DIR / "mcp-server.py"
    
    # Replace this process with the MCP server
    os = __import__('os')
    os.execv(sys.executable, [sys.executable, str(mcp_server)])


if __name__ == "__main__":
    main()
