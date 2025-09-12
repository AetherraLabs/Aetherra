<#
.SYNOPSIS
  One-command Docker quick start for Aetherra (alpha).

.DESCRIPTION
  Builds (or pulls in future) a dev image, runs Hub exposing core ports, and performs
  a health + chat probe. Designed for Windows PowerShell users.

.USAGE
  powershell -ExecutionPolicy Bypass -File tools/docker_quickstart.ps1
  # or from repo root
  ./tools/docker_quickstart.ps1

.NOTES
  Requires Docker daemon running. Uses local build context.
#>
param(
  [string]$Tag = "aetherra-dev:local",
  [int]$HubPort = 3001
)

Write-Host "[docker-quickstart] Building image $Tag ..." -ForegroundColor Cyan
docker build -t $Tag --target development . 2>$null
if ($LASTEXITCODE -ne 0) { Write-Error "Image build failed"; exit 1 }

Write-Host "[docker-quickstart] Running container (detached) ..." -ForegroundColor Cyan
$cid = docker run -d -e AETHERRA_AI_API_ENABLED=1 -e AETHERRA_AI_API_STREAM=1 -p ${HubPort}:3001 $Tag python -m aetherra_hub.compat
if (-not $cid) { Write-Error "Container failed to start"; exit 1 }

Write-Host "[docker-quickstart] Waiting for hub (port $HubPort) ..." -ForegroundColor Cyan
$attempt = 0
while ($attempt -lt 60) {
  try { (Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:$HubPort/api/lyrixa/chat" -Method POST -ContentType 'application/json' -Body '{"message":"ping"}' | Out-Null); break } catch { Start-Sleep -Milliseconds 500; $attempt++ }
}
if ($attempt -ge 60) { Write-Warning "Hub not responding; logs:"; docker logs $cid --tail 100; exit 2 }

Write-Host "[docker-quickstart] Chat probe:" -ForegroundColor Green
try {
  $resp = Invoke-RestMethod -Method Post -Uri "http://localhost:$HubPort/api/lyrixa/chat" -ContentType 'application/json' -Body '{"message":"hello from docker"}'
  $resp | ConvertTo-Json -Depth 6
}
catch { Write-Warning "Probe failed: $_" }

Write-Host "[docker-quickstart] Metrics (first 5 lines):" -ForegroundColor Green
try { (Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:$HubPort/metrics").Content -split "`n" | Select-Object -First 5 }
catch { Write-Warning "Metrics fetch failed" }

Write-Host "[docker-quickstart] Container ID: $cid" -ForegroundColor Cyan
Write-Host "Stop with: docker stop $cid" -ForegroundColor Yellow
