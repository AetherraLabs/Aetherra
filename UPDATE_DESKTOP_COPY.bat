@echo off
REM Quick script to update the Desktop copy with the fixed executable

echo.
echo ============================================================
echo  Aetherra OS - Update Desktop Copy
echo ============================================================
echo.

set "SOURCE=dist-packages\AetherraOS-1.0.0-beta.1-Windows-x64"
set "DEST=%USERPROFILE%\Desktop\AetherraOS\AetherraOS-1.0.0-beta.1-Windows-x64"

echo [1/2] Checking source files...
if not exist "%SOURCE%\AetherraOS.exe" (
    echo [ERROR] Source files not found: %SOURCE%
    pause
    exit /b 1
)
echo [OK] Source files found

echo.
echo [2/2] Copying updated files to Desktop...
xcopy "%SOURCE%\*" "%DEST%\" /E /I /Y >nul 2>&1

if %ERRORLEVEL% == 0 (
    echo [OK] Desktop copy updated successfully!
    echo.
    echo ============================================================
    echo  UPDATE COMPLETE
    echo ============================================================
    echo.
    echo The fixed executable has been copied to your Desktop.
    echo You can now launch Aetherra OS from the Desktop folder.
    echo.
) else (
    echo [ERROR] Copy failed. Error code: %ERRORLEVEL%
    echo.
    echo Try manually copying:
    echo   FROM: %SOURCE%
    echo   TO:   %DEST%
    echo.
)

pause
