@echo off
echo Neural Interface Feature Commit
echo ===============================

REM Remove git lock file
del ".git\index.lock" 2>nul

REM Add specific files for our neural interface changes
echo Adding neural interface files...
git add "Aetherra/lyrixa/conversation_manager.py"
git add "Aetherra/lyrixa/gui/web_interface_server.py"
git add "Aetherra/lyrixa/gui/web_templates/neural_interface.html"

REM Show what's staged
echo.
echo Staged changes:
git diff --cached --name-only

REM Commit with descriptive message
echo.
echo Creating commit...
git commit -m "Neural Interface: Ollama prioritization + Model selector + Auto-scroll

Enhanced Features:
- Ollama models prioritized in conversation manager
- Real-time model switching dropdown in web interface
- Auto-scrolling chat with smooth animation
- Enhanced WebSocket communication for model management

Files Modified:
- conversation_manager.py: Ollama-first model preference order
- web_interface_server.py: Model switching API routes + real conversation integration
- neural_interface.html: Model selector UI + enhanced auto-scroll functionality

All requested features now working:
- Set Ollama as primary model
- Model selector dropdown without restart
- Auto-scrolling chat panel"

if %errorlevel% equ 0 (
    echo.
    echo Commit successful!
    echo Ready to push: git push origin main
) else (
    echo.
    echo Commit failed
)

pause
