# Aetherra OS - Production Package Builder
# Builds a standalone Windows executable with all production settings

param(
    [Parameter(Mandatory = $false)]
    [string]$Version = "1.0.0-beta.1",

    [Parameter(Mandatory = $false)]
    [switch]$Clean,

    [Parameter(Mandatory = $false)]
    [switch]$SkipTests,

    [Parameter(Mandatory = $false)]
    [switch]$OneFile,

    [Parameter(Mandatory = $false)]
    [switch]$DebugBuild
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " Aetherra OS - Production Package Builder" -ForegroundColor Cyan
Write-Host " Version: $Version" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Validate environment
Write-Host "[1/8] Validating environment..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "  [ERROR] Python not found!" -ForegroundColor Red
    exit 1
}

# Check PyInstaller
try {
    python -c "import PyInstaller" 2>$null
    Write-Host "  [OK] PyInstaller installed" -ForegroundColor Green
}
catch {
    Write-Host "  [WARN] PyInstaller not found, installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Step 2: Set production environment flags
Write-Host "`n[2/8] Setting production environment..." -ForegroundColor Yellow

$env:AETHERRA_PROFILE = "prod"
$env:AETHERRA_SIGNING_STRICT = "1"
$env:AETHERRA_SCRIPT_VERIFY_STRICT = "1"
$env:AETHERRA_REQUIRE_STRICT = "1"
$env:AETHERRA_REQUIRE_CAPABILITIES = "1"
$env:AETHERRA_NET_STRICT = "1"
$env:AETHERRA_AI_API_REQUIRE_TOKEN = "1"
$env:AETHERRA_HMR_ENABLED = "0"
$env:AETHERRA_TRAINER_ENABLED = "0"
$env:AETHERRA_QFAC_MODE = "disabled"
$env:AETHERRA_MEMORY_STORM = "0"
$env:AETHERRA_QUIET = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "  [OK] Production flags set" -ForegroundColor Green

# Step 3: Run pre-pack validation (if not skipping tests)
if (-not $SkipTests) {
    Write-Host "`n[3/8] Running pre-pack validation..." -ForegroundColor Yellow

    # Run smoke tests
    Write-Host "  Running smoke tests..." -ForegroundColor Gray
    $smokeResult = pytest -q -o addopts= tests/smoke 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Smoke tests passed" -ForegroundColor Green
    }
    else {
        Write-Host "  [WARN] Some smoke tests failed" -ForegroundColor Yellow
        Write-Host "  Continue anyway? (Y/N): " -NoNewline -ForegroundColor Yellow
        $continue = Read-Host
        if ($continue -ne "Y" -and $continue -ne "y") {
            Write-Host "  [ABORT] Packaging cancelled" -ForegroundColor Red
            exit 1
        }
    }
}
else {
    Write-Host "`n[3/8] Skipping tests (--SkipTests flag)" -ForegroundColor Gray
}

# Step 4: Clean previous builds
if ($Clean) {
    Write-Host "`n[4/8] Cleaning previous builds..." -ForegroundColor Yellow

    $dirsToClean = @("build", "dist", "__pycache__")
    foreach ($dir in $dirsToClean) {
        if (Test-Path $dir) {
            Remove-Item -Recurse -Force $dir
            Write-Host "  [OK] Removed $dir/" -ForegroundColor Green
        }
    }
}
else {
    Write-Host "`n[4/8] Skipping clean (use --Clean to clean)" -ForegroundColor Gray
}

# Step 5: Create production config
Write-Host "`n[5/8] Creating production configuration..." -ForegroundColor Yellow

$prodConfig = @{
    "profile"    = "production"
    "version"    = $Version
    "build_date" = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    "logging"    = @{
        "level" = "INFO"
    }
    "safety"     = @{
        "enforce_prod_defaults" = $true
    }
    "features"   = @{
        "hmr_enabled"     = $false
        "trainer_enabled" = $false
        "qfac_mode"       = "disabled"
        "storm_enabled"   = $false
    }
}

$prodConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath "config.production.json" -Encoding UTF8
Write-Host "  [OK] Created config.production.json" -ForegroundColor Green

# Step 6: Build with PyInstaller
Write-Host "`n[6/8] Building executable with PyInstaller..." -ForegroundColor Yellow

$pyinstallerArgs = @(
    "-y"  # Overwrite without asking
    "--clean"  # Clean cache
    "--log-level", "WARN"
)

if ($OneFile) {
    Write-Host "  Mode: Single-file executable" -ForegroundColor Cyan
    $pyinstallerArgs += @(
        "--onefile"
        "--name", "AetherraOS"
        "aetherra_os_launcher.py"
    )
}
else {
    Write-Host "  Mode: Directory bundle (faster startup)" -ForegroundColor Cyan
    $pyinstallerArgs += "aetherra_os.spec"
}

if ($DebugBuild) {
    $pyinstallerArgs += "--debug", "all"
}

Write-Host "  Running PyInstaller..." -ForegroundColor Gray
$buildOutput = & pyinstaller @pyinstallerArgs 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Build completed successfully" -ForegroundColor Green
}
else {
    Write-Host "  [ERROR] Build failed!" -ForegroundColor Red
    Write-Host $buildOutput -ForegroundColor Red
    exit 1
}

# Step 7: Package additional files
Write-Host "`n[7/8] Packaging additional files..." -ForegroundColor Yellow

$distPath = if ($OneFile) { "dist" } else { "dist\AetherraOS" }

# Copy essential files
$filesToCopy = @(
    @{Source = ".env.example"; Dest = "$distPath\.env.example" },
    @{Source = "config.production.json"; Dest = "$distPath\config.json" },
    @{Source = "README.md"; Dest = "$distPath\README.md" },
    @{Source = "LICENSE"; Dest = "$distPath\LICENSE" },
    @{Source = "COPYRIGHT"; Dest = "$distPath\COPYRIGHT" }
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file.Source) {
        Copy-Item $file.Source $file.Dest -Force
        Write-Host "  [OK] Copied $($file.Source)" -ForegroundColor Green
    }
}

# Create data directories
$dataDirs = @("workflows", "plugins", "logs", ".aetherra")
foreach ($dir in $dataDirs) {
    $targetDir = Join-Path $distPath $dir
    if (!(Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        Write-Host "  [OK] Created $dir/ directory" -ForegroundColor Green
    }
}

# Copy workflows if they exist
if (Test-Path "workflows") {
    Copy-Item "workflows\*" "$distPath\workflows\" -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Copied workflows" -ForegroundColor Green
}

# Step 8: Create distribution package
Write-Host "`n[8/8] Creating distribution package..." -ForegroundColor Yellow

$packageName = "AetherraOS-$Version-Windows-x64"
$packagePath = "dist\$packageName"

if (Test-Path $packagePath) {
    Remove-Item -Recurse -Force $packagePath
}

if ($OneFile) {
    New-Item -ItemType Directory -Path $packagePath -Force | Out-Null
    Copy-Item "$distPath\AetherraOS.exe" "$packagePath\" -Force
    Copy-Item "$distPath\*.md" "$packagePath\" -Force -ErrorAction SilentlyContinue
    Copy-Item "$distPath\LICENSE" "$packagePath\" -Force -ErrorAction SilentlyContinue
    Copy-Item "$distPath\config.json" "$packagePath\" -Force -ErrorAction SilentlyContinue
    Copy-Item "$distPath\.env.example" "$packagePath\" -Force -ErrorAction SilentlyContinue
}
else {
    Rename-Item $distPath $packagePath -Force
}

# Create README for distribution
$distReadme = @"
# Aetherra AI Operating System

Version: $Version
Build Date: $(Get-Date -Format "yyyy-MM-dd")

## Quick Start

1. Copy .env.example to .env and configure your settings
2. Run AetherraOS.exe
3. Access the web interface at http://localhost:3001

## System Requirements

- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- 500MB disk space
- Internet connection (for AI features)

## Configuration

Edit config.json to customize:
- Logging levels
- Port numbers
- Feature flags
- Security settings

## Support

Documentation: https://github.com/AetherraLabs/Aetherra
Issues: https://github.com/AetherraLabs/Aetherra/issues

## License

See LICENSE file for details.

---
Built with Aetherra Labs | $(Get-Date -Format "yyyy")
"@

$distReadme | Out-File -FilePath "$packagePath\README.txt" -Encoding UTF8

# Create ZIP archive
Write-Host "  Creating ZIP archive..." -ForegroundColor Gray
$zipPath = "$packagePath.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path $packagePath -DestinationPath $zipPath -CompressionLevel Optimal
Write-Host "  [OK] Created $zipPath" -ForegroundColor Green

# Calculate checksums
Write-Host "  Calculating checksums..." -ForegroundColor Gray
$exePath = if ($OneFile) { "$packagePath\AetherraOS.exe" } else { "$packagePath\AetherraOS\AetherraOS.exe" }
$exeHash = (Get-FileHash -Path $exePath -Algorithm SHA256).Hash
$zipHash = (Get-FileHash -Path $zipPath -Algorithm SHA256).Hash

$checksums = @"
# Aetherra OS - $Version Checksums

## Executable
File: AetherraOS.exe
SHA256: $exeHash

## Distribution Archive
File: $packageName.zip
SHA256: $zipHash

Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
"@

$checksums | Out-File -FilePath "$packagePath.sha256" -Encoding UTF8
Write-Host "  [OK] Created checksums file" -ForegroundColor Green

# Final summary
Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host " Build Complete!" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Package Details:" -ForegroundColor White
Write-Host "  Version: $Version" -ForegroundColor Gray
Write-Host "  Size: $([math]::Round((Get-Item $zipPath).Length / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host ""
Write-Host "Output Files:" -ForegroundColor White
Write-Host "  Executable: $exePath" -ForegroundColor Gray
Write-Host "  Archive: $zipPath" -ForegroundColor Gray
Write-Host "  Checksums: $packagePath.sha256" -ForegroundColor Gray
Write-Host ""
Write-Host "SHA256 (exe): $exeHash" -ForegroundColor Gray
Write-Host "SHA256 (zip): $zipHash" -ForegroundColor Gray
Write-Host ""
Write-Host "[SUCCESS] Ready for distribution!" -ForegroundColor Green
Write-Host ""

# Optional: Test the executable
Write-Host "Test the executable? (Y/N): " -NoNewline -ForegroundColor Yellow
$test = Read-Host
if ($test -eq "Y" -or $test -eq "y") {
    Write-Host "`nStarting test run..." -ForegroundColor Cyan
    & $exePath --help
}

Write-Host ""
Write-Host "Packaging complete! You can now distribute:" -ForegroundColor Cyan
Write-Host "  $zipPath" -ForegroundColor White
Write-Host ""
