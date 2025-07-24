# Smart Git Cleanup for Aetherra Repository
# ==========================================

Write-Host "Aetherra Repository Cleanup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Get current status
$allFiles = git status --porcelain

# Categorize files
$deletions = $allFiles | Where-Object { $_ -match "^ D " }
$modifications = $allFiles | Where-Object { $_ -match "^ M " }
$untracked = $allFiles | Where-Object { $_ -match "^\?\?" }

Write-Host "`nRepository Analysis:" -ForegroundColor Yellow
Write-Host "  Deletions: $($deletions.Count)" -ForegroundColor Red
Write-Host "  Modifications: $($modifications.Count)" -ForegroundColor Yellow  
Write-Host "  Untracked: $($untracked.Count)" -ForegroundColor Cyan

Write-Host "`nStrategy Options:" -ForegroundColor Yellow
Write-Host "1. Conservative: Stage only essential modifications" -ForegroundColor Green
Write-Host "2. Moderate: Stage modifications + safe deletions" -ForegroundColor Yellow
Write-Host "3. Aggressive: Clean everything (stage all changes)" -ForegroundColor Red
Write-Host "4. Analysis: Show detailed breakdown" -ForegroundColor Cyan

$choice = Read-Host "`nChoose strategy (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`nCONSERVATIVE APPROACH" -ForegroundColor Green
        Write-Host "Staging only essential modifications..." -ForegroundColor Yellow
        
        # Stage key modified files
        git add .gitignore 2>$null
        if (Test-Path "Aetherra/cli/plugin.py") { git add "Aetherra/cli/plugin.py" }
        if (Test-Path "Aetherra/lyrixa/agents/__init__.py") { git add "Aetherra/lyrixa/agents/__init__.py" }
        if (Test-Path "Aetherra/lyrixa/agents/core_agent.py") { git add "Aetherra/lyrixa/agents/core_agent.py" }
        if (Test-Path "Aetherra/lyrixa/gui/__init__.py") { git add "Aetherra/lyrixa/gui/__init__.py" }
        if (Test-Path "Aetherra/lyrixa/intelligence/__init__.py") { git add "Aetherra/lyrixa/intelligence/__init__.py" }
        
        Write-Host "`nStaged files:" -ForegroundColor Yellow
        git diff --cached --name-only
        
        $confirm = Read-Host "`nCommit these essential changes? (y/n)"
        if ($confirm -eq "y") {
            git commit -m "Essential core updates: Agent and module improvements"
            Write-Host "Essential changes committed!" -ForegroundColor Green
        }
    }
    
    "2" {
        Write-Host "`nMODERATE APPROACH" -ForegroundColor Yellow
        Write-Host "Staging modifications and safe deletions..." -ForegroundColor Yellow
        
        # Stage all modifications and deletions (but not untracked)
        git add -u
        
        Write-Host "`nFiles to be committed:" -ForegroundColor Yellow
        $staged = git diff --cached --name-status
        Write-Host "Total files staged: $($staged.Count)"
        
        $confirm = Read-Host "`nCommit these changes? (y/n)"
        if ($confirm -eq "y") {
            git commit -m "Repository cleanup: Remove deprecated files and update core modules"
            Write-Host "Moderate cleanup committed!" -ForegroundColor Green
        }
    }
    
    "3" {
        Write-Host "`nAGGRESSIVE APPROACH" -ForegroundColor Red
        Write-Host "WARNING: This will stage ALL files including untracked ones!" -ForegroundColor Red
        
        $confirm = Read-Host "Are you sure? This adds $($untracked.Count) new files (y/n)"
        if ($confirm -eq "y") {
            git add .
            
            Write-Host "`nMassive commit preview:" -ForegroundColor Yellow
            $staged = git diff --cached --name-status
            Write-Host "Total files to commit: $($staged.Count)"
            
            $finalConfirm = Read-Host "Proceed with massive commit? (y/n)"
            if ($finalConfirm -eq "y") {
                git commit -m "Major repository consolidation: Complete codebase cleanup"
                Write-Host "Massive cleanup committed!" -ForegroundColor Green
            }
        }
    }
    
    "4" {
        Write-Host "`nDETAILED ANALYSIS" -ForegroundColor Cyan
        
        Write-Host "`nSample deleted files:" -ForegroundColor Red
        $deletions | Select-Object -First 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        
        Write-Host "`nModified files:" -ForegroundColor Yellow
        $modifications | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        
        Write-Host "`nSample untracked files:" -ForegroundColor Cyan
        $untracked | Select-Object -First 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
        
        Write-Host "`nRun script again to choose cleanup strategy." -ForegroundColor Green
    }
    
    default {
        Write-Host "Invalid choice. Run script again." -ForegroundColor Red
    }
}

Write-Host "`nFinal Status:" -ForegroundColor Yellow
$remaining = git status --porcelain
Write-Host "Remaining pending files: $($remaining.Count)" -ForegroundColor Cyan

if ($remaining.Count -eq 0) {
    Write-Host "Repository is clean! Ready to push:" -ForegroundColor Green
    Write-Host "   git push origin main" -ForegroundColor Cyan
}
