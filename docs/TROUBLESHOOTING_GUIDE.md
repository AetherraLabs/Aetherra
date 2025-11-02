# Aetherra Troubleshooting Guide

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This guide helps diagnose and resolve common issues with Aetherra OS, Hub, services, and integrations. Each section includes symptoms, root causes, and step-by-step solutions.

## Quick Diagnosis Checklist

Before diving into specific issues, run this quick health check:

```powershell
# 1. Check if OS is running
python tools/os_smoke.py

# 2. Check Hub status
curl http://localhost:3001/api/stats

# 3. Check services in registry
# (Look for service_registry output in OS logs)

# 4. Check for errors in logs
Get-Content aetherra_os.log | Select-String -Pattern "ERROR|CRITICAL"

# 5. Verify environment
python -c "import sys; print(f'Python: {sys.version}'); import flask; print(f'Flask: {flask.__version__}')"
```

---

## 🚨 Critical Issues

### OS Won't Start

**Symptoms:**

- OS launcher exits immediately
- `Exit Code: 1` or `Exit Code: -1`
- Error messages about missing modules or import failures

**Common Causes:**

#### 1. Missing Dependencies

**Diagnosis:**

```powershell
pip list | Select-String "flask|requests|pydantic"
```

**Solution:**

```powershell
pip install -r requirements.txt
```

#### 2. Port Already in Use

**Diagnosis:**

```powershell
netstat -ano | findstr ":3001"
```

**Solution:**

```powershell
# Find and kill process using port 3001
$pid = (netstat -ano | findstr ":3001" | Select-String -Pattern "\d+$").Matches.Value
Stop-Process -Id $pid -Force

# Or use a different port
python aetherra_os_launcher.py --port 3002
```

#### 3. Corrupted State Files

**Symptoms:**

- "Failed to load state" errors
- JSON decode errors

**Solution:**

```powershell
# Backup current state
Copy-Item .aetherra .aetherra_backup -Recurse

# Remove corrupted state
Remove-Item .aetherra\*.json -Force

# Restart OS (will regenerate state)
python aetherra_os_launcher.py --mode full
```

#### 4. Python Virtual Environment Issues

**Symptoms:**

- Module not found errors despite installation
- Wrong Python version

**Solution:**

```powershell
# Recreate virtual environment
Remove-Item -Recurse .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### Hub Server Fails to Start

**Symptoms:**

- "Hub failed to initialize" in OS logs
- Port 3001 not responding
- Exit Code: 1 in Hub terminal

**Common Causes:**

#### 1. Registry Not Available

**Diagnosis:**
Check OS logs for:

```
[REGISTRY] Service registry not initialized
```

**Solution:**

```powershell
# Ensure OS starts before Hub
# Terminal 1:
python aetherra_os_launcher.py --mode full -v

# Wait for "OS online" message, then Terminal 2:
python tools/run_hub_ai_api.py --port 3001
```

#### 2. Blueprint Import Errors

**Diagnosis:**

```powershell
python -c "from aetherra_hub.blueprints import maintenance"
```

**Solution:**

```powershell
# Check for syntax errors in blueprints
Get-ChildItem aetherra_hub\blueprints\*.py | ForEach-Object {
    Write-Host "Checking $($_.Name)..."
    python -m py_compile $_.FullName
}
```

#### 3. Missing Configuration

**Diagnosis:**

```
FileNotFoundError: config.json
```

**Solution:**

```powershell
# Create minimal config.json
@"
{
  "hub_enabled": true,
  "gui_enabled": false,
  "log_level": "INFO"
}
"@ | Out-File -Encoding utf8 config.json
```

---

### Services Marked as DEGRADED or FAILED

**Symptoms:**

- `/api/stats` shows unhealthy services
- "Service not available" errors

**Diagnosis:**

```bash
curl http://localhost:3001/api/stats | jq '.services'
```

**Common Causes:**

#### 1. Service Heartbeat Timeout

**Symptoms:**

```json
{
  "self_incorporation": {
    "status": "DEGRADED",
    "last_heartbeat": "2025-11-01T09:00:00Z"
  }
}
```

**Solution:**
Service stopped sending heartbeats. Check service-specific logs:

```powershell
# Look for the service's error messages
Get-Content aetherra_os.log | Select-String "self_incorporation|ERROR"

# Restart OS to reinitialize services
```

#### 2. Service Initialization Failed

**Diagnosis:**
Look for init errors in OS startup logs:

```
[SELFINC] Failed to initialize: ...
```

**Solution:**
Check specific service requirements and dependencies.

---

## 🔌 Connection Issues

### Frontend Can't Connect to Hub

**Symptoms:**

- "Failed to fetch" errors in browser console
- API calls return network errors
- CORS errors

**Diagnosis:**

1. **Check Hub is running:**

```bash
curl http://localhost:3001/api/stats
```

2. **Check browser console:**
Press F12, look for network errors

**Solutions:**

#### Hub Not Running

```powershell
# Start Hub
python tools/run_hub_ai_api.py --port 3001
```

#### Wrong Port

**In `Aetherra/lyrixa/gui/vite.config.ts`:**

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:3001',  // Ensure this matches Hub port
      changeOrigin: true
    }
  }
}
```

#### CORS Issues

Hub should automatically handle CORS for localhost. If issues persist:

```powershell
# Check Hub CORS config in aetherra_hub/app.py
# Ensure flask-cors is installed
pip install flask-cors
```

---

### Registry Connection Errors

**Symptoms:**

- "Failed to connect to registry" errors
- Services can't communicate
- Message passing fails

**Diagnosis:**

```python
python -c "from aetherra_service_registry import get_service_registry; print(get_service_registry())"
```

**Solution:**

#### Registry Not Initialized

Registry must be started before any services:

```python
# In aetherra_os_launcher.py, ensure Phase 1 runs first:
# Phase 1: Initialize Service Registry
```

If using external registry daemon:

```powershell
# Terminal 1: Start registry daemon
python aetherra_registry_daemon.py --host 127.0.0.1 --port 3030

# Terminal 2: Start OS with registry URL
$env:AETHERRA_REGISTRY_URL="http://127.0.0.1:3030"
python aetherra_os_launcher.py --mode full
```

---

## 🧠 Memory System Issues

### Memory Queries Timeout

**Symptoms:**

- `/api/memory/status` returns 500 error
- Queries hang or timeout
- High memory RTT in metrics

**Diagnosis:**

```bash
curl http://localhost:3001/api/memory/status
```

**Solutions:**

#### Database Lock

**Symptoms:**

```
sqlite3.OperationalError: database is locked
```

**Solution:**

```powershell
# Stop all processes accessing memory
# Check for zombie processes
Get-Process python | Where-Object {$_.ProcessName -eq "python"}

# If needed, force unlock (data loss risk)
Remove-Item data\memory\*.db-wal
Remove-Item data\memory\*.db-shm
```

#### Corrupted Database

**Solution:**

```powershell
# Backup current database
Copy-Item data\memory\lyrixa_memory.db data\memory\lyrixa_memory.db.backup

# Run integrity check
sqlite3 data\memory\lyrixa_memory.db "PRAGMA integrity_check;"

# If corrupted, restore from backup or recreate
Remove-Item data\memory\lyrixa_memory.db
# OS will recreate on next start
```

#### STORM Initialization Failure

**Symptoms:**

```
[STORM] Failed to initialize: POT backend not available
```

**Solution:**

```powershell
# Disable STORM temporarily
$env:AETHERRA_MEMORY_STORM="0"

# Or install POT backend
pip install POT

# Check STORM status
curl http://localhost:3001/api/memory/status | jq '.storm'
```

---

### Memory Queries Return No Results

**Symptoms:**

- Queries return empty arrays
- `recall_memories()` returns no matches
- Memory appears empty despite storing data

**Diagnosis:**

```python
python -c "
import asyncio
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem

async def check():
    mem = LyrixaMemorySystem()
    await mem.initialize()
    stats = await mem.get_memory_stats()
    print(f'Total memories: {stats[\"total_memories\"]}')

asyncio.run(check())
"
```

**Solutions:**

#### Wrong Query Strategy

Try different recall strategies:

```python
# In code or via API
result = await memory.recall(
    query="my search",
    strategy="hybrid"  # Try: "core", "conceptual", "episodic", "storm"
)
```

#### Database Not Initialized

```powershell
# Check if database file exists
Test-Path data\memory\lyrixa_memory.db

# Check file size (should be > 0 bytes)
(Get-Item data\memory\lyrixa_memory.db).Length
```

---

## 🔄 Self-Improvement Issues

### Proposals Not Appearing in UI

**Symptoms:**

- Self-Improve tab shows no suggestions
- `/api/selfimprove/proposals` returns empty array

**Diagnosis:**

```bash
# Check if Self-Improvement Engine is enabled
curl http://localhost:3001/api/maintenance/status | jq '.subsystems.self_improvement_engine'
```

**Solutions:**

#### Engine Not Enabled

**In `config.json`:**

```json
{
  "self_improvement": {
    "enabled": true
  }
}
```

#### No Metrics Available

Self-Improvement Engine needs metrics from Homeostasis:

```powershell
# Check Homeostasis status
curl http://localhost:3001/api/homeostasis/status

# Ensure metrics bridge is running
# Look for Phase 8 in OS logs:
# [HOMEOSTASIS] Phase 8: Self-Improvement Metrics Bridge started
```

#### Proposal Generation Paused

Check if generation is paused or rate-limited.

---

### HMR Failures

**Symptoms:**

- "HMR unavailable" message after approval
- `restart_required: true` always returned
- Proposals approved but not applied

**Diagnosis:**

```bash
# Check HMR status
curl http://localhost:3001/api/kernel/status | jq '.hmr'
```

**Solutions:**

#### HMR Not Enabled

```powershell
# Set environment variables before starting OS
$env:AETHERRA_HMR_ENABLED="1"
$env:AETHERRA_HMR_MODE="safe"
$env:AETHERRA_HMR_AUTO_RELOAD="1"

python aetherra_os_launcher.py --mode full
```

#### HMR Controller Not Initialized

Check OS logs for:

```
[HMR] Controller initialized successfully
```

If missing, HMR failed to initialize. Check for errors.

#### Target Module Not Reloadable

Some modules can't be hot-reloaded. HMR works best with:

- Plugin modules
- Service adapters
- Non-core engine components

**See [AETHERRA_HMR_GUIDE.md](./AETHERRA_HMR_GUIDE.md) for detailed HMR troubleshooting.**

---

### Proposal Application Fails with 400 Error

**Symptoms:**

```json
{
  "ok": false,
  "error": "HMR application failed"
}
```

**Diagnosis:**
Check Hub logs for detailed error:

```powershell
# Hub terminal shows HMR error details
```

**Common Causes:**

#### Invalid Proposal ID

```json
{
  "error": "Proposal not found"
}
```

**Solution:** Ensure proposal ID is valid and not already applied.

#### Self-Incorporation Service Unavailable

```json
{
  "error": "Self-Incorporation service not available"
}
```

**Solution:**

```bash
# Check service status
curl http://localhost:3001/api/selfinc/status

# If not running, check OS logs for initialization errors
```

---

## 🔌 Plugin Issues

### Plugin Not Loading

**Symptoms:**

- Plugin not in `/api/plugins` list
- "Plugin not found" errors
- Missing from discovery logs

**Diagnosis:**

```bash
curl http://localhost:3001/api/plugins
```

**Solutions:**

#### Plugin Not Discovered

**Check plugin directory:**

```powershell
# Plugins should be in Aetherra/plugins/<category>/<name>/
Test-Path Aetherra\plugins\my_category\my_plugin\
```

**Run discovery:**

```powershell
python aetherra_plugin_discovery.py
```

#### Missing Manifest

Every plugin needs `aetherra-plugin.json`:

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "entry_point": "plugin.py:Plugin",
  "category": "tools"
}
```

#### Import Errors

**Check plugin imports:**

```powershell
python -c "from Aetherra.plugins.my_category.my_plugin.plugin import Plugin"
```

**Common import issues:**

- Missing dependencies
- Circular imports
- Syntax errors

---

### Plugin Execution Fails

**Symptoms:**

- Plugin invocation returns error
- Timeout errors
- "Capability not allowed" errors

**Solutions:**

#### Capability Not Granted

**Check capabilities policy:**

```bash
# Check if plugin's capability is in allowlist
curl http://localhost:3001/api/security/policy | jq '.capabilities.allow'
```

**Grant capability in `~/.aetherra/policy/capabilities.json`:**

```json
{
  "allow": {
    "plugin:my_plugin": ["network:outbound"]
  }
}
```

#### Plugin Timeout

**Increase timeout:**

```powershell
$env:AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC="60"
```

#### Circuit Breaker Opened

Plugin failed too many times and circuit breaker opened:

```bash
# Check kernel status for circuit breaker state
curl http://localhost:3001/api/kernel/status
```

**Solution:** Wait for cooldown period or restart OS to reset.

---

## 🎨 Frontend Issues

### Frontend Build Fails

**Symptoms:**

- `npm run dev` errors
- TypeScript compilation errors
- Module not found errors

**Solutions:**

#### Dependencies Not Installed

```powershell
cd Aetherra\lyrixa\gui
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json -Force
npm install
```

#### Node Version Mismatch

**Check Node version:**

```powershell
node --version  # Should be 18.x or 20.x
```

**Install correct version:**

```powershell
# Using nvm (if installed)
nvm install 20
nvm use 20
```

#### TypeScript Errors

```powershell
# Check for type errors
npm run type-check

# Clean TypeScript cache
Remove-Item .tsbuildinfo
```

---

### UI Components Not Updating

**Symptoms:**

- Stale data in UI
- Components not re-rendering
- Polling not working

**Solutions:**

#### Polling Interval Too Long

**In React components:**

```typescript
// Reduce polling interval (default is often 2000ms)
const data = useApiPoll("/api/stats", 1000);
```

#### API Endpoint Not Responding

**Check browser network tab:**

- Are requests succeeding?
- What's the response time?
- Are there any errors?

#### React State Not Updating

**Check React DevTools:**

- Is state changing?
- Are props being passed correctly?

---

## 📝 Aether Script Issues

### Script Won't Execute

**Symptoms:**

- `python aether.py workflow.aether` fails
- "Invalid signature" errors
- Parse errors

**Solutions:**

#### Missing Signature

```powershell
# Sign the script
python tools\sign_aether.py workflows\my_script.aether

# Verify signature
python tools\verify_aether_scripts.py --root workflows --strict
```

#### Syntax Errors

**Check script syntax:**

```powershell
python aether.py workflows\my_script.aether --validate-only
```

**Common syntax issues:**

- Missing colons
- Invalid operator names
- Incorrect indentation in meta section

#### Plugin Not Available

**Script references non-existent plugin:**

```
step1: run_plugin("nonexistent_plugin", ...)
```

**Solution:** Ensure plugin is loaded or remove the step.

---

### Script Execution Hangs

**Symptoms:**

- Script starts but never completes
- No output or progress
- Process appears frozen

**Diagnosis:**

```powershell
# Check if script is actually running
Get-Process | Where-Object {$_.ProcessName -eq "python"}
```

**Solutions:**

#### Infinite Loop in Script

**Add timeout to steps:**

```aether
meta:
  timeout: 300  # 5 minutes max

step1: run_plugin("my_plugin", ...)
```

#### Waiting for User Input

Some operations may wait for input. Check script for interactive steps.

#### Deadlock

Service or plugin may be deadlocked. Check logs for blocked operations.

---

## 🔐 Security & Authentication Issues

### Authentication Failures

**Symptoms:**

- 401 Unauthorized errors
- "Invalid token" messages

**Solutions:**

#### Token Not Provided

```bash
# Provide token in Authorization header
curl -H "Authorization: Bearer your_token_here" \
  http://localhost:3001/api/ai/ask
```

#### Token Mismatch

**Check token matches:**

```powershell
# Server expects:
$env:AETHERRA_AI_API_TOKEN="my_secret_token"

# Client must send same token in header
```

#### Token Expired

Currently tokens don't expire, but future versions may implement expiration.

---

### Network Policy Violations

**Symptoms:**

- "Network access denied" errors
- Outbound requests blocked

**Diagnosis:**

```bash
curl http://localhost:3001/api/security/policy | jq '.network'
```

**Solutions:**

#### Add to Allowlist

**In environment:**

```powershell
$env:AETHERRA_NETWORK_ALLOWLIST="localhost,127.0.0.1,trusted-domain.com"
```

**Or in `~/.aetherra/policy/network.json`:**

```json
{
  "allowlist": ["localhost", "127.0.0.1", "trusted-domain.com"],
  "denylist": []
}
```

#### Disable Strict Mode (Development Only)

```powershell
$env:AETHERRA_NET_STRICT="0"
```

**⚠️ Warning:** Only disable in development. Production should use strict mode.

---

## 🔍 Debugging Techniques

### Enable Verbose Logging

```powershell
# Set log level
$env:AETHERRA_LOG_LEVEL="DEBUG"

# Start OS with verbose flag
python aetherra_os_launcher.py --mode full -v
```

### Check Service Health

```bash
# Get all service statuses
curl http://localhost:3001/api/stats | jq

# Get specific subsystem status
curl http://localhost:3001/api/homeostasis/status
curl http://localhost:3001/api/memory/status
curl http://localhost:3001/api/selfinc/status
```

### Monitor Metrics

```bash
# Get Prometheus metrics
curl http://localhost:3001/metrics

# Filter specific metrics
curl http://localhost:3001/metrics | grep "aetherra_kernel"
```

### Analyze Logs

```powershell
# Search for errors
Get-Content aetherra_os.log | Select-String "ERROR|CRITICAL"

# Search for specific service
Get-Content aetherra_os.log | Select-String "SELFINC"

# Get last 50 lines
Get-Content aetherra_os.log -Tail 50

# Follow logs in real-time
Get-Content aetherra_os.log -Wait
```

### Use Python Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint()
breakpoint()
```

### Test Individual Components

```python
# Test memory system
python -c "
import asyncio
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem

async def test():
    mem = LyrixaMemorySystem()
    await mem.initialize()
    result = await mem.store_memory('Test memory', tags=['test'])
    print(f'Stored: {result}')

asyncio.run(test())
"
```

---

## 🆘 Emergency Procedures

### Force Stop All Processes

```powershell
# Stop all Python processes
Get-Process python | Stop-Process -Force

# Or target specific ones
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process
```

### Clean Slate Restart

```powershell
# 1. Stop all processes
Get-Process python | Stop-Process -Force

# 2. Backup state
Copy-Item .aetherra .aetherra_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss') -Recurse

# 3. Clean state
Remove-Item .aetherra\*.json -Force

# 4. Clean cache
Remove-Item __pycache__ -Recurse -Force
Remove-Item *.pyc -Recurse -Force

# 5. Restart
python aetherra_os_launcher.py --mode full -v
```

### Restore from Backup

```powershell
# Restore state files
Copy-Item .aetherra_backup\* .aetherra\ -Recurse -Force

# Restore database
Copy-Item backups\lyrixa_memory.db data\memory\lyrixa_memory.db -Force
```

### Safe Mode Boot

```powershell
# Minimal services only
$env:AETHERRA_SAFE_MODE="1"
$env:AETHERRA_HMR_ENABLED="0"
$env:AETHERRA_PLUGINS_ENABLED="0"

python aetherra_os_launcher.py --mode minimal
```

---

## 📊 Performance Issues

### High CPU Usage

**Diagnosis:**

```powershell
# Check CPU usage by process
Get-Process python | Select-Object ProcessName,CPU,Id | Sort-Object CPU -Descending
```

**Common Causes:**

#### Infinite Loop in Service

Check logs for repeating patterns.

#### Excessive Polling

Reduce polling frequency in services.

#### Night Cycle Running

Night cycles are CPU-intensive. Check if running during day:

```bash
curl http://localhost:3001/api/kernel/status | jq '.night_cycle'
```

---

### High Memory Usage

**Diagnosis:**

```powershell
# Check memory usage
Get-Process python | Select-Object ProcessName,WorkingSet,Id | Sort-Object WorkingSet -Descending
```

**Solutions:**

#### Memory Leak

**Enable memory profiling:**

```powershell
pip install memory_profiler
python -m memory_profiler aetherra_os_launcher.py
```

#### Large Memory Database

**Check database size:**

```powershell
(Get-Item data\memory\lyrixa_memory.db).Length / 1MB
```

**Compact database:**

```powershell
sqlite3 data\memory\lyrixa_memory.db "VACUUM;"
```

#### Run Maintenance Cycle

```python
# Trigger memory consolidation
import asyncio
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem

async def maintain():
    mem = LyrixaMemorySystem()
    await mem.initialize()
    await mem.consolidate_memories()

asyncio.run(maintain())
```

---

## 📞 Getting Help

### Check Existing Documentation

- [AETHERRA_HUB_API_REFERENCE.md](./AETHERRA_HUB_API_REFERENCE.md) - API endpoints
- [AETHERRA_KERNEL_SYSTEM.md](./AETHERRA_KERNEL_SYSTEM.md) - Kernel and services
- [AETHERRA_MEMORY_SYSTEM.md](./AETHERRA_MEMORY_SYSTEM.md) - Memory subsystem
- [DEVELOPER_ONBOARDING.md](./DEVELOPER_ONBOARDING.md) - Getting started

### Collect Debug Information

When reporting issues, include:

1. **Environment info:**

```powershell
python --version
pip list
$PSVersionTable.PSVersion
```

2. **Configuration:**

```powershell
Get-Content config.json
```

3. **Recent logs:**

```powershell
Get-Content aetherra_os.log -Tail 100 > debug_logs.txt
```

4. **Service status:**

```bash
curl http://localhost:3001/api/stats > service_status.json
```

5. **Reproduction steps:**

- What you were trying to do
- What happened
- What you expected to happen

### Community Support

- **GitHub Issues**: <https://github.com/AetherraLabs/Aetherra/issues>
- **Documentation**: <https://docs.aetherra.ai>
- **Email**: <support@aetherraalabs.com>

---

Status: ✅ Complete - Comprehensive troubleshooting guide covering critical issues, services, plugins, and debugging

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
