#!/bin/bash
set -e
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

echo "============================================================"
echo "AI Tools GUI Automation - Quick Start"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "[1/4] Checking Python installation..."
python3 --version

echo ""
echo "[2/4] Installing dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo "[3/4] Running setup tests..."
python3 test_setup.py

echo ""
echo "[4/4] Setup complete!"
echo ""
echo "============================================================"
echo "Next Steps:"
echo "============================================================"
echo "1. Run the automation:"
echo "   Create prompts.md using TEMPLATE.md, then run python3 src/main.py prompts.md"
echo ""
echo "2. Log in to Gemini when the browser opens"
echo ""
echo "3. Watch the automation work!"
echo ""
echo "For help, see README.md or SETUP.md"
echo "============================================================"
