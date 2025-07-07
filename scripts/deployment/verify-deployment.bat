@echo off
echo Running Aetherra domain verification...
powershell -ExecutionPolicy Bypass -File "%~dp0verify-deployment.ps1"
pause
