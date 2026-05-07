@echo off
REM SPDX-FileCopyrightText: 2026 SAP Engagement Cloud
REM SPDX-License-Identifier: MIT
REM
REM Launcher for Loyalty CSV Verifier (Windows)
REM Usage: double-click or run from cmd

setlocal enabledelayedexpansion

REM --- Change to the script's own directory so src.* imports resolve ---
cd /d "%~dp0"

REM -----------------------------------------------------------------------
REM Locate Python 3
REM Priority: py launcher -> python -> python3
REM -----------------------------------------------------------------------
set PYTHON=
set PY3FLAG=

REM 1. Windows Python Launcher (most reliable)
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py
    set PY3FLAG=-3
    goto :found_python
)

REM 2. 'python' command - verify it is Python 3
python --version >nul 2>&1
if not errorlevel 1 (
    python -c "import sys; exit(0 if sys.version_info.major==3 else 1)" >nul 2>&1
    if not errorlevel 1 (
        set PYTHON=python
        set PY3FLAG=
        goto :found_python
    )
)

REM 3. 'python3' command
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=python3
    set PY3FLAG=
    goto :found_python
)

REM -----------------------------------------------------------------------
REM Python not found - attempt auto-install via winget
REM -----------------------------------------------------------------------
echo Python 3 not found. Attempting automatic installation...
echo.

where winget >nul 2>&1
if errorlevel 1 (
    echo winget is not available on this system.
    echo Please download and install Python 3 manually:
    echo   https://www.python.org/downloads/
    echo When installing, check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

echo Refreshing winget sources...
winget source refresh --disable-interactivity >nul 2>&1

REM Try Python versions newest-first until one succeeds
set INSTALLED=0
for %%v in (3.13 3.12 3.11 3.10) do (
    if "!INSTALLED!"=="0" (
        echo Trying Python %%v...
        winget install --id Python.Python.%%v --accept-source-agreements --accept-package-agreements --disable-interactivity
        if not errorlevel 1 set INSTALLED=1
    )
)

if "!INSTALLED!"=="0" (
    echo.
    echo Automatic installation failed. Please download Python 3 manually:
    echo   https://www.python.org/downloads/
    echo When installing, check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

REM The py launcher reads from the Windows registry - no PATH refresh needed
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py
    set PY3FLAG=-3
    goto :found_python
)

REM Scan common install locations as fallback
for %%p in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
) do (
    if exist %%p (
        set PYTHON=%%p
        set PY3FLAG=
        goto :found_python
    )
)

echo.
echo Python was installed but cannot be detected in this session.
echo Please close this window and run the script again.
echo.
pause
exit /b 1

:found_python
for /f "tokens=*" %%v in ('%PYTHON% %PY3FLAG% --version 2^>^&1') do echo Using %%v

REM -----------------------------------------------------------------------
REM Create virtual environment if it does not exist
REM -----------------------------------------------------------------------
set VENV_DIR=%~dp0.venv-web
set VENV_PYTHON=%VENV_DIR%\Scripts\python.exe

if not exist "%VENV_PYTHON%" (
    echo Creating virtual environment...
    %PYTHON% %PY3FLAG% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to create virtual environment.
        echo Try running this script from a folder without special characters in its path.
        echo.
        pause
        exit /b 1
    )
    echo Virtual environment created.
)

REM -----------------------------------------------------------------------
REM Install Flask into the venv if missing
REM -----------------------------------------------------------------------
"%VENV_PYTHON%" -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing flask...
    "%VENV_PYTHON%" -m pip install flask
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install flask. Check your internet connection.
        echo.
        pause
        exit /b 1
    )
    echo Dependencies installed.
)

REM -----------------------------------------------------------------------
REM Launch server
REM -----------------------------------------------------------------------
echo Starting Loyalty CSV Verifier...
"%VENV_PYTHON%" "%~dp0server.py"

REM Keep window open if server exits with an error
if errorlevel 1 (
    echo.
    echo Server stopped with an error. See above for details.
    pause
)

endlocal
