@echo off
echo Musico Windows Test
echo ==================
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

echo Testing Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not working
    pause
    exit /b 1
)

echo.
echo Testing audio devices...
python select_input_windows.py
if errorlevel 1 (
    echo ERROR: Audio test failed
    pause
    exit /b 1
)

echo.
echo Testing GUI...
python -c "import tkinter; print('GUI test: PASSED')"
if errorlevel 1 (
    echo ERROR: GUI test failed
    pause
    exit /b 1
)

echo.
echo Testing Shazam API...
python -c "from shazamio import Shazam; print('Shazam test: PASSED')"
if errorlevel 1 (
    echo ERROR: Shazam test failed
    pause
    exit /b 1
)

echo.
echo All tests passed! Musico is ready to run.
echo.
pause
