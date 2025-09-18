#!/bin/bash
# Setup script for Musico (Raspberry Pi and macOS)

echo "Setting up Musico..."

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "Detected Linux (Raspberry Pi)"
else
    echo "Error: Unsupported operating system: $OSTYPE"
    echo "This script supports macOS and Linux (Raspberry Pi)"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    if [[ "$OS" == "macos" ]]; then
        echo "On macOS, you can install Python 3 using Homebrew: brew install python3"
        echo "Or download from https://www.python.org/downloads/"
    else
        echo "On Linux, install with: sudo apt install python3"
    fi
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Installing pip..."
    if [[ "$OS" == "macos" ]]; then
        # On macOS, pip3 usually comes with Python 3
        echo "Please install pip3 manually or reinstall Python 3"
        exit 1
    else
        sudo apt update
        sudo apt install python3-pip -y
    fi
fi

# Install system dependencies for audio processing
echo "Installing system dependencies..."
if [[ "$OS" == "macos" ]]; then
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install portaudio and other dependencies
    echo "Installing audio dependencies via Homebrew..."
    brew install portaudio
    brew install ffmpeg  # For audio processing with pydub
    brew install python-tk  # For tkinter GUI support
    
elif [[ "$OS" == "linux" ]]; then
    sudo apt update
    sudo apt install portaudio19-dev python3-pyaudio python3-venv python3-tk -y
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv music_env

# Activate virtual environment
echo "Activating virtual environment..."
source music_env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To run Musico:"
echo "1. Activate the virtual environment: source music_env/bin/activate"
echo "2. Run the script: python Musico.py"
echo ""
echo "Or simply run: ./run.sh"
echo ""
echo "To deactivate the virtual environment when done: deactivate"

