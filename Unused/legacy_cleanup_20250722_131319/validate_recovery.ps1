# File Recovery Validation Report
Write-Host "File Recovery Validation Report" -ForegroundColor Green
Write-Host "=================================================="
Write-Host

$files = @(
    "Aetherra\core\agent_orchestrator.py",
    "Aetherra\lyrixa\memory\memory_core.py",
    "Aetherra\lyrixa\engine\reasoning_engine.py",
    "Aetherra\lyrixa\engine\self_improvement_engine.py",
    "Aetherra\lyrixa\engine\plugin_chain_executor.py",
    "Aetherra\lyrixa\engine\introspection_controller.py",
    "Aetherra\lyrixa\engine\lyrixa_engine.py",
    "Aetherra\lyrixa\db_session.py"
)

$totalLines = 0
$recoveredCount = 0

foreach ($file in $files) {
    if (Test-Path $file) {
        $lineCount = (Get-Content $file | Measure-Object -Line).Lines
        $totalLines += $lineCount
        $recoveredCount++
        $fileDisplay = $file.PadRight(50)
        $linesDisplay = $lineCount.ToString().PadLeft(4)
        Write-Host "✓ $fileDisplay ($linesDisplay lines)" -ForegroundColor Green
    }
    else {
        $fileDisplay = $file.PadRight(50)
        Write-Host "✗ $fileDisplay (MISSING)" -ForegroundColor Red
    }
}

Write-Host
Write-Host "Summary: $recoveredCount/$($files.Count) critical files recovered" -ForegroundColor Cyan
Write-Host "Total code recovered: $($totalLines.ToString('N0')) lines" -ForegroundColor Cyan
Write-Host

if ($recoveredCount -eq $files.Count) {
    Write-Host "Core System Status: FULLY RESTORED" -ForegroundColor Green
    Write-Host "Ready for GUI redesign phase!" -ForegroundColor Green
}
else {
    $missing = $files.Count - $recoveredCount
    Write-Host "Missing $missing files" -ForegroundColor Yellow
}
