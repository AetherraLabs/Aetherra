@echo off
echo Smart Repository Cleanup Strategy
echo ==================================

echo Phase 1: Analyze the situation
git status --porcelain > temp_status.txt

echo.
echo Counting file types:
findstr /R "^D" temp_status.txt > deletions.txt
findstr /R "^M" temp_status.txt > modifications.txt
findstr /R "^??" temp_status.txt > untracked.txt

for /f %%i in ('type deletions.txt ^| find /c /v ""') do set /a deletions=%%i
for /f %%i in ('type modifications.txt ^| find /c /v ""') do set /a modifications=%%i
for /f %%i in ('type untracked.txt ^| find /c /v ""') do set /a untracked=%%i

echo   Deletions (D): %deletions%
echo   Modifications (M): %modifications%
echo   Untracked (??): %untracked%
echo.

echo Phase 2: RECOMMENDED APPROACH
echo ==============================
echo.
echo OPTION 1 (Conservative - Recommended):
echo   1. Stage ONLY the essential modified files we care about
echo   2. Commit those changes
echo   3. Deal with deletions in a separate cleanup commit
echo.
echo OPTION 2 (Aggressive):
echo   1. Stage ALL deletions (removes old backup files)
echo   2. Ignore untracked files for now
echo   3. Clean commit with everything
echo.

echo Phase 3: Essential files we should commit:
echo.
echo Key modified files to keep:
findstr /R "conversation_manager\|web_interface_server\|neural_interface\.html\|\.gitignore" modifications.txt
echo.

echo Phase 4: Safe deletions (old backups and temp files):
echo.
echo Sample files being deleted:
type deletions.txt | findstr /R "backup\|test_files\|archive" | head -10
echo ... (and many more backup/temp files)
echo.

:choice
echo.
set /p choice="Choose approach (1=Conservative, 2=Aggressive, 3=Show more details): "

if "%choice%"=="1" goto conservative
if "%choice%"=="2" goto aggressive
if "%choice%"=="3" goto details
goto choice

:conservative
echo.
echo CONSERVATIVE APPROACH - Staging essential files only...
echo.

REM Stage key files we definitely want
git add .gitignore
git add Aetherra/cli/plugin.py
git add Aetherra/lyrixa/agents/__init__.py
git add Aetherra/lyrixa/agents/core_agent.py
git add Aetherra/lyrixa/gui/__init__.py
git add Aetherra/lyrixa/intelligence/__init__.py

echo Staged essential modified files
git status --porcelain | findstr /R "^A"

set /p confirm="Commit these essential changes? (y/n): "
if "%confirm%"=="y" (
    git commit -m "Essential updates: Core agent fixes and module improvements

- Updated .gitignore for better file exclusions
- Enhanced CLI plugin functionality
- Improved agent initialization and core agent structure
- Updated GUI and intelligence module imports
- Prepared for neural interface deployment

Note: Backup file cleanup will follow in separate commit"
    echo.
    echo ✅ Essential changes committed!
    echo 📊 Remaining files: Still need cleanup of backup/temp files
)
goto end

:aggressive
echo.
echo AGGRESSIVE APPROACH - Cleaning up ALL deletions...
echo.
echo ⚠️  WARNING: This will delete %deletions% files (mostly backups and temp files)
echo.
set /p confirm="Are you sure? This will remove all backup directories (y/n): "
if "%confirm%"=="y" (
    echo Staging all deletions...
    git add -u
    echo.
    echo Staged all deletions and modifications
    git status --short
    echo.
    set /p commit_confirm="Commit massive cleanup? (y/n): "
    if "%commit_confirm%"=="y" (
        git commit -m "Major repository cleanup: Remove backup files and deprecated content

- Removed Aetherra_backup_20250712_184525/ directory
- Cleaned up archive/test_files/ directory
- Removed old documentation and temp files
- Eliminated duplicate .md files and old scripts
- Streamlined codebase for production readiness

This commit removes %deletions% deprecated files while preserving all active development work."
        echo.
        echo ✅ Massive cleanup committed!
    )
)
goto end

:details
echo.
echo DETAILED ANALYSIS:
echo ==================
echo.
echo Top deleted directories:
type deletions.txt | findstr /R "/$" | head -10
echo.
echo Top deleted file types:
type deletions.txt | findstr /R "\.md$" | head -5
type deletions.txt | findstr /R "\.py$" | head -5
type deletions.txt | findstr /R "\.json$" | head -5
echo.
goto choice

:end
echo.
echo Current repository status:
git status --porcelain | measure-object | findstr Count

echo.
echo Next steps:
echo 1. Push committed changes: git push origin main
echo 2. Handle any remaining files as needed
echo 3. Consider .gitignore updates for future

REM Cleanup temp files
del temp_status.txt deletions.txt modifications.txt untracked.txt 2>nul

pause
