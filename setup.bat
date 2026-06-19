@echo off
:: Force UTF-8 to prevent charmap errors with Bengali/Hindi characters
set PYTHONUTF8=1
chcp 65001 >nul 2>&1

echo ============================================================
echo  Suto Cafe AI Marketing Platform -- PoC Setup (Windows)
echo ============================================================
echo.

:: Detect Python — try py launcher first, then python, then python3
set PYTHON_CMD=
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :found_python
)
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :found_python
)
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :found_python
)

echo.
echo [ERROR] Python not found on this machine.
echo.
echo  Please install Python 3.11+ from:
echo    https://www.python.org/downloads/
echo.
echo  IMPORTANT during install:
echo    Check the box "Add Python to PATH"
echo    Then re-run this setup.bat
echo.
pause & exit /b 1

:found_python
for /f "tokens=*" %%v in ('%PYTHON_CMD% --version 2^>^&1') do echo [OK] Found: %%v

:: Create virtual environment
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv. Try: %PYTHON_CMD% -m pip install virtualenv
        pause & exit /b 1
    )
)
echo [OK] Virtual environment ready

:: Activate and install
echo [INFO] Installing dependencies (this takes 1-2 minutes)...
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARN] Some packages may have had issues. Trying again verbosely...
    pip install -r requirements.txt
)

:: Copy .env if missing
if not exist ".env" (
    copy .env.example .env
    echo [INFO] Created .env -- please add your API keys
) else (
    echo [OK] .env already exists
)

echo.
echo ============================================================
echo  Setup complete!
echo.
echo  NEXT STEPS:
echo  1. Edit .env and add your free API keys:
echo     - GROQ_API_KEY  (free at console.groq.com)
echo     - OPENWEATHER_API_KEY  (free at openweathermap.org)
echo     OR set DEMO_MODE=true to skip API keys entirely
echo.
echo  2. Run the app:
echo     venv\Scripts\activate
echo     streamlit run app.py
echo.
echo  3. Open browser at: http://localhost:8501
echo ============================================================
pause
