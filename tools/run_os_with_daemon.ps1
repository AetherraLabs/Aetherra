param(
    [string]$DaemonUrl = "http://127.0.0.1:3030"
)

# Set env var for this process and its children
$env:AETHERRA_REGISTRY_URL = $DaemonUrl
Write-Host "AETHERRA_REGISTRY_URL=$env:AETHERRA_REGISTRY_URL"

# Compute project root and launcher path
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Launcher = Join-Path $ProjectRoot "aetherra_os_launcher.py"

# Run the OS launcher
python "$Launcher" --mode full -v
