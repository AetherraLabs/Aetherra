# STORM Shadow Mode Quick Start Guide

**Ready to deploy?** Follow these steps to enable STORM in shadow mode (Phase 1).

---

## Prerequisites ✅

- [x] STORM integration complete (Day 10e)
- [x] All tests passing (105/111)
- [x] Documentation reviewed
- [x] Production approval obtained

---

## 5-Minute Setup

### Step 1: Set Environment Variables

**PowerShell (Windows)**:
```powershell
$env:AETHERRA_MEMORY_STORM = "1"
$env:AETHERRA_STORM_SHADOW_MODE = "1"
```

**Bash (Linux/Mac)**:
```bash
export AETHERRA_MEMORY_STORM=1
export AETHERRA_STORM_SHADOW_MODE=1
```

**Or add to `.env` file**:
```bash
AETHERRA_MEMORY_STORM=1
AETHERRA_STORM_SHADOW_MODE=1
```

### Step 2: Verify Configuration

```bash
python tools/deploy_storm_shadow.py --check-only
```

**Expected output**:
```
✅ AETHERRA_MEMORY_STORM=1 ..................... PASS
✅ AETHERRA_STORM_SHADOW_MODE=1 ................ PASS
✅ STORM config loaded ......................... PASS
✅ STORM enabled ............................... PASS
✅ Shadow mode ................................. PASS
```

### Step 3: Start Hub

```bash
python aetherra_hub_server.py
```

**Look for**:
```
✅ Lyrixa memory system initialized
STORM engine initialized (shadow_mode=True)
```

### Step 4: Verify Metrics

```bash
curl http://localhost:3001/metrics | grep storm
```

**Should see**:
```
storm_recalls_total{strategy="storm"} 0
storm_shadow_comparisons_total{agreed="true"} 0
storm_shadow_errors_total 0
...
```

### Step 5: Test Shadow Recall

```python
import asyncio
from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngineAdvanced

async def test():
    engine = AetherraMemoryEngineAdvanced()

    # Store memory
    await engine.remember(
        content="STORM shadow mode test",
        tags=["test"],
        category="validation"
    )

    # Recall (returns baseline, runs STORM in shadow)
    result = await engine.recall_typed(
        query="shadow mode",
        recall_strategy="storm_hybrid",
        limit=5
    )

    print(f"✅ Shadow test complete!")
    print(f"   Source: {result.source}")  # Should be 'hybrid' or 'base'
    print(f"   Items: {len(result.items)}")

asyncio.run(test())
```

---

## Monitoring (Week 1-2)

### Daily Checks

```bash
# 1. Check metrics
curl http://localhost:3001/metrics | grep storm

# 2. Calculate agreement rate
python -c "
import re, requests
r = requests.get('http://localhost:3001/metrics').text
agreed = float(re.search(r'agreed=\"true\"\}\s+(\d+)', r).group(1) or 0)
disagreed = float(re.search(r'agreed=\"false\"\}\s+(\d+)', r).group(1) or 0)
total = agreed + disagreed
rate = (agreed / total * 100) if total > 0 else 0
print(f'Agreement rate: {rate:.1f}%')
print(f'Total comparisons: {int(total)}')
"

# 3. Check status
curl http://localhost:3001/api/memory/status | jq '.storm'
```

### Success Criteria (End of Week 2)

- [ ] Shadow error rate < 1%
- [ ] STORM latency p95 < 500ms
- [ ] Agreement rate > 80%
- [ ] No production impact
- [ ] Metrics collecting properly

---

## Troubleshooting

### "STORM not initializing"

```bash
# Check environment
python -c "import os; print('STORM:', os.getenv('AETHERRA_MEMORY_STORM'))"

# Should print: STORM: 1
```

**Fix**: Set environment variable correctly.

### "No shadow metrics"

```bash
# Trigger recall to generate metrics
python -c "
import asyncio
from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngineAdvanced

async def go():
    engine = AetherraMemoryEngineAdvanced()
    await engine.remember(content='test', tags=['test'], category='test')
    await engine.recall_typed(query='test', recall_strategy='storm_hybrid', limit=5)
    print('Metrics generated!')

asyncio.run(go())
"
```

### "Hub not running"

```bash
# Start Hub
python aetherra_hub_server.py

# Or in background
nohup python aetherra_hub_server.py > hub.log 2>&1 &
```

---

## Next Steps

After 2 weeks of successful shadow mode operation:

1. **Review metrics** - Ensure all success criteria met
2. **Proceed to Phase 2** - Hybrid mode deployment
3. **See full checklist** - `docs/STORM_DEPLOYMENT_CHECKLIST.md`

---

## Emergency Rollback

If issues occur:

```bash
# Disable STORM immediately
export AETHERRA_MEMORY_STORM=0

# Restart Hub
pkill -f aetherra_hub_server.py
python aetherra_hub_server.py
```

---

## Resources

- **Deployment Checklist**: `docs/STORM_DEPLOYMENT_CHECKLIST.md`
- **Integration Report**: `docs/STORM_FINAL_INTEGRATION_REPORT.md`
- **Security Audit**: `docs/STORM_SECURITY_VERIFICATION.md`
- **A/B Testing Results**: `docs/STORM_AB_TESTING_RESULTS.md`
- **README**: STORM Memory System section

---

**Questions?** See full deployment checklist or contact STORM team.

**Ready?** Run `python tools/deploy_storm_shadow.py` to begin! 🚀
