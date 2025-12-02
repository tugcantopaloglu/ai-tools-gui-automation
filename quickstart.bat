@echo off
echo ============================================================
echo AI Tools GUI Automation - Quick Start
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [3/4] Running setup tests...
python test_setup.py

echo.
echo [4/4] Setup complete!
echo.
echo ============================================================
echo Next Steps:
echo ============================================================
echo 1. Run the automation:
echo    python src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md
echo.
echo 2. Log in to Gemini when the browser opens
echo.
echo 3. Watch the automation work!
echo.
echo For help, see SETUP.md or example_usage.md
echo ============================================================
pause
