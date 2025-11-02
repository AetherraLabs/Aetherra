# Create Distribution Package for Aetherra OS
# Packages the built executable with documentation and generates checksums

param(
    [string]$Version = "1.0.0-beta.1",
    [string]$OutputDir = "dist-packages"
)

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Aetherra OS - Distribution Package Creator" -ForegroundColor Cyan
Write-Host " Version: $Version" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if build exists
if (-not (Test-Path "dist\AetherraOS\AetherraOS.exe")) {
    Write-Host "[ERROR] Build not found. Run build_exe.ps1 first." -ForegroundColor Red
    exit 1
}

# Create output directory
$packageName = "AetherraOS-$Version-Windows-x64"
$packageDir = Join-Path $OutputDir $packageName

Write-Host "[1/6] Creating package directory..." -ForegroundColor Yellow
if (Test-Path $packageDir) {
    Remove-Item $packageDir -Recurse -Force
}
New-Item -ItemType Directory -Path $packageDir -Force | Out-Null
Write-Host "  [OK] Created: $packageDir" -ForegroundColor Green

# Copy executable and dependencies
Write-Host ""
Write-Host "[2/6] Copying executable and dependencies..." -ForegroundColor Yellow
Copy-Item "dist\AetherraOS\*" -Destination $packageDir -Recurse -Force
$exeSize = [math]::Round((Get-Item "$packageDir\AetherraOS.exe").Length / 1MB, 2)
Write-Host "  [OK] Copied AetherraOS.exe ($exeSize MB)" -ForegroundColor Green

# Copy essential documentation
Write-Host ""
Write-Host "[3/6] Copying documentation..." -ForegroundColor Yellow
$docs = @(
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "docs/PRE_PACK_VALIDATION_GUIDE.md",
    "docs/PRE_PACK_QUICK_REFERENCE.md"
)

foreach ($doc in $docs) {
    if (Test-Path $doc) {
        $dest = Join-Path $packageDir (Split-Path $doc -Leaf)
        Copy-Item $doc -Destination $dest -Force
        Write-Host "  [OK] Copied: $(Split-Path $doc -Leaf)" -ForegroundColor Green
    }
    else {
        Write-Host "  [SKIP] Not found: $doc" -ForegroundColor Yellow
    }
}

# Create INSTALLATION.txt
Write-Host ""
Write-Host "[4/6] Creating installation guide..." -ForegroundColor Yellow
$installGuide = @"
AETHERRA AI OPERATING SYSTEM
Installation Guide - Version $Version
=====================================

SYSTEM REQUIREMENTS
-------------------
- Windows 10/11 (64-bit)
- 4 GB RAM minimum (8 GB recommended)
- 2 GB free disk space
- Internet connection for AI features

INSTALLATION STEPS
------------------
1. Extract this package to a folder of your choice
2. Run AetherraOS.exe to start the system
3. First launch will initialize the system (takes 30-60 seconds)

USAGE
-----
Launch modes:
  AetherraOS.exe --mode full       Full AI Operating System (default)
  AetherraOS.exe --mode minimal    Minimal systems only
  AetherraOS.exe --mode test       Test mode with mocks

Options:
  --gui           Enable GUI interface
  --no-gui        Disable GUI (terminal only)
  --verbose       Verbose logging
  --boot-menu     Show interactive boot menu
  --help          Show all options

CONFIGURATION
-------------
- Configuration file: config.json
- Environment template: .env.example
- Copy .env.example to .env and configure as needed

TROUBLESHOOTING
---------------
1. If the executable doesn't start:
   - Run as Administrator
   - Check Windows Defender / Antivirus settings
   - Ensure all files were extracted

2. For GUI issues:
   - Try running with --no-gui flag first
   - Check graphics drivers are up to date

3. For AI features:
   - Configure API keys in .env file
   - Check internet connectivity

DOCUMENTATION
-------------
See included documentation files:
- README.md - Project overview
- CHANGELOG.md - Version history
- PRE_PACK_VALIDATION_GUIDE.md - System validation
- PRE_PACK_QUICK_REFERENCE.md - Quick reference

SUPPORT
-------
GitHub: https://github.com/AetherraLabs/Aetherra
Issues: https://github.com/AetherraLabs/Aetherra/issues

LICENSE
-------
See LICENSE file for licensing information.

COPYRIGHT
---------
Copyright (c) 2024-2025 Aetherra Labs
"@

$installGuide | Out-File -FilePath (Join-Path $packageDir "INSTALLATION.txt") -Encoding UTF8
Write-Host "  [OK] Created: INSTALLATION.txt" -ForegroundColor Green

# Generate checksums
Write-Host ""
Write-Host "[5/6] Generating checksums..." -ForegroundColor Yellow
$checksumFile = Join-Path $packageDir "CHECKSUMS.txt"
$checksums = @()
$checksums += "Aetherra OS - File Checksums (SHA256)"
$checksums += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$checksums += "Version: $Version"
$checksums += "=" * 80
$checksums += ""

# Calculate checksums for important files
$filesToHash = @("AetherraOS.exe", "config.json", ".env.example")
foreach ($file in $filesToHash) {
    $filePath = Join-Path $packageDir $file
    if (Test-Path $filePath) {
        $hash = (Get-FileHash -Path $filePath -Algorithm SHA256).Hash
        $size = [math]::Round((Get-Item $filePath).Length / 1MB, 2)
        $checksums += "$hash  $file  ($size MB)"
        Write-Host "  [OK] $file - $hash" -ForegroundColor Green
    }
}

$checksums | Out-File -FilePath $checksumFile -Encoding UTF8

# Create ZIP archive
Write-Host ""
Write-Host "[6/6] Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = Join-Path $OutputDir "$packageName.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path $packageDir -DestinationPath $zipPath -CompressionLevel Optimal
$zipSize = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
Write-Host "  [OK] Created: $zipPath ($zipSize MB)" -ForegroundColor Green

# Calculate ZIP checksum
$zipHash = (Get-FileHash -Path $zipPath -Algorithm SHA256).Hash
$zipChecksumFile = Join-Path $OutputDir "$packageName.sha256"
"$zipHash  $packageName.zip" | Out-File -FilePath $zipChecksumFile -Encoding UTF8
Write-Host "  [OK] Checksum: $zipChecksumFile" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " DISTRIBUTION PACKAGE COMPLETE" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Package Directory: $packageDir" -ForegroundColor Cyan
Write-Host "ZIP Archive:       $zipPath ($zipSize MB)" -ForegroundColor Cyan
Write-Host "SHA256 Checksum:   $zipChecksumFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Package Contents:" -ForegroundColor Yellow
Get-ChildItem $packageDir | Select-Object Name, @{Name = "Size"; Expression = {
        if ($_.PSIsContainer) { "DIR" } else { "$([math]::Round($_.Length / 1MB, 2)) MB" }
    }
} | Format-Table -AutoSize
Write-Host ""
Write-Host "[SUCCESS] Distribution package ready for release!" -ForegroundColor Green
Write-Host ""
