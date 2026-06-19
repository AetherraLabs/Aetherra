#!/usr/bin/env python3
"""Quick smoke test for STORM skeleton integration"""

import os
import sys

# Test 1: Import storm engine
print("Test 1: Import storm engine...")
try:
    from Aetherra.aetherra_core.memory.storm import StormConfig, StormEngine

    print("  ✓ Storm imports OK")
except Exception as e:
    print(f"  ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Config from env (default off)
print("\nTest 2: Config defaults (flag off)...")
os.environ.pop("AETHERRA_MEMORY_STORM", None)
cfg = StormConfig.from_env()
assert not cfg.enabled, "STORM should be disabled by default"
assert cfg.ot_backend == "auto"
assert cfg.tt_max_rank == 32
print(
    f"  ✓ Config: enabled={cfg.enabled}, backend={cfg.ot_backend}, rank={cfg.tt_max_rank}"
)

# Test 3: Config with flag on
print("\nTest 3: Config with flag enabled...")
os.environ["AETHERRA_MEMORY_STORM"] = "1"
cfg2 = StormConfig.from_env()
assert cfg2.enabled, "STORM should be enabled when flag=1"
print(f"  ✓ Config: enabled={cfg2.enabled}")

# Test 4: StormEngine status (flag off)
print("\nTest 4: StormEngine status (disabled)...")
os.environ.pop("AETHERRA_MEMORY_STORM", None)
engine = StormEngine()
status = engine.status()
assert not status["enabled"], "Engine should report disabled"
assert "backends" in status
assert "selected_backend" in status
print(f"  ✓ Status: {status}")

# Test 5: StormEngine status (flag on)
print("\nTest 5: StormEngine status (enabled)...")
os.environ["AETHERRA_MEMORY_STORM"] = "1"
cfg_on = StormConfig.from_env()
engine_on = StormEngine(config=cfg_on)
status_on = engine_on.status()
assert status_on["enabled"], "Engine should report enabled"
print(
    f"  ✓ Status: enabled={status_on['enabled']}, backend={status_on['selected_backend']}"
)

# Test 6: Recall with no base fallback
print("\nTest 6: Recall (no base)...")
import asyncio

result = asyncio.run(engine_on.recall("test query", limit=5))
assert result.source in ("storm", "storm_hybrid"), (
    f"Expected storm source, got {result.source}"
)
assert isinstance(result.items, list)
assert isinstance(result.scores, list)
assert "storm_meta" in result.metadata
print(
    f"  ✓ Recall: source={result.source}, items={len(result.items)}, meta keys={list(result.metadata.keys())}"
)

# Test 7: Memory engine integration
print("\nTest 7: Memory engine integration (flag off)...")
os.environ.pop("AETHERRA_MEMORY_STORM", None)
from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
)

eng = AetherraMemoryEngineAdvanced()
sys_status = eng.get_system_status()
assert "storm" in sys_status, "System status should include storm block"
assert not sys_status["storm"]["enabled"], "STORM should be disabled by default"
print(f"  ✓ System status storm block: {sys_status['storm']}")

# Test 8: Memory engine integration (flag on)
print("\nTest 8: Memory engine integration (flag on)...")
os.environ["AETHERRA_MEMORY_STORM"] = "1"
eng2 = AetherraMemoryEngineAdvanced()
sys_status2 = eng2.get_system_status()
assert "storm" in sys_status2
assert sys_status2["storm"]["enabled"], "STORM should be enabled when flag=1"
print(f"  ✓ System status storm block: enabled={sys_status2['storm']['enabled']}")

# Test 9: Typed recall integration
print("\nTest 9: Typed recall (flag on, should return storm_hybrid)...")
result2 = asyncio.run(eng2.recall_typed("test query", limit=3))
assert result2.source in ("storm", "storm_hybrid"), (
    f"Expected storm/storm_hybrid, got {result2.source}"
)
print(f"  ✓ Typed recall: source={result2.source}, items={len(result2.items)}")

print("\n" + "=" * 60)
print("✓ All STORM skeleton tests passed!")
print("=" * 60)
