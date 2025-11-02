# Quick Exe Builder for Aetherra OS
# Simplified version for testing

Write-Host "Building Aetherra OS executable..." -ForegroundColor Cyan
Write-Host ""

# Set production environment
$env:AETHERRA_PROFILE = "prod"
$env:PYTHONIOENCODING = "utf-8"

# Build command
$cmd = @(
    "pyinstaller",
    "--onedir",
    "--name", "AetherraOS",
    "--noconfirm",
    "--clean",
    "--add-data", ".env.example;.",
    "--add-data", "config.json;.",
    "--hidden-import", "aetherra_kernel_loop",
    "--hidden-import", "aetherra_service_registry",
    "--hidden-import", "flask",
    "--hidden-import", "flask_socketio",
    "--hidden-import", "openai",
    "--collect-all", "Aetherra",
    "aetherra_os_launcher.py"
)

Write-Host "Running: $($cmd -join ' ')" -ForegroundColor Gray
Write-Host ""

& $cmd[0] $cmd[1..($cmd.Length - 1)]

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Build complete!" -ForegroundColor Green
    Write-Host "Executable: dist\AetherraOS\AetherraOS.exe" -ForegroundColor Cyan
}
else {
    Write-Host ""
    Write-Host "[ERROR] Build failed with code $LASTEXITCODE" -ForegroundColor Red
}
