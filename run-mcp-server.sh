#!/bin/bash
# RS-Agent MCP Server Launcher
# =============================
# Ensures dependencies are installed before running MCP server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=${PYTHON:-python3}

echo "============================================================"
echo "RS-Agent MCP Server Launcher"
echo "============================================================"

# Check Python version
echo "Checking Python version..."
$PYTHON --version

# Check/install dependencies
echo "Checking dependencies..."
if ! $PYTHON -c "import requests" 2>/dev/null; then
    echo "⚠️  requests library not found. Installing..."
    $PYTHON -m pip install requests --break-system-packages
    echo "✅ Dependencies installed!"
else
    echo "✅ All dependencies installed"
fi

echo "============================================================"
echo "Starting MCP Server..."
echo "============================================================"

# Launch MCP server
exec $PYTHON "$SCRIPT_DIR/mcp-server.py"
