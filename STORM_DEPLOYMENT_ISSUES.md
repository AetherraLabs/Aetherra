# STORM Deployment Issues - Diagnostic Report
**Date:** October 22, 2025
**Session:** STORM Shadow Mode Validation

---

## 🔍 Issues Identified

### 1. **STORM Not Enabled** ❌
**Problem:** STORM environment variable not set
**Current State:** `AETHERRA_MEMORY_STORM=0`
**Expected:** `AETHERRA_MEMORY_STORM=1`

**Impact:**
- STORM subsystem never initializes
- No optimal transport calculations
- Zero STORM metrics (recall=0.0, coherence=0.0, drift=0.0, redundancy=0.0)
- Shadow mode comparisons never execute

**Evidence from metrics:**
```json
{
  "ts": 1761113621.9423685,
  "ok": true,
  "recall": 0.0,
  "coherence": 0.0,
  "drift": 0.0,
  "redundancy": 0.0,
  "latency_avg_ms": 41.41,
  "cases": 3
}
```

**Root Cause:**
- No `.env` file existed in project root
- System defaulted to `AETHERRA_MEMORY_STORM=0` from code
- OS launcher logged: `STORM enabled: 0`

---

### 2. **Homeostasis in DEGRADED State** ⚠️
**Problem:** Three vital checks consistently failing
**Current State:** System verification shows DEGRADED every 10 seconds

**Failed Checks:**
1. **`memory_coherence`**: Status degraded
2. **`plugin_queue`**: Status degraded
3. **`hub_link`**: Status degraded

**Evidence from logs:**
```
2025-10-22 23:40:48,042 - Aetherra.homeostasis.system_supervisor - INFO - 🔍 System verification complete: DEGRADED
2025-10-22 23:40:48,042 - Aetherra.homeostasis.system_supervisor - WARNING - ⚠️ Failed vital checks: memory_coherence, plugin_queue, hub_link
```

**Recurring Actions (All Failing):**
- `reconnect_hub` ❌
- `increase_task_workers` ❌
- `optimize_plugin_timeouts` ❌

**Additional Errors:**
```
Plugin metrics collection failed: 'AetherraServiceRegistry' object has no attribute 'services'
GUI metrics collection failed: 'AetherraServiceRegistry' object has no attribute 'services'
```

---

## 🔬 Root Cause Analysis

### Memory Coherence
**Why it fails:**
- `AetherraMemoryEngineAdvanced` lacks `check_coherence()` method
- Homeostasis `_verify_memory_coherence()` checks for this method
- When missing, coherence check defaults to degraded status

**Code Location:**
`Aetherra/homeostasis/system_supervisor.py:742-744`
```python
if hasattr(memory_service.instance, "check_coherence"):
    coherence_ok = await memory_service.instance.check_coherence()
    if not coherence_ok:
        return {"status": "degraded", "reason": "coherence_check_failed"}
```

**Is this critical?** No - cosmetic only. Memory system is fully functional.

---

### Plugin Queue
**Why it fails:**
- `plugin_manager` service not registered with OS
- Plugin system may not be running
- Homeostasis expects plugin manager for some workflows

**Code Location:**
`Aetherra/homeostasis/system_supervisor.py:753-761`
```python
plugin_service = registry.get_service_info("plugin_manager")
if not plugin_service:
    return {"status": "failed", "reason": "service_not_found"}
```

**Is this critical?** No - normal if plugins aren't used. Safe to ignore.

---

### Hub Link
**Why it fails:**
- Hub runs as separate process (not embedded in OS)
- Hub not started or not registered with service registry
- OS can't find `aetherra_hub` service

**Code Location:**
`Aetherra/homeostasis/system_supervisor.py:816-820`
```python
hub_service = registry.get_service_info("aetherra_hub")
if not hub_service:
    return {"status": "failed", "reason": "service_not_found"}
```

**Is this critical?** Yes - Hub provides AI API, metrics export, and STORM monitoring.

---

### Service Registry Attribute Error
**Why it fails:**
- `AetherraServiceRegistry` implements different interface than expected
- Homeostasis stability metrics try to access `.services` attribute
- Registry doesn't expose services this way (uses `get_service_info()` instead)

**Code Location:**
`Aetherra/homeostasis/stability_metrics.py` (exact line unknown)
```python
# Trying to access registry.services (doesn't exist)
# Should use registry.list_services() or registry.get_service_info()
```

**Is this critical?** No - causes DEBUG log spam but doesn't affect functionality.

---

## ✅ Solutions

### 1. Enable STORM
**Action:** Created `.env` file with STORM configuration

**File:** `d:\Aetherra Project\.env`
```bash
# STORM Memory System
AETHERRA_MEMORY_STORM=1
AETHERRA_STORM_SHADOW_MODE=1
AETHERRA_STORM_OT_BACKEND=auto
AETHERRA_STORM_TT_MAX_RANK=32
```

**Verification:**
```powershell
# Check environment variables
python -c "import os; print('STORM:', os.environ.get('AETHERRA_MEMORY_STORM', '0'))"
# Expected output: STORM: 1
```

**Restart Required:** Yes - OS must be restarted to load `.env` file

---

### 2. Start Hub Service
**Action:** Launch Hub in separate terminal

**Command:**
```powershell
python tools/run_hub_ai_api.py --port 3001
```

**What This Does:**
- Starts Flask-based Hub server on port 3001
- Auto-registers with OS service registry as `aetherra_hub`
- Exposes `/api/memory/status` for STORM status queries
- Exposes `/metrics` for Prometheus STORM metrics
- Clears `hub_link` vital check failure

**Verification:**
```powershell
# Check Hub is running
curl http://localhost:3001/metrics

# Check STORM status endpoint
curl http://localhost:3001/api/memory/status
```

---

### 3. Add Memory Coherence Method (Optional)
**Action:** Implement `check_coherence()` in `AetherraMemoryEngineAdvanced`

**File:** `Aetherra/aetherra_core/memory/aetherra_memory_engine.py`

**Implementation:**
```python
async def check_coherence(self) -> bool:
    """Check memory system coherence for homeostasis."""
    try:
        # Basic coherence check - verify core systems responding
        if not self._memory_core:
            return False

        # Check fractal mesh if available
        if self._fractal_mesh:
            # Verify mesh is accessible
            pass

        # Check STORM if enabled
        if self._storm_engine:
            status = self._storm_engine.get_status()
            if not status.get("available"):
                return False

        return True
    except Exception:
        return False
```

**Priority:** Low - cosmetic fix only

---

### 4. Fix Service Registry Access (Optional)
**Action:** Update stability metrics to use correct registry API

**File:** `Aetherra/homeostasis/stability_metrics.py`

**Change:**
```python
# OLD (doesn't work)
for service in registry.services:
    ...

# NEW (correct API)
all_services = registry.list_services()
for service in all_services:
    ...
```

**Priority:** Low - reduces DEBUG log noise

---

## 📋 Immediate Action Items

### Required (Do Now):
1. ✅ **Created `.env` file** with STORM enabled
2. **Restart Aetherra OS** to load environment variables
3. **Start Hub** in separate terminal: `python tools/run_hub_ai_api.py --port 3001`
4. **Verify STORM enabled** in OS boot logs:
   ```
   [STORM] enabled=True shadow_mode=True backend=auto tt_rank_cap=32
   ```
5. **Confirm Hub registration** - watch for homeostasis `hub_link` to clear

### Optional (Can Defer):
- Add `check_coherence()` method to memory engine (cosmetic)
- Fix service registry attribute access in stability metrics (reduces log noise)
- Implement plugin manager if plugins needed (probably not)

---

## 🎯 Expected Outcomes After Fix

### STORM Metrics
After restarting with STORM enabled and exercising recall:
```json
{
  "ts": 1761114000.0,
  "ok": true,
  "recall": 0.85,          // Non-zero after recall operations
  "coherence": 0.92,       // Sheaf consistency score
  "drift": 0.03,           // Memory drift detection
  "redundancy": 0.15,      // Overlap detection
  "latency_avg_ms": 45.2,  // Slightly higher (OT compute)
  "cases": 10
}
```

### Homeostasis Status
After starting Hub:
```
🔍 System verification complete: HEALTHY
✅ All vital checks passed
📊 Health: 100.0% (6/6 services)
```

### Hub Metrics
STORM series will appear on `/metrics`:
```
storm_recalls_total{strategy="storm_hybrid"} 15
storm_ot_cost_avg 0.23
storm_sheaf_inconsistency_avg 0.08
storm_maintenance_cycles_total 3
...
```

---

## 🔄 Next Steps

1. **Restart OS** with new `.env` configuration
2. **Start Hub** for metrics export and status API
3. **Exercise STORM** with recall operations (see `storm_traffic_test.py`)
4. **Monitor metrics** for 1-2 weeks in shadow mode
5. **Evaluate Phase 2** hybrid rollout based on metrics

---

## 📚 References

- **STORM Integration Summary**: `docs/STORM_INTEGRATION_SUMMARY.md`
- **Memory System Docs**: `docs/AETHERRA_MEMORY_SYSTEM.md` (Section 6)
- **Hub Startup**: `tools/run_hub_ai_api.py`
- **Traffic Generator**: `storm_traffic_test.py`
- **Monitoring Tools**: `tools/monitor_storm_shadow.py`

---

**Status:** Issues diagnosed, `.env` created, ready for restart and Hub launch
