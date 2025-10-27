param(
    [int]$Port = 3030
)

# Resolve the project root and daemon script path
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DaemonScript = Join-Path $ProjectRoot "aetherra_registry_daemon.py"

Write-Host "Starting Aetherra Registry Daemon at port $Port"
Write-Host "Script: $DaemonScript"

# Launch the daemon
python "$DaemonScript" --port $Port
