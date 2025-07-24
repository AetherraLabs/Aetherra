@echo off
echo 🚀 AETHERRA PYTHON ENVIRONMENT SETUP
echo ====================================
echo.

echo 📝 Step 1: Creating virtual environment...
py -m venv .venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    echo 💡 Make sure Python is installed: py --version
    pause
    exit /b 1
)
echo ✅ Virtual environment created successfully!
echo.

echo 📦 Step 2: Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated!
echo.

echo 📥 Step 3: Installing required packages...
if exist requirements.txt (
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install requirements
        pause
        exit /b 1
    )
    echo ✅ Requirements installed successfully!
) else (
    echo ⚠️  No requirements.txt found, installing essential packages...
    pip install PySide6 requests python-dotenv fastapi uvicorn
    if %errorlevel% neq 0 (
        echo ❌ Failed to install essential packages
        pause
        exit /b 1
    )
    echo ✅ Essential packages installed!
)
echo.

echo 🎉 SETUP COMPLETE!
echo 💡 Your Python environment is ready for Aetherra
echo 🚀 You can now run: py aetherra_hybrid_launcher.py
echo.
pause
