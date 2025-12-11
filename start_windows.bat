@echo off
title Quantum Autonomous Agent
echo [System] Waking up the Agent...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python is not installed or not in PATH.
    echo Please download and install Python 3.10+ from https://www.python.org/downloads/
    echo Important: Check the box "Add Python to PATH" during installation.
    pause
    exit
)

:: Install dependencies
echo [System] Verifying Neural and Quantum dependencies...
pip install -r ai_core/requirements.txt
if %errorlevel% neq 0 (
    echo [Error] Failed to install dependencies. Check your internet connection.
    pause
    exit
)

:: Run the AI
echo [System] Dependencies OK. Starting Life Loop...
echo.
python -m ai_core.main

pause
