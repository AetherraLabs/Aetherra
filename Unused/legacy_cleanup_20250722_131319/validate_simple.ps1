Write-Host "File Recovery Validation Report" -ForegroundColor Green
Write-Host "=================================================="

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
        Write-Host "OK  $file ($lineCount lines)" -ForegroundColor Green
    } else {
        Write-Host "MISSING  $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Summary: $recoveredCount of $($files.Count) files recovered" -ForegroundColor Cyan
Write-Host "Total lines: $totalLines" -ForegroundColor Cyan

if ($recoveredCount -eq $files.Count) {
    Write-Host "STATUS: FULLY RESTORED - Ready for GUI redesign!" -ForegroundColor Green
}
