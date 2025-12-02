#!/bin/bash

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
pip3 install -r requirements.txt

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
echo "   python3 src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md"
echo ""
echo "2. Log in to Gemini when the browser opens"
echo ""
echo "3. Watch the automation work!"
echo ""
echo "For help, see SETUP.md or example_usage.md"
echo "============================================================"
