#!/usr/bin/env python3
"""
RS-Agent MCP Server Launcher - Universal
=========================================
Finds the correct Python interpreter and ensures dependencies are installed.

This script:
1. Finds best Python (prefers 3.8+, tries multiple paths)
2. Verifies dependencies
3. Auto-installs if missing
4. Launches MCP server

Usage:
    ./mcp-launcher.py
"""

import sys
import subprocess
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
MCP_SERVER = SCRIPT_DIR / "mcp-server.py"

def find_python():
    """Find best available Python 3 interpreter."""
    candidates = [
        sys.executable,  # Current Python
        "/opt/homebrew/bin/python3",  # Homebrew Python (macOS ARM)
        "/usr/local/bin/python3",  # Homebrew Python (macOS Intel)
        "python3",  # From PATH
        "/usr/bin/python3",  # System Python
    ]
    
    for python in candidates:
        try:
            result = subprocess.run(
                [python, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Check version is 3.8+
                version_str = result.stderr.split()[-1] if result.stderr else result.stdout.split()[-1]
                major, minor = map(int, version_str.split('.')[:2])
                if major == 3 and minor >= 8:
                    return python
        except Exception:
            continue
    
    # Fallback to any Python 3
    for python in candidates:
        try:
            result = subprocess.run([python, "--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return python
        except Exception:
            continue
    
    return None

def check_and_install_dependencies(python):
    """Check if requests is installed, install if not."""
    try:
        subprocess.run(
            [python, "-c", "import requests"],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        print(f"Installing requests for {python}...")
        try:
            # Try with --break-system-packages first (newer pip)
            subprocess.run(
                [python, "-m", "pip", "install", "requests", "--break-system-packages"],
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            try:
                # Fallback to --user
                subprocess.run(
                    [python, "-m", "pip", "install", "requests", "--user"],
                    check=True
                )
                return True
            except subprocess.CalledProcessError as e:
                print(f"Failed to install requests: {e}")
                return False

def main():
    print("=" * 60, file=sys.stderr)
    print("RS-Agent MCP Server Launcher", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # Find Python
    python = find_python()
    if not python:
        print("❌ No Python 3 interpreter found!", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ Using Python: {python}", file=sys.stderr)
    
    # Check version
    result = subprocess.run([python, "--version"], capture_output=True, text=True)
    print(f"   Version: {result.stderr.strip() or result.stdout.strip()}", file=sys.stderr)
    
    # Check/install dependencies
    if not check_and_install_dependencies(python):
        print("❌ Failed to install dependencies!", file=sys.stderr)
        print("", file=sys.stderr)
        print("Manual installation:", file=sys.stderr)
        print(f"  {python} -m pip install requests", file=sys.stderr)
        sys.exit(1)
    
    print("✅ Dependencies installed", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("Starting MCP Server...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # Launch MCP server
    os.execv(python, [python, str(MCP_SERVER)])

if __name__ == "__main__":
    main()
