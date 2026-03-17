@echo off
REM RS-Agent Setup Script for Windows
REM ==================================
REM Cross-platform setup - Windows version

echo.
echo 🦆 RS-Agent-Skill-Lobster-Edition Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    exit /b 1
)

echo ✅ Python found
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

echo ✅ Dependencies installed
echo.

REM Create data directories
echo 📁 Creating data directories...
if not exist "data\portfolio" mkdir "data\portfolio"
if not exist "data\collection" mkdir "data\collection"
if not exist "config" mkdir "config"
if not exist "logs" mkdir "logs"

echo ✅ Directories created
echo.

REM Test installation
echo 🧪 Testing installation...
python tools\runescape-api.py --clan "Lords of Arcadia" --json >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Warning: Tool test failed, but installation may still work
) else (
    echo ✅ Tools working correctly
)

echo.
echo ========================================
echo ✅ Setup complete!
echo.
echo Quick Start:
echo   python tools\runescape-api.py --clan "Your Clan"
echo   python tools\portfolio-tracker.py --view
echo   python tools\multi-clan-compare.py --clan "Clan1" --clan "Clan2"
echo.
echo For Discord bot setup, see discord-bot\README.md
echo For LM Studio MCP setup, see docs\MCP-GUIDE.md
echo ========================================
echo.

pause
