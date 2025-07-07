# Aetherra Project Protection Manager
# PowerShell script for managing project file protection

param(
    [Parameter(Position = 0)]
    [string]$Command = "help",

    [Parameter(Position = 1)]
    [string]$FilePath = "",

    [Parameter(Position = 2)]
    [string]$Reason = "Manual operation"
)

function Show-Help {
    Write-Host "Aetherra Project Protection Manager" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  status           - Show protection status"
    Write-Host "  backup           - Create backups of critical files"
    Write-Host "  restore <file>   - Restore file from backup"
    Write-Host "  enable           - Enable file protection"
    Write-Host "  disable          - Disable file protection"
    Write-Host "  install          - Install protection system"
    Write-Host "  help             - Show this help"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  powershell -ExecutionPolicy Bypass -File protect.ps1 status"
    Write-Host "  powershell -ExecutionPolicy Bypass -File protect.ps1 backup"
    Write-Host ""
}

function Test-PythonAvailable {
    try {
        $null = Get-Command python -ErrorAction Stop
        return $true
    }
    catch {
        try {
            $null = Get-Command python3 -ErrorAction Stop
            return $true
        }
        catch {
            Write-Host "Python not found. Please install Python 3.8+." -ForegroundColor Red
            return $false
        }
    }
}

function Get-PythonCommand {
    try {
        $null = Get-Command python -ErrorAction Stop
        return "python"
    }
    catch {
        return "python3"
    }
}

function Invoke-ProtectionCommand {
    param([string]$Cmd, [string]$File = "", [string]$ReasonText = "")

    if (-not (Test-PythonAvailable)) {
        return $false
    }

    $python = Get-PythonCommand
    $args = @("scripts\project_protection.py", $Cmd)

    if ($File -ne "") {
        $args += $File
    }

    if ($ReasonText -ne "") {
        $args += $ReasonText
    }

    try {
        & $python @args
        return $true
    }
    catch {
        Write-Host "Error running protection command: $_" -ForegroundColor Red
        return $false
    }
}

# Main script logic
switch ($Command.ToLower()) {
    "help" {
        Show-Help
    }

    "status" {
        Write-Host "Checking project protection status..." -ForegroundColor Cyan
        Invoke-ProtectionCommand "status"
    }

    "backup" {
        Write-Host "Creating backups of critical files..." -ForegroundColor Cyan
        Invoke-ProtectionCommand "backup"
    }

    "restore" {
        if ($FilePath -eq "") {
            Write-Host "Please specify a file to restore" -ForegroundColor Red
            Write-Host "Usage: protect.ps1 restore file_path"
            exit 1
        }
        Write-Host "Restoring file: $FilePath" -ForegroundColor Cyan
        Invoke-ProtectionCommand "restore" $FilePath
    }

    "enable" {
        Write-Host "Enabling project protection..." -ForegroundColor Green
        if (Test-Path ".project_protection.json") {
            $config = Get-Content ".project_protection.json" | ConvertFrom-Json
            $config.protection_enabled = $true
            $config | ConvertTo-Json -Depth 10 | Set-Content ".project_protection.json"
            Write-Host "Protection enabled" -ForegroundColor Green
        }
        else {
            Write-Host "Protection config not found. Run 'install' first." -ForegroundColor Yellow
        }
    }

    "disable" {
        Write-Host "Disabling project protection..." -ForegroundColor Yellow
        Write-Host "Are you sure? This will disable all file protection safeguards." -ForegroundColor Red
        $confirm = Read-Host "Type 'yes' to confirm"

        if ($confirm -eq "yes") {
            if (Test-Path ".project_protection.json") {
                $config = Get-Content ".project_protection.json" | ConvertFrom-Json
                $config.protection_enabled = $false
                $config | ConvertTo-Json -Depth 10 | Set-Content ".project_protection.json"
                Write-Host "Protection disabled" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "Operation cancelled" -ForegroundColor Gray
        }
    }

    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
