@echo off
REM NeuroHub Startup Script for Windows
echo 🚀 Starting NeuroHub - The AI Package Manager
echo ==============================================

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16+ and try again.
    pause
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm and try again.
    pause
    exit /b 1
)

echo ✅ Node.js and npm are available

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
) else (
    echo ✅ Dependencies already installed
)

REM Create uploads directory if it doesn't exist
if not exist "uploads" (
    mkdir uploads
    echo ✅ Created uploads directory
)

echo.
echo 🌟 Starting NeuroHub services...
echo.

REM Start the backend server
echo 🔧 Starting backend API server...
start "NeuroHub Backend" cmd /k "npm start"

REM Wait a moment for the server to start
timeout /t 3 /nobreak >nul

echo ✅ Backend API server started
echo 📊 API available at: http://localhost:3001/api/v1

REM Start the frontend server
echo 🌐 Starting frontend server...
start "NeuroHub Frontend" cmd /k "npm run frontend"

timeout /t 2 /nobreak >nul

echo ✅ Frontend server started
echo 🌐 Frontend available at: http://localhost:8080

echo.
echo 🎉 NeuroHub is now running!
echo ================================
echo Frontend:  http://localhost:8080
echo API:       http://localhost:3001/api/v1
echo Health:    http://localhost:3001/api/health
echo.
echo Press any key to open NeuroHub in your browser...
pause >nul

REM Open NeuroHub in default browser
start http://localhost:8080

echo.
echo NeuroHub is running in separate windows.
echo Close those windows to stop the services.
pause
