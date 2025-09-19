#!/bin/bash
# Musico macOS Run Script

echo "Starting Musico for macOS..."
echo

# Check if virtual environment exists
if [ ! -d "music_env" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run setup_macos.sh first"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source music_env/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Run Musico
echo "Starting Musico..."
python3 Musico_macos.py
