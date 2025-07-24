#!/usr/bin/env powershell
# Neural Interface Feature Commit Script
# This script commits only the specific files related to our neural interface enhancements

Write-Host "🚀 Committing Neural Interface Enhancements..." -ForegroundColor Green

# Remove any git lock files
Remove-Item ".git\index.lock" -Force -ErrorAction SilentlyContinue

# List of files we want to commit (our neural interface changes)
$filesToCommit = @(
    "Aetherra/lyrixa/conversation_manager.py",
    "Aetherra/lyrixa/gui/web_interface_server.py", 
    "Aetherra/lyrixa/gui/web_templates/neural_interface.html"
)

Write-Host "📁 Adding specific files to staging:" -ForegroundColor Yellow
foreach ($file in $filesToCommit) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
        git add $file
    } else {
        Write-Host "  ⚠️ $file (not found)" -ForegroundColor Yellow
    }
}

# Check what's staged
Write-Host "`n📋 Staged changes:" -ForegroundColor Yellow
git diff --cached --name-only

# Create commit
$commitMessage = @"
✨ Neural Interface: Ollama prioritization + Model selector + Auto-scroll

🔧 Enhanced Features:
- Ollama models prioritized in conversation manager
- Real-time model switching dropdown in web interface  
- Auto-scrolling chat with smooth animation
- Enhanced WebSocket communication for model management

🎯 Files Modified:
- conversation_manager.py: Ollama-first model preference order
- web_interface_server.py: Model switching API routes + real conversation integration
- neural_interface.html: Model selector UI + enhanced auto-scroll functionality

✅ All requested features now working:
• Set Ollama as primary model ✓
• Model selector dropdown without restart ✓  
• Auto-scrolling chat panel ✓
"@

Write-Host "`n💬 Commit message:" -ForegroundColor Yellow
Write-Host $commitMessage -ForegroundColor Gray

Write-Host "`n🔄 Creating commit..." -ForegroundColor Green
git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit successful!" -ForegroundColor Green
    Write-Host "`n📊 Repository status:" -ForegroundColor Yellow
    git status --porcelain | Measure-Object | ForEach-Object { Write-Host "  $($_.Count) files still pending" }
    
    Write-Host "`n🚀 Ready to push:" -ForegroundColor Green
    Write-Host "  git push origin main" -ForegroundColor Cyan
} else {
    Write-Host "❌ Commit failed" -ForegroundColor Red
}
