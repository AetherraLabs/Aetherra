@echo off
echo ========================================
echo FORCE BROWSER CACHE CLEAR
echo ========================================
echo.

echo This will help clear any stubborn browser cache issues.
echo.

echo [Method 1] Clear browser cache completely:
echo.
echo Chrome:
echo 1. Press Ctrl+Shift+Delete
echo 2. Select "All time" 
echo 3. Check "Cached images and files"
echo 4. Check "Cookies and other site data"
echo 5. Click "Clear data"
echo.

echo Firefox:
echo 1. Press Ctrl+Shift+Delete
echo 2. Select "Everything"
echo 3. Check "Cache" and "Cookies"
echo 4. Click "Clear Now"
echo.

echo Edge:
echo 1. Press Ctrl+Shift+Delete
echo 2. Select "All time"
echo 3. Check "Cached images and files"
echo 4. Click "Clear now"
echo.

echo [Method 2] Test with timestamp parameter:
echo Try opening: website\index.html?v=%random%
echo This forces the browser to treat it as a new file.
echo.

echo [Method 3] Test in different browser:
echo If you're using Chrome, try Firefox or Edge
echo.

echo [Method 4] Test direct file path:
echo Right-click website\index.html and "Open with" your browser
echo.

echo ========================================
echo The file currently shows correct links:
findstr /n "btn btn-secondary" website\index.html
echo ========================================
pause
