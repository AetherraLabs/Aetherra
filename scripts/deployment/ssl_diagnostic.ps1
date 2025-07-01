# SSL Certificate & Domain Diagnostic Script
# Checks the SSL status and configuration for neuro-code.dev

param(
    [string]$Domain = "neuro-code.dev"
)

Write-Host "🔍 Diagnosing SSL Certificate for: $Domain" -ForegroundColor Cyan
Write-Host "=" * 50

# Function to test HTTP vs HTTPS
function Test-SiteAccess {
    param([string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        Write-Host "✅ $Url - Status: $($response.StatusCode)" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ $Url - Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to check DNS records
function Test-DnsRecords {
    param([string]$Domain)

    Write-Host "`n🌐 DNS Records for $Domain" -ForegroundColor Yellow

    try {
        $aRecords = Resolve-DnsName -Name $Domain -Type A -ErrorAction SilentlyContinue
        if ($aRecords) {
            foreach ($record in $aRecords) {
                Write-Host "   A Record: $($record.IPAddress)" -ForegroundColor White
            }
        }

        $cnameRecords = Resolve-DnsName -Name $Domain -Type CNAME -ErrorAction SilentlyContinue
        if ($cnameRecords) {
            foreach ($record in $cnameRecords) {
                Write-Host "   CNAME: $($record.NameHost)" -ForegroundColor White
            }
        }
    }
    catch {
        Write-Host "   ⚠️ DNS lookup failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Function to check SSL certificate
function Test-SslCertificate {
    param([string]$Domain)

    Write-Host "`n🔒 SSL Certificate Status" -ForegroundColor Yellow

    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $tcpClient.Connect($Domain, 443)

        $sslStream = New-Object System.Net.Security.SslStream($tcpClient.GetStream())
        $sslStream.AuthenticateAsClient($Domain)

        $cert = $sslStream.RemoteCertificate
        $cert2 = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($cert)

        Write-Host "   ✅ Certificate found" -ForegroundColor Green
        Write-Host "   Subject: $($cert2.Subject)" -ForegroundColor White
        Write-Host "   Issuer: $($cert2.Issuer)" -ForegroundColor White
        Write-Host "   Valid From: $($cert2.NotBefore)" -ForegroundColor White
        Write-Host "   Valid Until: $($cert2.NotAfter)" -ForegroundColor White

        if ($cert2.NotAfter -lt (Get-Date)) {
            Write-Host "   ❌ Certificate has EXPIRED!" -ForegroundColor Red
        } elseif ($cert2.NotAfter -lt (Get-Date).AddDays(30)) {
            Write-Host "   ⚠️ Certificate expires soon!" -ForegroundColor Yellow
        } else {
            Write-Host "   ✅ Certificate is valid" -ForegroundColor Green
        }

        $sslStream.Close()
        $tcpClient.Close()
    }
    catch {
        Write-Host "   ❌ SSL connection failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   This is likely the cause of 'Your connection is not private'" -ForegroundColor Yellow
    }
}

# Main diagnostic process
Write-Host "`n📋 Testing Site Access" -ForegroundColor Yellow

$httpWorks = Test-SiteAccess "http://$Domain"
$httpsWorks = Test-SiteAccess "https://$Domain"

Test-DnsRecords $Domain
Test-SslCertificate $Domain

# GitHub Pages specific checks
Write-Host "`n📦 GitHub Pages Checks" -ForegroundColor Yellow

$githubPagesUrls = @(
    "https://yourusername.github.io/reponame",  # Replace with actual
    "https://$Domain"
)

Write-Host "   CNAME Configuration:" -ForegroundColor White
if (Test-Path "CNAME") {
    $cnameContent = Get-Content "CNAME" -Raw
    Write-Host "   Root CNAME: $cnameContent" -ForegroundColor White
}
if (Test-Path "website/CNAME") {
    $websiteCnameContent = Get-Content "website/CNAME" -Raw
    Write-Host "   Website CNAME: $websiteCnameContent" -ForegroundColor White
}

# Recommendations
Write-Host "`n💡 Recommendations" -ForegroundColor Yellow

if (-not $httpsWorks -and $httpWorks) {
    Write-Host "   1. SSL Certificate issue detected" -ForegroundColor Red
    Write-Host "      → GitHub Pages may be provisioning SSL certificate" -ForegroundColor White
    Write-Host "      → Wait 24-48 hours for certificate generation" -ForegroundColor White
    Write-Host "      → Check GitHub repository Settings > Pages > Enforce HTTPS" -ForegroundColor White
}

if (-not $httpWorks -and -not $httpsWorks) {
    Write-Host "   1. DNS or hosting issue detected" -ForegroundColor Red
    Write-Host "      → Check DNS records point to GitHub Pages" -ForegroundColor White
    Write-Host "      → Verify GitHub Pages deployment is working" -ForegroundColor White
}

Write-Host "`n🔧 Quick Fixes to Try:" -ForegroundColor Yellow
Write-Host "   1. Temporarily disable 'Enforce HTTPS' in GitHub Pages settings" -ForegroundColor White
Write-Host "   2. Wait 24 hours, then re-enable 'Enforce HTTPS'" -ForegroundColor White
Write-Host "   3. Check that CNAME files are consistent" -ForegroundColor White
Write-Host "   4. Verify GitHub Actions deployment completed successfully" -ForegroundColor White

Write-Host "`n" -NoNewline
Write-Host "✅ Diagnostic complete! " -ForegroundColor Green -NoNewline
Write-Host "Check the recommendations above." -ForegroundColor White
