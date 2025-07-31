# Aetherra Domain Verification Script (PowerShell)
# Tests DNS propagation and GitHub Pages deployment

Write-Host "=== Aetherra Domain Verification ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: DNS Resolution
Write-Host "1. Testing DNS resolution for httpsAetherra.dev..." -ForegroundColor Yellow
try {
    $dns = Resolve-DnsName httpsAetherra.dev -Type A -ErrorAction Stop
    Write-Host "✓ DNS resolved successfully:" -ForegroundColor Green
    $dns | ForEach-Object { Write-Host "  - $($_.IPAddress)" }
} catch {
    Write-Host "✗ DNS resolution failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: CNAME Resolution
Write-Host "2. Testing CNAME resolution for www.httpsAetherra.dev..." -ForegroundColor Yellow
try {
    $cname = Resolve-DnsName www.httpsAetherra.dev -Type CNAME -ErrorAction Stop
    Write-Host "✓ CNAME resolved successfully:" -ForegroundColor Green
    $cname | ForEach-Object { Write-Host "  - $($_.NameHost)" }
} catch {
    Write-Host "✗ CNAME resolution failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: HTTP Response
Write-Host "3. Testing HTTP response from httpsAetherra.dev..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://httpsAetherra.dev" -Method Head -UseBasicParsing -ErrorAction Stop
    Write-Host "✓ HTTP response successful:" -ForegroundColor Green
    Write-Host "  - Status Code: $($response.StatusCode)"
    Write-Host "  - Server: $($response.Headers.Server)"
} catch {
    Write-Host "✗ HTTP request failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: GitHub Pages Status
Write-Host "4. Testing GitHub Pages content..." -ForegroundColor Yellow
try {
    $content = Invoke-WebRequest -Uri "https://httpsAetherra.dev" -UseBasicParsing -ErrorAction Stop
    if ($content.Content -match "Aetherra") {
        Write-Host "✓ GitHub Pages serving Aetherra content" -ForegroundColor Green
    } else {
        Write-Host "⚠ GitHub Pages serving content, but Aetherra branding not detected" -ForegroundColor Orange
    }
    Write-Host "  - Content Length: $($content.Content.Length) bytes"
} catch {
    Write-Host "✗ Could not fetch GitHub Pages content: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: CNAME File Check
Write-Host "5. Verifying CNAME file in repository..." -ForegroundColor Yellow
try {
    $cnameFile = Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Zyonic88/Aetherra/main/CNAME" -UseBasicParsing -ErrorAction Stop
    $cnameContent = $cnameFile.Content.Trim()
    if ($cnameContent -eq "httpsAetherra.dev") {
        Write-Host "✓ CNAME file contains correct domain: $cnameContent" -ForegroundColor Green
    } else {
        Write-Host "⚠ CNAME file contains unexpected content: $cnameContent" -ForegroundColor Orange
    }
} catch {
    Write-Host "✗ Could not fetch CNAME file: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Verification Complete ===" -ForegroundColor Cyan
Write-Host "If any tests failed, wait 10-30 minutes and run this script again." -ForegroundColor Gray
Write-Host "DNS propagation can take up to 48 hours in some cases." -ForegroundColor Gray
