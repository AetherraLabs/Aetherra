# Aetherra Hot Module Reload (HMR) Guide

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This guide explains Aetherra's Hot Module Reload (HMR) system, which enables dynamic reloading of system components without requiring a full OS restart. HMR is designed for development, testing, and controlled production updates.

## Purpose and scope

- Understand Hot Module Reload concepts and architecture
- Enable and configure HMR for different environments
- Reload specific system components dynamically
- Implement state handoff for stateful components
- Monitor HMR operations and metrics
- Troubleshoot HMR failures and rollbacks

## What is Hot Module Reload?

**Hot Module Reload (HMR)** allows replacing running system components with updated versions while the OS continues operating. This enables:

- **Rapid iteration** during development
- **Zero-downtime updates** for non-critical components
- **A/B testing** of algorithm improvements
- **Quick bug fixes** without service interruption

### Supported Components

| Component           | Target Name      | Typical Use Case              |
| ------------------- | ---------------- | ----------------------------- |
| **Aetherra Engine** | `engine`         | Core reasoning engine updates |
| **Memory Adapter**  | `adapter:memory` | Memory system improvements    |
| **Plugin Adapter**  | `adapter:plugin` | Plugin system changes         |
| **Lyrixa Chat**     | `lyrixa_chat`    | Chat interface updates        |

---

## HMR Architecture

### Reload Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                      HMR Reload Flow                         │
└─────────────────────────────────────────────────────────────┘

1. PREPARE
   ├─ Load shadow module from source
   ├─ Verify source is allowed (if strict mode)
   └─ Create new instance

2. VERIFY
   ├─ Run health probe on shadow instance
   └─ Validate basic functionality

3. QUIESCE
   ├─ Drain in-flight work for target
   ├─ Wait for quiet period (timeout: 30s)
   └─ Block new work to target

4. STATE HANDOFF (Optional)
   ├─ Export state from current instance
   └─ Import state into shadow instance

5. SWAP
   ├─ Replace current with shadow
   ├─ Broadcast HMR_SWAP event
   └─ Update kernel references

6. POST-SWAP HEALTH
   ├─ Verify new instance is healthy
   ├─ If healthy: Resume work
   └─ If unhealthy: ROLLBACK

7. RESUME or ROLLBACK
   ├─ Success: Resume normal operations
   └─ Failure: Restore previous instance
```

### HMR Controller

The `HMRController` (defined in `aetherra_hmr_controller.py`) orchestrates the reload process:

```python
class HMRController:
    """Hot Module Reload controller service."""

    def __init__(self, registry, kernel, strict: bool = False):
        self.registry = registry      # Service registry for events
        self.kernel = kernel          # Kernel for component access
        self.strict = bool(strict)    # Strict mode enforces source allowlist
        self.allowed_sources = set()  # Approved source paths/modules
        self.audit_path = ...         # Audit log location
```

---

## Configuration

### Environment Variables

**Enable HMR:**

```bash
# Enable HMR system
export AETHERRA_HMR_ENABLED=1

# HMR mode: safe (default) or force
export AETHERRA_HMR_MODE=safe

# Enable auto-reload on file changes (development)
export AETHERRA_HMR_AUTO_RELOAD=1
```

**Security and auditing:**

```bash
# Strict mode: require source allowlist
export AETHERRA_HMR_STRICT=1

# Comma-separated allowed sources
export AETHERRA_HMR_ALLOWED_SOURCES="Aetherra.engine,Aetherra.adapters,/opt/aetherra/plugins/*"

# Audit log path
export AETHERRA_HMR_AUDIT_PATH=".aetherra/hmr_audit.jsonl"

# Audit rotation settings
export AETHERRA_HMR_AUDIT_MAX_BYTES=5242880  # 5 MB
export AETHERRA_HMR_AUDIT_MAX_BACKUPS=3
```

### Configuration Profiles

**Development (permissive):**

```bash
export AETHERRA_HMR_ENABLED=1
export AETHERRA_HMR_MODE=safe
export AETHERRA_HMR_AUTO_RELOAD=1
export AETHERRA_HMR_STRICT=0
```

**Staging (monitored):**

```bash
export AETHERRA_HMR_ENABLED=1
export AETHERRA_HMR_MODE=safe
export AETHERRA_HMR_STRICT=1
export AETHERRA_HMR_ALLOWED_SOURCES="Aetherra.engine,Aetherra.adapters"
export AETHERRA_HMR_AUDIT_PATH="/var/log/aetherra/hmr_audit.jsonl"
```

**Production (restricted):**

```bash
export AETHERRA_HMR_ENABLED=0  # Disabled by default
# Or if enabled:
export AETHERRA_HMR_ENABLED=1
export AETHERRA_HMR_MODE=safe
export AETHERRA_HMR_STRICT=1
export AETHERRA_HMR_ALLOWED_SOURCES="Aetherra.engine"
export AETHERRA_HMR_AUDIT_PATH="/var/log/aetherra/hmr_audit.jsonl"
```

---

## Usage

### Triggering HMR via API

**Endpoint:** `POST /api/selfimprove/apply`

```bash
curl -X POST http://localhost:3001/api/selfimprove/apply \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "proposal_id": "prop_12345",
    "target": "engine",
    "source": "Aetherra.engine_v2",
    "mode": "safe"
  }'
```

**Response:**

```json
{
  "ok": true,
  "applied": true,
  "swap_ms": 245,
  "restart_required": false
}
```

### Triggering HMR via Kernel Task

**Submit kernel task:**

```python
import asyncio
from aetherra_kernel_loop import get_kernel

async def reload_engine():
    kernel = get_kernel()

    result = await kernel.enqueue_task({
        "type": "hmr_reload",
        "data": {
            "target": "engine",
            "source": "Aetherra.engine_improved",
            "mode": "safe"
        }
    })

    print(f"HMR result: {result}")

# Run
asyncio.run(reload_engine())
```

### Checking HMR Status

**Via API:**

```bash
curl http://localhost:3001/api/selfimprove/status
```

**Via kernel task:**

```python
result = await kernel.enqueue_task({
    "type": "hmr_status"
})
print(result["state"])
```

**Response:**

```json
{
  "ok": true,
  "state": {
    "status": "swapped",
    "target": "engine",
    "swap_ms": 245
  }
}
```

---

## Implementing State Handoff

For stateful components, implement `export_state` and `import_state` methods:

### Export State (Old Instance)

```python
class MyAdapter:
    def __init__(self):
        self.cache = {}
        self.counters = {"requests": 0, "errors": 0}

    def export_state(self) -> dict:
        """Export state for HMR handoff."""
        return {
            "cache": self.cache.copy(),
            "counters": self.counters.copy(),
            "timestamp": time.time()
        }
```

### Import State (New Instance)

```python
class MyAdapterV2:
    def __init__(self):
        self.cache = {}
        self.counters = {"requests": 0, "errors": 0}

    def import_state(self, state: dict):
        """Import state from previous instance."""
        self.cache = state.get("cache", {})
        self.counters = state.get("counters", {})
        logger.info(f"[HMR] Imported state from {state.get('timestamp')}")
```

### Async State Handoff

For async components:

```python
class AsyncAdapter:
    async def export_state(self) -> dict:
        """Async state export."""
        # Finalize any async operations
        await self.flush_pending()

        return {
            "state": self.current_state,
            "queue_size": len(self.queue)
        }

    async def import_state(self, state: dict):
        """Async state import."""
        self.current_state = state.get("state")

        # Reinitialize if needed
        await self.initialize_from_state(state)
```

---

## HMR Modes

### Safe Mode (Default)

**Behavior:**
- Requires quiesce timeout to succeed
- Fails if health checks don't pass
- Automatic rollback on post-swap failure

**Use when:**
- Production environment
- State preservation is critical
- Safety over speed

```python
{
    "target": "engine",
    "source": "Aetherra.engine_v2",
    "mode": "safe"  # Default
}
```

### Force Mode

**Behavior:**
- Proceeds even if quiesce times out
- May interrupt in-flight operations
- Still performs health checks

**Use when:**
- Emergency updates required
- Development/testing
- Target is known to be stateless

```python
{
    "target": "adapter:memory",
    "source": "Aetherra.memory_adapter_fixed",
    "mode": "force"
}
```

**⚠️ Warning:** Force mode may cause request failures for in-flight operations.

---

## Monitoring HMR Operations

### Audit Log

HMR operations are logged to `AETHERRA_HMR_AUDIT_PATH`:

**Log format (JSONL):**

```json
{"timestamp": 1730476800, "event": "swapped", "target": "engine", "source": "Aetherra.engine_v2", "ok": true, "swap_ms": 245}
{"timestamp": 1730476850, "event": "load_failed", "target": "adapter:memory", "source": "bad_module", "ok": false}
{"timestamp": 1730476900, "event": "post_swap_failed", "target": "lyrixa_chat", "source": "Aetherra.lyrixa_v2", "ok": false}
```

### Metrics

HMR exposes Prometheus metrics via the Hub:

**Metrics available:**

```
# HMR attempts
aetherra_hmr_attempts_total{target="engine"}

# HMR successes
aetherra_hmr_successes_total{target="engine"}

# HMR rollbacks
aetherra_hmr_rollbacks_total{target="engine"}

# HMR swap duration
aetherra_hmr_swap_duration_ms{target="engine"}
```

**Query in Prometheus:**

```promql
# Success rate
rate(aetherra_hmr_successes_total[5m]) / rate(aetherra_hmr_attempts_total[5m])

# Average swap time
avg(aetherra_hmr_swap_duration_ms) by (target)

# Rollback rate
rate(aetherra_hmr_rollbacks_total[5m])
```

### Events

HMR broadcasts events via the Service Registry:

| Event          | When           | Payload                            |
| -------------- | -------------- | ---------------------------------- |
| `HMR_PREPARE`  | Before quiesce | `{"target": "engine"}`             |
| `HMR_SWAP`     | After swap     | `{"target": "engine", "ok": true}` |
| `HMR_ROLLBACK` | On failure     | `{"target": "engine"}`             |

**Subscribe to HMR events:**

```python
async def hmr_listener(event):
    if event["type"] == "HMR_SWAP":
        target = event["payload"]["target"]
        ok = event["payload"]["ok"]
        logger.info(f"[HMR] Swap {target}: {'success' if ok else 'failed'}")

# Register listener
await registry.subscribe("HMR_SWAP", hmr_listener)
```

---

## Troubleshooting

### Common Issues

#### 1. Source Not Allowed

**Error:**

```json
{"ok": false, "error": "source_not_allowed"}
```

**Cause:** Source module/path not in `AETHERRA_HMR_ALLOWED_SOURCES`

**Solution:**

```bash
# Add source to allowlist
export AETHERRA_HMR_ALLOWED_SOURCES="Aetherra.engine,Aetherra.adapters,your_module"
```

#### 2. Load Failed

**Error:**

```json
{"ok": false, "error": "load_failed"}
```

**Causes:**
- Module doesn't exist
- Syntax error in source file
- Missing dependencies

**Solutions:**

```bash
# Verify module exists
python -c "import your_module"

# Check syntax
python -m py_compile your_module.py

# Install dependencies
pip install -r requirements.txt
```

#### 3. Probe Failed

**Error:**

```json
{"ok": false, "error": "probe_failed"}
```

**Cause:** Shadow instance failed health check

**Solution:**

Ensure new instance has `get_status()` method:

```python
class MyAdapter:
    def get_status(self):
        """Health check for HMR."""
        return {
            "healthy": True,
            "version": "2.0"
        }
```

#### 4. Quiesce Timeout

**Error:**

```json
{"ok": false, "error": "quiesce_timeout"}
```

**Cause:** Target didn't drain work within 30 seconds

**Solutions:**

- Wait for quieter period
- Use `mode: force` (if safe)
- Increase timeout in kernel implementation

#### 5. State Import Failed (Strict Mode)

**Error:**

```json
{"ok": false, "error": "state_import_failed"}
```

**Cause:** `import_state()` raised exception in strict mode

**Solution:**

Fix `import_state()` implementation:

```python
def import_state(self, state: dict):
    try:
        self.cache = state.get("cache", {})
        self.counters = state.get("counters", {})
    except Exception as e:
        logger.error(f"Failed to import state: {e}")
        # Initialize with defaults
        self.cache = {}
        self.counters = {}
```

#### 6. Post-Swap Failed

**Error:**

```json
{"ok": false, "error": "post_swap_failed"}
```

**Cause:** Health check failed after swap

**Solution:**

- Check kernel status endpoint
- Review system logs for errors
- Verify new instance is compatible

### Debug Mode

Enable verbose HMR logging:

```python
import logging
logging.getLogger("aetherra_hmr_controller").setLevel(logging.DEBUG)
```

Or set environment variable:

```bash
export AETHERRA_LOG_LEVEL=DEBUG
```

---

## Best Practices

### Development

✅ **Enable HMR with auto-reload:**

```bash
export AETHERRA_HMR_ENABLED=1
export AETHERRA_HMR_AUTO_RELOAD=1
export AETHERRA_HMR_MODE=safe
```

✅ **Test HMR before committing:**

```bash
# Test reload
curl -X POST http://localhost:3001/api/selfimprove/apply \
  -H "Content-Type: application/json" \
  -d '{"target": "engine", "source": "Aetherra.engine_dev"}'
```

✅ **Implement state handoff for stateful components**

❌ **Don't rely on HMR for schema changes** - Use migrations

### Staging

✅ **Enable strict mode:**

```bash
export AETHERRA_HMR_STRICT=1
export AETHERRA_HMR_ALLOWED_SOURCES="Aetherra.engine,Aetherra.adapters"
```

✅ **Monitor audit logs:**

```bash
tail -f .aetherra/hmr_audit.jsonl
```

✅ **Test state handoff with production-like data**

### Production

✅ **Disable HMR by default:**

```bash
export AETHERRA_HMR_ENABLED=0
```

✅ **If enabled, use strict allowlist:**

```bash
export AETHERRA_HMR_ENABLED=1
export AETHERRA_HMR_STRICT=1
export AETHERRA_HMR_ALLOWED_SOURCES="Aetherra.engine"
```

✅ **Require approval for HMR operations**

✅ **Monitor metrics and alerts:**

```promql
# Alert on high rollback rate
rate(aetherra_hmr_rollbacks_total[5m]) > 0.1
```

❌ **Don't use force mode in production**

❌ **Don't reload critical components during peak hours**

---

## Advanced Topics

### Custom Health Probes

Implement custom health checks for shadow instances:

```python
class AdvancedAdapter:
    async def get_status(self):
        """Comprehensive health check."""
        # Check database connection
        db_ok = await self.db.ping()

        # Check cache
        cache_ok = self.cache.is_connected()

        # Run smoke tests
        test_ok = await self.run_smoke_tests()

        return {
            "healthy": db_ok and cache_ok and test_ok,
            "details": {
                "database": db_ok,
                "cache": cache_ok,
                "tests": test_ok
            }
        }
```

### Gradual Rollout

Implement progressive rollout with feature flags:

```python
class GradualEngineAdapter:
    def __init__(self):
        self.rollout_percentage = 0  # Start at 0%

    async def process(self, request):
        # Use new logic for percentage of requests
        if random.random() < self.rollout_percentage:
            return await self.process_v2(request)
        else:
            return await self.process_v1(request)

    def increase_rollout(self, percentage: float):
        """Gradually increase to new version."""
        self.rollout_percentage = min(1.0, percentage)
```

### Coordinated HMR

Reload multiple components in sequence:

```python
async def coordinated_reload():
    """Reload multiple components with dependencies."""
    # 1. Reload memory adapter first
    result1 = await hmr_reload("adapter:memory", "Aetherra.memory_v2")
    if not result1["ok"]:
        return {"error": "memory reload failed"}

    # 2. Reload engine (depends on memory)
    result2 = await hmr_reload("engine", "Aetherra.engine_v2")
    if not result2["ok"]:
        # Rollback memory too
        await hmr_reload("adapter:memory", "Aetherra.memory_v1")
        return {"error": "engine reload failed"}

    return {"ok": True}
```

---

## Security Considerations

### Source Allowlist

**Always use allowlist in production:**

```bash
export AETHERRA_HMR_STRICT=1
export AETHERRA_HMR_ALLOWED_SOURCES="Aetherra.engine,Aetherra.adapters.memory"
```

### Code Signing

Verify module signatures before HMR:

```python
def verify_signature(source: str) -> bool:
    """Verify module signature before reload."""
    sig_path = f"{source}.sig"
    if not os.path.exists(sig_path):
        return False

    # Verify signature
    return verify_file_signature(source, sig_path)
```

### Audit Trail

Maintain comprehensive audit logs:

```json
{
  "timestamp": 1730476800,
  "event": "swapped",
  "target": "engine",
  "source": "Aetherra.engine_v2",
  "user": "admin@aetherraalabs.com",
  "ip": "10.0.1.100",
  "ok": true,
  "swap_ms": 245
}
```

### Rate Limiting

Prevent HMR abuse:

```python
# Limit HMR operations per hour
MAX_HMR_PER_HOUR = 5
```

---

## Related Documentation

- [AETHERRA_SELF_IMPROVEMENT_API.md](./AETHERRA_SELF_IMPROVEMENT_API.md) - API for triggering HMR
- [AETHERRA_MAINTENANCE_SYSTEM.md](./AETHERRA_MAINTENANCE_SYSTEM.md) - Maintenance system integration
- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - HMR troubleshooting
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - HMR in production
- [AETHERRA_HUB_API_REFERENCE.md](./AETHERRA_HUB_API_REFERENCE.md) - API endpoints

---

Status: ✅ Complete - Comprehensive Hot Module Reload guide

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
