@echo off
echo Running NeuroCode domain verification...
powershell -ExecutionPolicy Bypass -File "%~dp0verify-deployment.ps1"
pause
