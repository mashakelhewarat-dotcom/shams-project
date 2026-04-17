@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
color 0A
title Shams Al-Maarif v19 - Production Server

cls
echo.
echo  ============================================================
echo   SHAMS AL-MAARIF v19 - Production Grade Server
echo  ============================================================
echo.

:: ----------------------------------------------------------
:: STEP 1: Verify Python
:: ----------------------------------------------------------
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Python not found in PATH.
    echo  Install Python 3.9+ from https://python.org
    echo  Check "Add Python to PATH" during install!
    echo.
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% detected.

:: ----------------------------------------------------------
:: STEP 2: Working directory
:: ----------------------------------------------------------
echo [2/6] Setting working directory...
cd /d "%~dp0"
echo  [OK] %CD%

:: ----------------------------------------------------------
:: STEP 3: Virtual environment
:: ----------------------------------------------------------
echo [3/6] Virtual environment...
if not exist "venv\Scripts\activate.bat" (
    echo  Creating virtual environment (first time only)...
    python -m venv venv >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [WARNING] Cannot create venv, using system Python.
        set USE_VENV=0
    ) else (
        set USE_VENV=1
    )
) else (
    set USE_VENV=1
)

if "%USE_VENV%"=="1" (
    call venv\Scripts\activate.bat >nul 2>&1
    echo  [OK] Virtual environment ready.
)

:: ----------------------------------------------------------
:: STEP 4: Install requirements
:: ----------------------------------------------------------
echo [4/6] Installing requirements...
if exist "requirements.txt" (
    echo  Installing packages (may take a minute on first run)...
    pip install -r requirements.txt --quiet --disable-pip-version-check > pip_log.txt 2>&1
    if %errorlevel% neq 0 (
        echo  [WARNING] Some packages failed - see pip_log.txt
    ) else (
        del pip_log.txt >nul 2>&1
        echo  [OK] All packages installed.
    )
)

:: ----------------------------------------------------------
:: STEP 5: .env file
:: ----------------------------------------------------------
echo [5/6] Environment config...
if not exist ".env" (
    (
        echo FLASK_ENV=production
        echo FLASK_DEBUG=0
        echo HOST=0.0.0.0
        echo PORT=5000
        echo SECRET_KEY=shams-v19-key
        echo LATITUDE=30.0444
        echo LONGITUDE=31.2357
        echo ELEVATION=0
        echo GEMINI_API_KEY=
        echo LICENSE_KEY=
    ) > .env
    echo  [OK] .env created.
) else (
    echo  [OK] .env found.
)

:: ----------------------------------------------------------
:: STEP 6: Quick Python import test
:: ----------------------------------------------------------
echo [6/6] Testing Python environment...
python -c "import flask; import psutil" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Critical packages missing.
    echo  Running emergency install...
    pip install flask psutil python-dotenv --quiet
)

echo  [OK] Environment ready.
echo.

:: ----------------------------------------------------------
:: LAUNCH
:: ----------------------------------------------------------
echo  ============================================================
echo   Starting server at http://localhost:5000
echo   DO NOT close this window while using the app!
echo   Press Ctrl+C to stop.
echo  ============================================================
echo.

:: Open browser AFTER server starts (5 second delay)
start /b "" cmd /c "timeout /t 5 >nul && start http://localhost:5000"

:: Start server - show ALL errors if it crashes
python app.py

:: If we reach here, server stopped or crashed
echo.
echo  ============================================================
if %errorlevel% neq 0 (
    color 0C
    echo   [ERROR] Server crashed! Reading error...
    echo  ============================================================
    echo.
    echo  Running diagnostic to find the problem:
    python -c "import app" 2>&1
) else (
    echo   Server stopped normally.
)
echo  ============================================================
echo.
echo  If you see an error above, copy it and send it for support.
echo.

if "%USE_VENV%"=="1" (
    call venv\Scripts\deactivate.bat >nul 2>&1
)
pause
endlocal
