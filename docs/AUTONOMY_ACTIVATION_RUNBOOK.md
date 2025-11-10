# Aetherra OS Autonomy Activation Runbook

**Version:** 3.0-beta
**Date:** November 2, 2025
**Status:** Production-Ready
**Safety Level:** Maximum (MAB Compliant)

---

## 🎯 Executive Summary

This runbook guides the safe activation of Aetherra OS's full autonomy capabilities following the **Minimum Autonomy Baseline (MAB)** framework. The system will operate in:

- **Staging**: `AUTONOMY_MODE=suggest` - OS suggests actions, human approves
- **Production**: `AUTONOMY_MODE=auto` - OS acts autonomously within safety envelope

**Critical Success Factors:**

- ✅ All safety rails active before autonomy
- ✅ Metrics observable in real-time
- ✅ Rollback procedures tested
- ✅ Token auth enforced on all APIs
- ✅ Spec→Tests gate blocks unsafe code changes

---

## 📋 Pre-Flight Checklist

### Infrastructure Ready

- [ ] Python 3.11+ environment active
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] SQLite database initialized
- [ ] Sufficient disk space (10GB+ recommended)
- [ ] Network connectivity verified

### Configuration Ready

- [ ] Copy `.env.autonomy.staging.template` → `.env.autonomy.staging`
- [ ] Generate staging tokens (128-bit min entropy)
- [ ] Review `config.autonomy.staging.json` settings
- [ ] Backup current config/data before proceeding

### Security Ready

- [ ] Token authentication configured
- [ ] Rate limiting thresholds set
- [ ] Network allowlist defined
- [ ] Audit logging enabled
- [ ] TLS certificates ready (production only)

### Observability Ready

- [ ] Prometheus endpoint accessible
- [ ] Dashboard UI available
- [ ] Log aggregation configured
- [ ] Alert thresholds defined

---

## 🚀 Phase 1: Environment Setup

### 1.1 Activate Staging Configuration

```powershell
# Set environment profile
$env:AETHERRA_PROFILE = "staging"
$env:AETHERRA_CONFIG_PATH = "config.autonomy.staging.json"

# Load staging environment variables
Get-Content .env.autonomy.staging | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Verify configuration
python -c "import os; print('Profile:', os.getenv('AETHERRA_PROFILE')); print('Autonomy Mode:', os.getenv('AETHERRA_AUTONOMY_MODE'))"
```

**Expected Output:**

```
Profile: staging
Autonomy Mode: suggest
```

### 1.2 Generate Secure Tokens

```powershell
# Generate staging tokens (128-bit)
python -c "import secrets; print('HUB_TOKEN:', secrets.token_urlsafe(32))"
python -c "import secrets; print('AGENTS_TOKEN:', secrets.token_urlsafe(32))"

# Update .env.autonomy.staging with generated tokens
# Replace <GENERATE_STAGING_TOKEN> placeholders
```

**Security Note:** Store tokens securely. Never commit to git. Use environment variables or secret management in production.

---

## 🏥 Phase 2: Hub + Security Hardening

### 2.1 Start Hub with Auth Enabled

```powershell
# Terminal 1: Start Hub with token auth
$env:AETHERRA_AI_API_REQUIRE_TOKEN = "1"
$env:AETHERRA_AI_API_TOKEN = "<YOUR_HUB_TOKEN>"
python tools/run_hub_ai_api.py --port 3001
```

**Health Check:**

```powershell
# Without token - should fail
curl http://localhost:3001/api/ai/ask -d '{"message":"test"}' -H "Content-Type: application/json"
# Expected: 401 Unauthorized

# With token - should succeed
curl http://localhost:3001/api/ai/ask `
  -d '{"message":"test"}' `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer <YOUR_HUB_TOKEN>"
# Expected: 200 OK with response
```

### 2.2 Verify Security Endpoints

```powershell
# Check policy endpoint
curl http://localhost:3001/api/security/policy -H "Authorization: Bearer <YOUR_HUB_TOKEN>"

# Check Interactive Lyrixa emotion endpoint
curl http://localhost:3001/api/interactive/emotion -H "Authorization: Bearer <YOUR_HUB_TOKEN>"

# Check metrics endpoint
curl http://localhost:3001/metrics
```

**Success Criteria:**

- ✅ Token auth blocking unauthorized requests
- ✅ Rate limiting active (check headers: `X-RateLimit-*`)
- ✅ Audit logs showing request traces
- ✅ All endpoints responding correctly

---

## 💾 Phase 3: Memory System Configuration

### 3.1 Initialize Memory with QFAC + Shadow STORM

```powershell
# Verify memory configuration
python -c "
import json
with open('config.autonomy.staging.json') as f:
    cfg = json.load(f)
    print('Memory Engine:', cfg['memory']['engine'])
    print('QFAC Enabled:', cfg['memory']['qfac_enabled'])
    print('STORM Mode:', cfg['memory']['storm']['mode'])
"
```

**Expected Output:**

```
Memory Engine: sqlite
QFAC Enabled: True
STORM Mode: shadow
```

### 3.2 Test Memory Operations

```powershell
# Start memory service (if standalone)
# Or check status if part of OS launcher
curl http://localhost:3001/api/memory/status -H "Authorization: Bearer <YOUR_HUB_TOKEN>"
```

**Success Criteria:**

- ✅ SQLite DB created and accessible
- ✅ QFAC compression active
- ✅ STORM running in shadow mode (no production writes yet)
- ✅ Backup schedule configured

---

## 🔧 Phase 4: Maintenance System 24/7

### 4.1 Start Homeostasis Controller

```powershell
# Verify homeostasis configuration
python -c "
import json
with open('config.autonomy.staging.json') as f:
    cfg = json.load(f)
    h = cfg['maintenance']['homeostasis']
    print('Mode:', h['mode'])
    print('PID (Kp, Ki, Kd):', h['pid_tuning']['kp'], h['pid_tuning']['ki'], h['pid_tuning']['kd'])
    print('Max Actions/Hour:', h['max_actions_per_hour'])
"
```

### 4.2 Enable Self-Improvement Engine

```powershell
# Check self-improvement settings
curl http://localhost:3001/api/selfimprove/status -H "Authorization: Bearer <YOUR_HUB_TOKEN>"
```

**Expected Response:**

```json
{
  "enabled": true,
  "hmr_enabled": true,
  "require_approval": true,
  "proposals_generated": 0,
  "proposals_accepted": 0
}
```

### 4.3 Activate Self-Incorporation

```powershell
# Verify self-incorporation is in safe discovery mode
# Check logs for discovery activities
python -c "
import json
with open('config.autonomy.staging.json') as f:
    cfg = json.load(f)
    si = cfg['maintenance']['self_incorporation']
    print('Discovery Mode:', si['discovery_mode'])
    print('Integration Gating:', si['integration_gating'])
    print('Test Before Integrate:', si['test_before_integrate'])
"
```

**Success Criteria:**

- ✅ Homeostasis PID loops active and stable
- ✅ Self-improvement proposals being generated
- ✅ Self-incorporation scanning for safe code patterns
- ✅ All actions respect cooldowns and rate limits

---

## 🤖 Phase 5: Agent Orchestrator Loop

### 5.1 Enable Agent API

```powershell
# Start OS with agents enabled (or check if already running)
curl http://localhost:3001/api/agents -H "Authorization: Bearer <YOUR_AGENTS_TOKEN>"
```

**Expected Response:**

```json
{
  "orchestrator": {
    "total_agents": 5,
    "active_agents": 0,
    "pending_tasks": 0,
    "tick_hz": 1,
    "capability_routing": true
  }
}
```

### 5.2 Submit Test Task

```powershell
# Create a simple test task
curl -X POST http://localhost:3001/api/tasks `
  -H "Authorization: Bearer <YOUR_AGENTS_TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{
    "name": "health_check_task",
    "description": "Verify orchestrator is working",
    "capabilities_required": ["system:status"],
    "priority": "normal"
  }'
```

### 5.3 Monitor Task Execution

```powershell
# Poll task status
curl http://localhost:3001/api/tasks?limit=10 -H "Authorization: Bearer <YOUR_AGENTS_TOKEN>"
```

**Success Criteria:**

- ✅ Agents responding to capability requests
- ✅ Tasks moving through states: PENDING → ASSIGNED → RUNNING → COMPLETED
- ✅ Track record weighting functional
- ✅ No timeouts or policy denials on valid tasks

---

## 🧠 Phase 6: Consciousness Loop (Suggest Mode)

### 6.1 Start Consciousness Runner

```powershell
# Verify consciousness settings
python -c "
import os
print('Autonomy Mode:', os.getenv('AETHERRA_AUTONOMY_MODE'))
print('Safety Envelope:', os.getenv('AETHERRA_SAFETY_ENVELOPE_ENABLED'))
print('Tick Hz:', os.getenv('AETHERRA_TICK_HZ'))
print('QFAC Enabled:', os.getenv('AETHERRA_ENABLE_QFAC'))
"
```

**Expected Output:**

```
Autonomy Mode: suggest
Safety Envelope: 1
Tick Hz: 1
QFAC Enabled: 1
```

### 6.2 Observe Consciousness Cycles

```powershell
# Watch ThinkStream (if UI available)
Start-Process "http://localhost:3001/think-stream"

# Or monitor via API
curl http://localhost:3001/api/consciousness/status -H "Authorization: Bearer <YOUR_HUB_TOKEN>"
```

### 6.3 Test Suggest Mode

**In Suggest Mode:**

- Consciousness will OBSERVE and SUGGEST actions
- NO actions executed without approval
- All suggestions logged for review

**Monitor Suggestions:**

```powershell
# Check recent suggestions
curl http://localhost:3001/api/consciousness/suggestions -H "Authorization: Bearer <YOUR_HUB_TOKEN>"
```

**Success Criteria:**

- ✅ Consciousness loop running at 1Hz
- ✅ Safety envelope validating all suggestions
- ✅ QFAC narratives being persisted
- ✅ No auto-execution in suggest mode

---

## 💻 Phase 7: Coding Autopilot with Test Gate

### 7.1 Enable Spec→Tests Gate

```powershell
# Verify test gate is enforced
python -c "
import json
with open('config.autonomy.staging.json') as f:
    cfg = json.load(f)
    ca = cfg['coding_autopilot']
    print('Spec→Tests Gate:', ca['spec_to_tests_gate'])
    print('Mandatory Test Pass:', ca['mandatory_test_pass'])
    print('Stages:', ca['stages'])
"
```

**Expected Output:**

```
Spec→Tests Gate: True
Mandatory Test Pass: True
Stages: ['plan', 'patch', 'verify', 'sign', 'ship']
```

### 7.2 Test Code Change Flow

```powershell
# Create a test specification
echo "SPEC: Add hello_world function to utils.py
Requirements:
- Function returns 'Hello, World!'
- Include unit test
- Must pass lint" > test_spec.txt

# Submit to coding autopilot (via Lyrixa chat or API)
curl -X POST http://localhost:3001/api/ai/ask `
  -H "Authorization: Bearer <YOUR_HUB_TOKEN>" `
  -H "Content-Type: application/json" `
  -d '{
    "message": "Implement the specification in test_spec.txt",
    "context": {"type": "coding_task"}
  }'
```

### 7.3 Verify Gate Enforcement

**The system must:**

1. Generate tests FIRST
2. Run tests (should fail initially)
3. Generate code patch
4. Apply patch
5. Run tests again (must pass)
6. Lint code (must pass)
7. Sign changes
8. Ship (commit/apply)

**Check Logs:**

```powershell
# Look for spec→tests gate enforcement messages
Select-String -Path "logs/*.log" -Pattern "spec_to_tests_gate"
```

**Success Criteria:**

- ✅ No code changes without passing tests
- ✅ All stages complete in order
- ✅ Signature verification on shipped code
- ✅ Rollback on any stage failure

---

## 📊 Phase 8: Observability & Monitoring

### 8.1 Access Metrics Dashboard

```powershell
# Open Prometheus metrics
Start-Process "http://localhost:3001/metrics"

# Open Lyrixa GUI dashboard
Start-Process "http://localhost:3001"
```

### 8.2 Configure Alert Thresholds

**Monitor These Key Metrics:**

| Metric                     | Threshold | Alert Level             |
| -------------------------- | --------- | ----------------------- |
| `consciousness_coherence`  | < 0.7     | WARNING                 |
| `homeostasis_stability`    | < 0.8     | WARNING                 |
| `agent_success_rate`       | < 0.7     | WARNING                 |
| `memory_recall_latency_ms` | > 200     | WARNING                 |
| `autopilot_eligibility`    | > 0.9     | INFO (ready to promote) |

### 8.3 Set Up Log Monitoring

```powershell
# Tail all logs in real-time
Get-Content -Path "logs/aetherra.log" -Wait -Tail 50

# Filter for critical events
Select-String -Path "logs/*.log" -Pattern "CRITICAL|ERROR" | Select-Object -Last 20
```

**Success Criteria:**

- ✅ All metrics exporting to Prometheus
- ✅ Dashboard showing real-time status
- ✅ Alert thresholds configured
- ✅ Logs structured and queryable

---

## 💾 Phase 9: Backup & Recovery Automation

### 9.1 Configure Backup Schedule

```powershell
# Create backup script wrapper
@'
# Aetherra Backup Script
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Memory DB backup (hourly)
if ((Get-Date).Minute -eq 0) {
    Copy-Item "aetherra_memory.db" "backups/memory/memory_$timestamp.db"
}

# Config backup (daily at 2 AM)
if ((Get-Date).Hour -eq 2 -and (Get-Date).Minute -eq 0) {
    Copy-Item "config*.json" "backups/configs/"
    Copy-Item ".env*" "backups/configs/"
}

# Full system backup (weekly on Sunday at 3 AM)
if ((Get-Date).DayOfWeek -eq "Sunday" -and (Get-Date).Hour -eq 3) {
    python tools/backup_system.py --full --verify
}
'@ | Out-File -FilePath "tools/automated_backup.ps1"
```

### 9.2 Schedule Backups

```powershell
# Windows Task Scheduler
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File tools/automated_backup.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At "00:00" -RepetitionInterval (New-TimeSpan -Minutes 60)
Register-ScheduledTask -TaskName "AetherraAutomatedBackup" -Action $action -Trigger $trigger
```

### 9.3 Test Backup & Restore

```powershell
# Create test backup
python tools/backup_system.py --memory --configs --verify

# Simulate restore
python tools/restore_system.py --backup "backups/memory/memory_latest.db" --dry-run
```

**Success Criteria:**

- ✅ Hourly memory DB backups running
- ✅ Daily config backups running
- ✅ Weekly full system backups running
- ✅ Backup verification passing
- ✅ Restore procedure tested and documented

---

## 🎓 Phase 10: Autonomy Promotion (Suggest → Auto)

### 10.1 Validate Eligibility Metrics

**Before promoting to AUTO mode, verify:**

```powershell
# Check autopilot eligibility
curl http://localhost:3001/api/consciousness/autopilot_eligibility `
  -H "Authorization: Bearer <YOUR_HUB_TOKEN>"
```

**Expected Response for Promotion:**

```json
{
  "eligible": true,
  "self_trust": 0.78,
  "snci": 0.62,
  "recent_success_rate": 0.87,
  "action_window_size": 100,
  "thresholds_met": {
    "min_self_trust": true,
    "min_snci": true,
    "min_recent_success": true
  },
  "promotion_conditions": {
    "uptime_hours": 36,
    "successful_cycles": 142,
    "zero_critical_failures": true
  }
}
```

**DO NOT PROMOTE IF:**

- ❌ `eligible: false`
- ❌ Any threshold not met
- ❌ Recent critical failures
- ❌ Uptime < 24 hours
- ❌ Successful cycles < 100

### 10.2 Staged Promotion Plan

**Week 1: Suggest Mode**

- Run 24/7 in suggest mode
- Collect metrics
- Review all suggestions manually
- Fix any issues

**Week 2: Limited Auto Mode**

- Promote ONLY low-risk capabilities to auto
- Keep high-risk in suggest mode
- Monitor closely

**Week 3: Full Auto Mode**

- If Week 1-2 green, promote to full auto
- Keep HiTL approval for critical actions

### 10.3 Promote to Auto Mode

```powershell
# Update environment
$env:AETHERRA_AUTONOMY_MODE = "auto"

# Restart consciousness loop
# The system will now ACT autonomously within safety envelope

# Monitor first hour closely
Get-Content -Path "logs/consciousness.log" -Wait -Tail 100
```

### 10.4 Auto Mode Safety Checks

**The system will:**

- ✅ Execute approved actions automatically
- ✅ Still respect safety envelope boundaries
- ✅ Still enforce Spec→Tests gate on code changes
- ✅ Still apply rate limits and cooldowns
- ✅ Still log all actions for audit
- ✅ Still rollback on failures

**Monitor These During First 24h of Auto:**

- Action success rate (should stay > 85%)
- Rollback frequency (should be < 5%)
- Safety envelope rejections
- Critical errors (should be zero)

---

## 🛡️ Safety Rails - Always Active

### Consciousness Safety Envelope

- **Pre-action validation**: Every action validated before execution
- **Post-action verification**: Results checked against expectations
- **Automatic rollback**: Failed actions reverted immediately

### Spec→Tests Gate

- **NO code changes** without passing tests first
- **ALL changes** must pass lint
- **ALL changes** must be signed
- **Failed tests** = no code applied

### Rate Limiting & Cooldowns

- **Homeostasis**: Max 10 actions/hour in staging, 5 in prod
- **Self-Improvement**: Max 5 proposals/cycle
- **Coding**: Max 5 changes/hour
- **Cooldowns**: 60s staging, 120s prod between major actions

### Token Authentication

- **ALL APIs** require valid Bearer token
- **Tokens rotate** every 30 days (staging) / 14 days (prod)
- **Failed auth** = immediate 401, logged

### Capability Policy

- **Dangerous ops** require approval: `network:external`, `file:write_system`, `exec:shell`
- **Denied ops** never execute: `file:delete_system`, `exec:privileged`

---

## 🚨 Emergency Procedures

### Emergency Stop

```powershell
# Stop all autonomous operations immediately
curl -X POST http://localhost:3001/api/homeostasis/emergency_stop `
  -H "Authorization: Bearer <YOUR_HUB_TOKEN>" `
  -d '{"reason": "Manual emergency stop"}'

# Verify stopped
curl http://localhost:3001/api/homeostasis/status `
  -H "Authorization: Bearer <YOUR_HUB_TOKEN>"
# Should show emergency_stop: true
```

### Rollback Last Action

```powershell
# Undo the most recent homeostasis action
curl -X POST http://localhost:3001/api/homeostasis/rollback `
  -H "Authorization: Bearer <YOUR_HUB_TOKEN>"
```

### Downgrade Auto → Suggest

```powershell
# Immediately switch to suggest-only mode
$env:AETHERRA_AUTONOMY_MODE = "suggest"

# Restart consciousness loop
# System will stop auto-executing and return to suggesting

# Verify mode
curl http://localhost:3001/api/consciousness/status `
  -H "Authorization: Bearer <YOUR_HUB_TOKEN>"
```

### Full Shutdown

```powershell
# Graceful shutdown of all services
python aetherra_os_launcher.py --shutdown

# Or force kill if unresponsive
Get-Process | Where-Object {$_.Name -like "*aetherra*"} | Stop-Process -Force
```

---

## 📈 Success Metrics

### After 24 Hours in Suggest Mode

| Metric                  | Target  | Status |
| ----------------------- | ------- | ------ |
| Consciousness coherence | > 0.7   | ⬜      |
| Homeostasis stability   | > 0.8   | ⬜      |
| Agent success rate      | > 0.7   | ⬜      |
| Memory recall latency   | < 200ms | ⬜      |
| Zero critical failures  | Yes     | ⬜      |
| Suggestions reviewed    | 100%    | ⬜      |

### After 7 Days in Auto Mode

| Metric                              | Target         | Status |
| ----------------------------------- | -------------- | ------ |
| Autopilot success rate              | > 0.85         | ⬜      |
| Self-improvement proposals accepted | > 60%          | ⬜      |
| Code changes (via gate)             | > 5 successful | ⬜      |
| Rollbacks required                  | < 5%           | ⬜      |
| System uptime                       | > 99%          | ⬜      |
| User satisfaction                   | High           | ⬜      |

---

## 📚 Appendix

### A. Token Generation Reference

```powershell
# 128-bit token (staging)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 256-bit token (production)
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### B. Configuration File Locations

```
config.autonomy.staging.json       # Staging settings
config.autonomy.production.json    # Production settings
.env.autonomy.staging              # Staging env vars
.env.autonomy.production           # Production env vars
```

### C. Log File Locations

```
logs/aetherra.log                  # Main OS log
logs/consciousness.log             # Consciousness loop
logs/homeostasis.log               # Maintenance system
logs/agents.log                    # Agent orchestrator
logs/hub.log                       # Hub API
logs/audit.log                     # Security audit trail
```

### D. Quick Reference Commands

```powershell
# Check system status
curl http://localhost:3001/api/kernel/status -H "Authorization: Bearer <TOKEN>"

# Check consciousness status
curl http://localhost:3001/api/consciousness/status -H "Authorization: Bearer <TOKEN>"

# Check homeostasis status
curl http://localhost:3001/api/homeostasis/status -H "Authorization: Bearer <TOKEN>"

# Check agents status
curl http://localhost:3001/api/agents -H "Authorization: Bearer <TOKEN>"

# View metrics
curl http://localhost:3001/metrics

# Emergency stop
curl -X POST http://localhost:3001/api/homeostasis/emergency_stop -H "Authorization: Bearer <TOKEN>"
```

---

## ✅ Final Pre-Launch Checklist

Before setting `AUTONOMY_MODE=auto` in production:

- [ ] All Phase 1-9 steps completed successfully
- [ ] 24+ hours uptime in suggest mode
- [ ] 100+ successful consciousness cycles
- [ ] Zero critical failures
- [ ] All safety rails tested and functional
- [ ] Backup/restore procedure verified
- [ ] Emergency procedures documented and tested
- [ ] Team trained on monitoring and response
- [ ] Rollback plan ready
- [ ] Stakeholders informed and ready

**Sign-off required from:**

- [ ] Technical Lead: ___________________  Date: _______
- [ ] Security Lead: ____________________  Date: _______
- [ ] Operations: _______________________  Date: _______

---

**Aetherra OS - Code Awakened**
*Autonomous, Observable, Safe*
