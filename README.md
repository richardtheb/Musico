# Musico

A Python script that automatically identifies music playing in the environment using Shazam. Works on both Raspberry Pi and macOS.

## Features

- Samples audio every 60 seconds from the default audio input
- Detects silence and skips processing when no music is playing
- Uses Shazam API to identify music tracks
- Displays track information and cover art in a GUI
- Comprehensive logging for debugging
- Runs in isolated virtual environment
- Cross-platform support (Raspberry Pi and macOS)

## Requirements

- **Raspberry Pi**: Audio input capability, Python 3.7+
- **macOS**: Built-in microphone or external audio input, Python 3.7+
- Internet connection for Shazam API calls

## Quick Setup

### For Raspberry Pi:
1. Clone or download this repository to your Raspberry Pi
2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

### For macOS:
1. Clone or download this repository to your Mac
2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

The setup script will automatically:
- Detect your operating system
- Install system dependencies (via apt on Linux, Homebrew on macOS)
- Create a virtual environment
- Install all Python packages

## Usage

### Option 1: Using the run script (recommended)
```bash
./run.sh
```

### Option 2: Manual activation
```bash
# Activate virtual environment
source music_env/bin/activate

# Run the script
python music_identifier.py

# Deactivate when done
deactivate
```

### Testing Your Setup
After setup, you can test if everything is working by running Musico:
```bash
./run.sh
```

The application will start and begin sampling audio. Check the console output for any error messages.

The script will:
1. Start a GUI window showing the current status
2. Begin sampling audio every 60 seconds
3. Display identified tracks with cover art
4. Log all activity to `Musico.log`

## Tools

Musico includes several helpful tools:

- **`adjust_threshold.py`** - Interactive threshold adjustment tool
- **`select_input.py`** - Audio input device selector
- **`run.sh`** - Easy startup script
- **`setup.sh`** - Cross-platform installation script

## Configuration

You can adjust these parameters in `config.py`:
- `RECORD_DURATION`: Length of audio sample (default: 10 seconds)
- `SILENCE_THRESHOLD`: Sensitivity for silence detection (default: 0.0001)
- `SAMPLE_RATE`: Audio sample rate (default: 44100 Hz)

If Musico is too sensitive or not sensitive enough, you can adjust the `SILENCE_THRESHOLD` value:

**Option 1: Use the adjustment tool (recommended)**
```bash
python adjust_threshold.py
```

**Option 2: Edit config.py manually**
- Lower values (e.g., 0.0001) = more sensitive to quiet sounds
- Higher values (e.g., 0.01) = less sensitive, requires louder music

## Troubleshooting

### Audio Issues
- **Raspberry Pi**: Check that your audio input is working with: `arecord -l`
- **macOS**: Check System Preferences > Sound > Input to ensure microphone is working
- **Multiple devices**: If you have multiple audio inputs, select the right one:
  ```bash
  python select_input.py
  ```
- Adjust `silence_threshold` if the script is too sensitive or not sensitive enough

### General Issues
- Check the log file for detailed error messages
- Ensure internet connectivity for Shazam API calls
- If you encounter permission issues, make sure the scripts are executable: `chmod +x *.sh`

### macOS Specific
- If you get "portaudio" errors, make sure Homebrew installed it correctly: `brew list portaudio`
- If tkinter GUI doesn't work, install python-tk: `brew install python-tk`
- If you get permission errors with Homebrew, you may need to run: `sudo chown -R $(whoami) /usr/local/var/homebrew`
- If you get "pyaudioop" errors on Python 3.13+, the script includes a compatibility module
- If you get FFmpeg warnings, install it with: `brew install ffmpeg`

### Python 3.13+ Compatibility
The script includes `pyaudioop_compat.py` to handle the removal of the `pyaudioop` module in Python 3.13+. This is automatically loaded when needed.

## Virtual Environment Management

The project uses a virtual environment to isolate dependencies:

- **Virtual environment location**: `music_env/`
- **Activation**: `source music_env/bin/activate`
- **Deactivation**: `deactivate`
- **Reinstalling dependencies**: `pip install -r requirements.txt` (while activated)

## Dependencies

- `pyaudio`: Audio recording
- `numpy`: Audio processing
- `shazamio`: Shazam API integration
- `Pillow`: Image processing for cover art
- `requests`: HTTP requests for downloading images
- `tkinter`: GUI (usually included with Python)
