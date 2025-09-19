# Musico Windows Installation Guide

## Prerequisites

### 1. Python Installation
- Download Python from https://python.org
- **IMPORTANT**: Check "Add Python to PATH" during installation
- Recommended: Python 3.8 or later

### 2. Audio Requirements
- Working microphone or audio input device
- Windows audio drivers installed
- Microphone permissions enabled

## Installation Steps

### Method 1: Automatic Installation (Recommended)

1. **Download Musico**: Extract all files to a folder (e.g., `C:\Musico`)

2. **Run Setup**: Double-click `setup_windows.bat`
   - This will create a virtual environment
   - Install all required Python packages
   - Test your audio devices

3. **Test Installation**: Double-click `test_windows.bat`
   - Verifies all components are working
   - Tests audio recording
   - Tests GUI functionality

4. **Run Musico**: Double-click `run_windows.bat`
   - Starts the full-screen music identification app

### Method 2: Manual Installation

1. **Open Command Prompt as Administrator**
   - Press `Win + R`, type `cmd`, press `Ctrl + Shift + Enter`

2. **Navigate to Musico folder**
   ```cmd
   cd C:\Musico
   ```

3. **Create virtual environment**
   ```cmd
   python -m venv music_env
   ```

4. **Activate virtual environment**
   ```cmd
   music_env\Scripts\activate.bat
   ```

5. **Install requirements**
   ```cmd
   pip install -r requirements.txt
   ```

6. **Test audio devices**
   ```cmd
   python select_input_windows.py
   ```

7. **Run Musico**
   ```cmd
   python Musico_windows.py
   ```

## Troubleshooting

### Common Issues

#### "Python is not recognized"
- **Solution**: Reinstall Python and check "Add Python to PATH"
- **Alternative**: Add Python to PATH manually in System Environment Variables

#### "Failed to install PyAudio"
- **Solution 1**: Install Microsoft Visual C++ Build Tools
- **Solution 2**: Use pipwin:
  ```cmd
  pip install pipwin
  pipwin install pyaudio
  ```
- **Solution 3**: Download PyAudio wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

#### "No audio devices found"
- **Solution 1**: Check microphone is connected and enabled
- **Solution 2**: Run Windows Audio Troubleshooter
- **Solution 3**: Check microphone permissions in Windows Settings > Privacy > Microphone

#### "GUI not working"
- **Solution 1**: Test GUI: `python -c "import tkinter; print('OK')"`
- **Solution 2**: Update graphics drivers
- **Solution 3**: Try running in windowed mode first

#### "Music not identified"
- **Solution 1**: Check internet connection
- **Solution 2**: Play music louder
- **Solution 3**: Try different music (some songs may not be in Shazam database)

### Advanced Troubleshooting

#### Check Python Installation
```cmd
python --version
python -c "import sys; print(sys.executable)"
```

#### Check Audio Devices
```cmd
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)['name']}') for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels'] > 0]; p.terminate()"
```

#### Check Dependencies
```cmd
python -c "import pyaudio, numpy, shazamio, PIL, requests, tkinter; print('All dependencies OK')"
```

#### Test Audio Recording
```cmd
python -c "import pyaudio, numpy; p = pyaudio.PyAudio(); stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024); data = stream.read(1024); stream.close(); p.terminate(); print('Audio recording OK')"
```

## File Structure

```
Musico/
├── Musico_windows.py          # Main Windows application
├── setup_windows.bat          # Windows setup script
├── run_windows.bat            # Windows run script
├── test_windows.bat           # Windows test script
├── select_input_windows.py    # Audio device selector
├── requirements.txt           # Cross-platform requirements
├── requirements_windows.txt   # Windows-specific requirements
├── README_Windows.md          # Windows documentation
├── INSTALL_Windows.md         # This installation guide
└── music_env/                 # Virtual environment (created by setup)
```

## Usage

### Running Musico
- **Full Screen**: Double-click `run_windows.bat`
- **Command Line**: `python Musico_windows.py`

### Controls
- `Escape`: Exit full-screen mode
- `F11`: Enter full-screen mode  
- `Q`: Quit application

### Display Modes
- **Black Screen**: No music detected (silence)
- **White Screen**: Music detected but not identified
- **Full-Screen Album Art**: Music successfully identified

## Support

If you encounter issues:
1. Check the `musico.log` file for detailed error messages
2. Run `test_windows.bat` to verify all components
3. Ensure all prerequisites are met
4. Check Windows audio and microphone settings

## Uninstallation

To remove Musico:
1. Delete the Musico folder
2. The virtual environment will be removed with the folder
3. No system files are modified during installation
