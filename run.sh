#!/bin/bash
# Run script for Music Identifier

echo "Starting Music Identifier..."

# Check if virtual environment exists
if [ ! -d "music_env" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source music_env/bin/activate

# Check if required packages are installed
echo "Checking dependencies..."
python -c "import pyaudio, numpy, shazamio, PIL, requests, tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Some dependencies are missing. Installing..."
    pip install -r requirements.txt
fi

# Run the music identifier
echo "Starting Musico..."
python Musico.py

# Deactivate virtual environment when done
deactivate

