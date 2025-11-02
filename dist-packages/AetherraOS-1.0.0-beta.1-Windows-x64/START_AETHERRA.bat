@echo off
REM Aetherra OS - Quick Start Launcher for Windows
REM This script starts Aetherra OS and keeps the console window open

echo.
echo ============================================================
echo  AETHERRA AI OPERATING SYSTEM - LAUNCHER
echo ============================================================
echo.

REM Check if executable exists
if not exist "AetherraOS.exe" (
    echo [ERROR] AetherraOS.exe not found!
    echo.
    echo Please run this from the AetherraOS folder.
    echo.
    pause
    exit /b 1
)

echo [LAUNCH] Starting Aetherra OS...
echo.
echo Mode: Full AI Operating System
echo.
echo ============================================================
echo  SYSTEM IS STARTING - PLEASE WAIT
echo ============================================================
echo.

REM Start the executable with GUI mode
AetherraOS.exe --mode full --gui

REM If the process exits, show this message
echo.
echo ============================================================
echo  AETHERRA OS HAS STOPPED
echo ============================================================
echo.
echo The system has shut down.
echo.
pause
