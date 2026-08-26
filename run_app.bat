@echo off
setlocal
cd /d "%~dp0"

REM Create the local virtual environment on the first run.
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    where py >nul 2>nul
    if %ERRORLEVEL% == 0 (
        py -3 -m venv .venv
    ) else (
        where python >nul 2>nul
        if %ERRORLEVEL% == 0 (
            python -m venv .venv
        ) else (
            echo.
            echo Python was not found. Install Python from https://www.python.org/downloads/
            echo During installation, select "Add Python to PATH".
            pause
            exit /b 1
        )
    )
    if errorlevel 1 (
        echo.
        echo Failed to create the virtual environment.
        pause
        exit /b 1
    )
)

REM Install project packages only when Streamlit has not yet been installed.
if not exist ".venv\Scripts\streamlit.exe" (
    echo Installing project dependencies. This may take a few minutes on the first run...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Installation failed. Check your internet connection and try again.
        pause
        exit /b 1
    )
)

echo Starting AI Resume Screening System...
".venv\Scripts\python.exe" -m streamlit run app.py
pause
