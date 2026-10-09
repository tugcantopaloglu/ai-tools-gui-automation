@echo off
cd /d "%~dp0"
if errorlevel 1 exit /b 1
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
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo.
echo [3/4] Running setup tests...
python test_setup.py
if errorlevel 1 exit /b 1

echo.
echo [4/4] Setup complete!
echo.
echo ============================================================
echo Next Steps:
echo ============================================================
echo 1. Run the automation:
echo    Create prompts.md using TEMPLATE.md, then run python src/main.py prompts.md
echo.
echo 2. Log in to Gemini when the browser opens
echo.
echo 3. Watch the automation work!
echo.
echo For help, see README.md or SETUP.md
echo ============================================================
pause
