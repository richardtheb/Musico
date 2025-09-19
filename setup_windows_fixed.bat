@echo off
echo Musico Windows Setup (Fixed for Python 3.13+)
echo =============================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo Python found!
echo.

REM Check Python version
echo Checking Python version compatibility...
python -c "import sys; version = sys.version_info; print(f'Python {version.major}.{version.minor}.{version.micro} detected')"
python -c "import sys; version = sys.version_info; exit(0 if version >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Python 3.8+ is recommended for best compatibility
    echo.
)

REM Create virtual environment
echo Creating virtual environment...
if exist "music_env" (
    echo Virtual environment already exists, removing old one...
    rmdir /s /q music_env
)

python -m venv music_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

REM Activate virtual environment
echo Activating virtual environment...
call music_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install wheel and setuptools first (helps with some packages)
echo Installing build tools...
pip install wheel setuptools
echo.

REM Install requirements with specific versions for better compatibility
echo Installing Python packages...
pip install numpy==1.24.3
pip install Pillow==10.0.0
pip install requests==2.31.0
pip install pyaudio==0.2.11
pip install shazamio==0.8.1

if errorlevel 1 (
    echo ERROR: Failed to install some packages
    echo This might be due to missing Visual C++ Build Tools
    echo.
    echo Please install Microsoft Visual C++ Build Tools from:
    echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
    echo.
    echo Then run this setup script again.
    pause
    exit /b 1
)
echo.

REM Test the compatibility modules
echo Testing Python 3.13+ compatibility modules...
python -c "import audioop; print('audioop compatibility: OK')"
python -c "import pyaudioop; print('pyaudioop compatibility: OK')"
echo.

REM Test audio devices
echo Testing audio devices...
python -c "import pyaudio; p = pyaudio.PyAudio(); print('Available audio devices:'); [print(f'  {i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels'] > 0]; p.terminate()"
echo.

REM Test GUI
echo Testing GUI...
python -c "import tkinter; print('GUI test: PASSED')"
if errorlevel 1 (
    echo ERROR: GUI test failed
    pause
    exit /b 1
)
echo.

REM Test Shazam
echo Testing Shazam API...
python -c "from shazamio import Shazam; print('Shazam test: PASSED')"
if errorlevel 1 (
    echo ERROR: Shazam test failed
    pause
    exit /b 1
)
echo.

echo Setup completed successfully!
echo.
echo To run Musico on Windows:
echo   run_windows.bat
echo.
echo To test the installation:
echo   test_windows.bat
echo.
echo To exit fullscreen mode, press Escape or F11
echo To quit the application, press Q
echo.
pause
