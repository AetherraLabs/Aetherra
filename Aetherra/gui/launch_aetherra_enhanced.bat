@echo off
REM Aetherra OS Enhanced Neural Dashboard Launcher
REM ==============================================

echo 🌌 Aetherra OS - Enhanced Neural Processing Dashboard
echo ================================================
echo.
echo ✨ Launching unified neural interface with:
echo    🧠 Pulsating Neural Web Background
echo    ⚛️ Animated Quantum Core
echo    🗺️ Live Memory Graph Integration
echo    📜 Consciousness Timeline
echo    🔬 Introspective Diagnostics
echo    ⚙️ Plugin Aura Viewer
echo    🔮 Synthetic Soul Metrics
echo    💤 Dream State Mode
echo    ⌨️ Command Palette (Ctrl+K)
echo.

cd /d "%~dp0"
python launch_enhanced_neural_os.py

if errorlevel 1 (
    echo.
    echo ❌ Error launching Aetherra OS
    echo Make sure Python and PySide6 are installed:
    echo    pip install PySide6 numpy
    pause
)
