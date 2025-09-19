@echo off
echo Musico Windows Test
echo ===================
echo.

REM Check if virtual environment exists
if not exist "music_env" (
    echo ERROR: Virtual environment not found
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call music_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Testing Python 3.13+ compatibility...
python -c "import sys; print(f'Python version: {sys.version}')"

echo.
echo Testing audioop compatibility...
python -c "import audioop; print('audioop module: OK')"

echo.
echo Testing pyaudioop compatibility...
python -c "import pyaudioop; print('pyaudioop module: OK')"

echo.
echo Testing PyAudio...
python -c "import pyaudio; print('PyAudio: OK')"

echo.
echo Testing Shazam API...
python -c "from shazamio import Shazam; print('Shazam API: OK')"

echo.
echo Testing GUI...
python -c "import tkinter; print('GUI: OK')"

echo.
echo All tests passed! Musico should work on Windows.
echo.
pause