@echo off
REM NeuroCode Project Overview - Quick Access Script
REM Usage: overview.bat [update] [view] [stats]

cd /d "%~dp0"

if "%1"=="update" (
    echo 🔄 Updating project overview...
    python scripts\update_overview.py
    goto :end
)

if "%1"=="stats" (
    echo 📊 Showing project statistics...
    python scripts\view_overview.py --stats-only
    goto :end
)

if "%1"=="full" (
    echo 📖 Showing full overview...
    python scripts\view_overview.py --full
    goto :end
)

REM Default action - show quick view
echo 🧬 NeuroCode Project Overview
python scripts\view_overview.py

:end
echo.
echo 💡 Commands:
echo    overview.bat         - Quick view (default)
echo    overview.bat update  - Update overview data
echo    overview.bat stats   - Statistics only
echo    overview.bat full    - Complete overview
