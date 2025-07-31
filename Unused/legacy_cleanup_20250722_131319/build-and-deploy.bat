@echo off
echo 🚀 Building and deploying Aetherra website...
echo.

echo 📦 Step 1: Building website...
cd "Aetherra\lyrixa\core\Aetherra Website"
call npm run build
if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo 📁 Step 2: Copying to docs directory...
cd ..\..\..\..
cp -r "Aetherra\lyrixa\core\Aetherra Website\dist\*" "docs\" -Force

echo 🌐 Step 3: Committing and pushing...
git add .
git commit -m "Website update: rebuilt and deployed to docs/"
git push origin main

echo ✅ Website deployed successfully!
echo 📍 Visit: https://aetherra.dev
pause
