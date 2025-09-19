@echo off
echo Musico Windows Setup
echo ===================
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

REM Install requirements
echo Installing Python packages...
pip install -r requirements_windows.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo.

REM Test audio devices
echo Testing audio devices...
python -c "import pyaudio; p = pyaudio.PyAudio(); print('Available audio devices:'); [print(f'  {i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels'] > 0]; p.terminate()"
echo.

echo Setup completed successfully!
echo.
echo To run Musico, double-click 'run_windows.bat' or run:
echo   run_windows.bat
echo.
echo To exit fullscreen mode, press Escape or F11
echo To quit the application, press Q
echo.
pause
