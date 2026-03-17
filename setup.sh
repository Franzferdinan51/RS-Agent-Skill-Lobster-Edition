#!/bin/bash
# RS-Agent Setup Script for Unix/Linux/macOS
# ===========================================
# Cross-platform setup - Unix version

set -e

echo ""
echo "🦆 RS-Agent-Skill-Lobster-Edition Setup"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/portfolio data/collection config logs

echo "✅ Directories created"
echo ""

# Make tools executable
echo "🔧 Making tools executable..."
chmod +x tools/*.py 2>/dev/null || echo "Note: File permissions not changed (Windows?)"

echo "✅ Tools ready"
echo ""

# Test installation
echo "🧪 Testing installation..."
if python3 tools/runescape-api.py --clan "Lords of Arcadia" --json > /dev/null 2>&1; then
    echo "✅ Tools working correctly"
else
    echo "⚠️  Warning: Tool test failed, but installation may still work"
fi

echo ""
echo "========================================"
echo "✅ Setup complete!"
echo ""
echo "Quick Start:"
echo "  python3 tools/runescape-api.py --clan 'Your Clan'"
echo "  python3 tools/portfolio-tracker.py --view"
echo "  python3 tools/multi-clan-compare.py --clan 'Clan1' --clan 'Clan2'"
echo ""
echo "For Discord bot setup, see discord-bot/README.md"
echo "For LM Studio MCP setup, see docs/MCP-GUIDE.md"
echo "========================================"
echo ""
