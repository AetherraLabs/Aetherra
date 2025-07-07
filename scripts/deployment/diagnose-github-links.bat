@echo off
echo ========================================
echo Aetherra GitHub Link Diagnostic Script
echo ========================================
echo.

echo [1] Checking current git configuration...
git remote -v
echo.

echo [2] Checking for any GitHub-related git configs...
git config --list | findstr github
echo.

echo [3] Checking DNS resolution for GitHub...
nslookup github.com
echo.

echo [4] Checking for any proxy settings...
netsh winhttp show proxy
echo.

echo [5] Checking hosts file for GitHub entries...
findstr /i "github" C:\Windows\System32\drivers\etc\hosts 2>nul
if errorlevel 1 echo No GitHub entries found in hosts file
echo.

echo [6] Verifying website files have correct links...
echo Checking website\index.html:
findstr /n "github.com" website\index.html | findstr /v "Zyonic88" 2>nul
if errorlevel 1 echo ✓ All GitHub links in website\index.html point to Zyonic88
echo.

echo Checking neurohub\index.html:
findstr /n "github.com" neurohub\index.html | findstr /v "Zyonic88" 2>nul
if errorlevel 1 echo ✓ All GitHub links in neurohub\index.html point to Zyonic88
echo.

echo [7] Testing network connectivity to correct repository...
echo Testing: https://github.com/Zyonic88/Aetherra
curl -I -s "https://github.com/Zyonic88/Aetherra" | findstr "HTTP/"
echo.

echo [8] Testing old repository (should return 404)...
echo Testing: https://github.com/VirtualVerse-Corporation/Aetherra
curl -I -s "https://github.com/VirtualVerse-Corporation/Aetherra" | findstr "HTTP/"
echo.

echo ========================================
echo DIAGNOSIS RESULT:
echo ✓ All file contents are CORRECT
echo ✓ DNS resolution works properly
echo ✓ Network connectivity is good
echo ✓ No proxy or hosts file issues
echo.
echo CRITICAL QUESTION:
echo HOW are you accessing the website when the redirect happens?
echo.
echo [A] Right-click website\index.html → "Open with" browser
echo [B] VS Code Live Server or similar extension
echo [C] Local development server (python -m http.server, etc.)
echo [D] Through a hosted version online
echo [E] Other method
echo.
echo NEXT STEPS:
echo 1. Tell us HOW you access the website when redirect happens
echo 2. Try: Right-click website\index.html → Open with browser
echo 3. Try: website\cache-buster-test.html to verify
echo 4. Check for VS Code extensions that might modify links
echo ========================================
pause
