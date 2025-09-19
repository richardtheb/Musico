# Musico - Windows Version

A full-screen music identification tool that displays album artwork when music is detected.

## Features

- **Full-Screen Display**: Black screen for silence, white screen for music detection, full-screen album art for identified music
- **No Text Overlay**: Clean, minimalist interface focusing on album artwork
- **Automatic Audio Detection**: Automatically finds and uses your microphone
- **Real-time Music Identification**: Uses Shazam API to identify songs
- **Windows Optimized**: Designed specifically for Windows audio systems

## Requirements

- Windows 10 or later
- Python 3.8 or later
- Microphone or audio input device
- Internet connection (for music identification)

## Quick Start

1. **Download and Extract**: Extract all files to a folder (e.g., `C:\Musico`)

2. **Run Setup**: Double-click `setup_windows.bat`
   - This will install Python dependencies
   - Test your audio devices
   - Set up the virtual environment

3. **Run Musico**: Double-click `run_windows.bat`
   - The application will start in full-screen mode
   - Press `Escape` to exit full-screen
   - Press `Q` to quit the application

## Manual Installation

If the batch files don't work, you can install manually:

```cmd
# Create virtual environment
python -m venv music_env

# Activate virtual environment
music_env\Scripts\activate.bat

# Install requirements
pip install -r requirements_windows.txt

# Run Musico
python Musico_windows.py
```

## Audio Device Selection

Musico will automatically detect and use your default microphone. If you have multiple audio devices:

1. Run the setup script to see available devices
2. The application will automatically select a microphone device
3. If no microphone is found, it will use the default input device

## Display Modes

- **Black Screen**: No music detected (silence)
- **White Screen**: Music detected but not identified
- **Full-Screen Album Art**: Music successfully identified

## Keyboard Controls

- `Escape`: Exit full-screen mode
- `F11`: Enter full-screen mode
- `Q`: Quit application

## Troubleshooting

### "Python is not installed"
- Download and install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

### "Failed to install PyAudio"
- Try: `pip install pipwin` then `pipwin install pyaudio`
- Or download PyAudio wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### "No audio devices found"
- Check that your microphone is connected and working
- Run Windows Audio Troubleshooter
- Check microphone permissions in Windows Settings

### "No music identified"
- Ensure you have a stable internet connection
- Try playing music louder
- Check that the music is recognizable (not too obscure)

### GUI Issues
- If the GUI doesn't appear, try running: `python -c "import tkinter; print('GUI available')"`
- Make sure you're not running in a headless environment

## File Structure

```
Musico/
├── Musico_windows.py      # Main Windows application
├── setup_windows.bat      # Windows setup script
├── run_windows.bat        # Windows run script
├── requirements_windows.txt # Windows dependencies
├── README_Windows.md      # This file
└── music_env/            # Virtual environment (created by setup)
```

## Technical Details

- **Audio Format**: 16-bit, 44.1kHz, mono
- **Recording Duration**: 2 seconds per sample
- **Silence Threshold**: 0.0002 RMS
- **Sample Interval**: 60 seconds between recordings
- **GUI Framework**: Tkinter (included with Python)

## Support

For issues specific to Windows:
1. Check that all requirements are installed
2. Verify your audio device is working
3. Ensure you have internet connectivity
4. Check the `musico.log` file for detailed error messages

## License

This project is open source. See the main README for license details.
