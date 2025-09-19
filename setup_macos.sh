#!/bin/bash
# Musico macOS Setup Script

echo "Musico macOS Setup"
echo "=================="
echo

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python from https://python.org or using Homebrew:"
    echo "  brew install python"
    exit 1
fi

python3 --version
echo "Python found!"
echo

# Check if Homebrew is installed (for portaudio)
echo "Checking for Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
    source ~/.zshrc
fi

# Install portaudio (required for PyAudio)
echo "Installing portaudio..."
brew install portaudio
echo

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "music_env" ]; then
    echo "Virtual environment already exists, removing old one..."
    rm -rf music_env
fi

python3 -m venv music_env
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "Virtual environment created successfully!"
echo

# Activate virtual environment
echo "Activating virtual environment..."
source music_env/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo "Virtual environment activated!"
echo

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip
echo

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    echo "Please check your internet connection and try again"
    exit 1
fi
echo

# Test audio devices
echo "Testing audio devices..."
python3 -c "
import pyaudio
p = pyaudio.PyAudio()
print('Available audio devices:')
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f'  {i}: {info[\"name\"]}')
p.terminate()
"
echo

# Test GUI
echo "Testing GUI..."
python3 -c "import tkinter; print('GUI test: PASSED')"
if [ $? -ne 0 ]; then
    echo "ERROR: GUI test failed"
    exit 1
fi
echo

# Test Shazam
echo "Testing Shazam API..."
python3 -c "from shazamio import Shazam; print('Shazam test: PASSED')"
if [ $? -ne 0 ]; then
    echo "ERROR: Shazam test failed"
    exit 1
fi
echo

echo "Setup completed successfully!"
echo
echo "To run Musico on macOS:"
echo "  source music_env/bin/activate"
echo "  python3 Musico_macos.py"
echo
echo "To exit fullscreen mode, press Escape or F11"
echo "To quit the application, press Q or Cmd+Q"
echo
