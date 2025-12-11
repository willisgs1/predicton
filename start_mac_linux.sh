#!/bin/bash

echo "[System] Waking up the Agent..."

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "[Error] Python3 could not be found."
    echo "Please install Python 3.10+ (e.g., 'brew install python' on Mac or 'sudo apt install python3' on Linux)."
    exit 1
fi

# Install dependencies
echo "[System] Verifying Neural and Quantum dependencies..."
pip install -r ai_core/requirements.txt

if [ $? -ne 0 ]; then
    echo "[Error] Failed to install dependencies."
    exit 1
fi

# Run the AI
echo "[System] Dependencies OK. Starting Life Loop..."
echo ""
python3 -m ai_core.main
