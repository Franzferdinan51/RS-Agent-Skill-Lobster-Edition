#!/bin/bash
# Fix npm Permissions - RS-Agent MCP
# ====================================
# Run this script to fix npm cache permission issues

echo "🔧 Fixing npm permissions..."
echo ""

# Fix npm cache ownership
echo "1. Fixing npm cache ownership..."
sudo chown -R $(whoami) ~/.npm

# Clean npm cache
echo "2. Cleaning npm cache..."
npm cache clean --force

# Verify npm works
echo "3. Verifying npm..."
if npx --version > /dev/null 2>&1; then
    echo "✅ npm is working correctly"
else
    echo "❌ npm still has issues"
    exit 1
fi

echo ""
echo "✅ npm permissions fixed!"
echo ""
echo "Next steps:"
echo "1. Restart LM Studio"
echo "2. Test MCP servers"
