@echo off
title Pokemon Shiny Reset Bot Launcher

echo =======================================================
echo          Pokemon Shiny Reset Bot - Launcher      
echo =======================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Python is not installed or not in PATH!
    echo.
    set /p install_py="Do you want to download and install Python now? (Y/N): "
    if /i "%install_py%"=="Y" (
        echo [INFO] Opening Python official download page...
        echo [IMPORTANT] Please check the "Add python.exe to PATH" option during installation!
        start https://www.python.org/downloads/windows/
        pause
        echo Please close this window and run the script again after installation is complete.
    ) else (
        echo [EXIT] Cannot run the bot without Python.
    )
    pause
    exit /b
)

echo [OK] Python is installed.

:: 2. Check and Install Requirements
echo.
echo [INFO] Checking required libraries...

if not exist requirements.txt goto SKIP_INSTALL

set /p install_req="Do you want to install/update required libraries now? (Y/N): "
if /i not "%install_req%"=="Y" goto SKIP_INSTALL

echo.
echo [INFO] Installing libraries... (Already installed ones will be skipped)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo [OK] Required libraries installed/updated.

:SKIP_INSTALL

:: 3. Run Main Bot
echo.
echo =======================================================
echo [INFO] Starting the Main Bot Program...
echo =======================================================
ping 127.0.0.1 -n 2 > nul

python src\main.py

echo.
echo [EXIT] Program has ended.
pause
