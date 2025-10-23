# STORM PR-2 Summary — Core OT Implementation

Status: Phase 1 Complete ✅ | Phase 2 Complete ✅

This phase wires a real Optimal Transport (OT) path into the STORM subsystem using the POT library,
with deterministic embeddings, budget-aware behavior, and enriched candidate selection from real memory stores.
It remains feature-flagged and degrades gracefully when unavailable.

## Phase 1: Core OT Computation (Completed)

What shipped

- Deterministic embeddings
  - `_generate_mock_embedding(text, dim=128)` creates reproducible numpy vectors using SHA-256 seeded RNG.
  - `_build_distance_matrix(X, Y)` constructs pairwise Euclidean cost matrices.
- OT computation (POT)
  - Prefers exact EMD; falls back to Sinkhorn if EMD fails.
  - Budget-aware: computes exact cost and marks the call approximate if it exceeds `max_ms_exact` (ms).
- Evidence tags
  - `metadata.evidence_tags.ot` carries a stable min-distance proxy for now (deterministic,
    identical text → 0.0). We keep the true OT plan internally; future phases may expose
    plan-derived cost directly.
  - `coh` and `pers` placeholders are wired per contract (to be enriched in PR-4).
- Hybrid fallback
  - `storm_hybrid` mode annotates results while returning the base fallback items/scores.
- Tests
  - `tests/storm/test_storm_ot.py` (10 tests) covering determinism, distance shape,
    identical/similar behavior, evidence tags, budget flagging, hybrid mode, metrics, and limits.

## Phase 2: Candidate Enrichment & Weighting (Completed)

What shipped

- Real memory candidate fetching
  - `_fetch_candidates()` method fetches real memories from `LyrixaMemorySystem.recall_memories()`
  - Graceful fallback to base_fallback when core memory unavailable
  - Returns empty items/scores for pure STORM mode without core memory (preserves PR-1 skeleton behavior)
- Coarse-to-fine candidate selection
  - `k_coarse` parameter controls initial candidate pool size (default 64)
  - Fetches larger candidate set, then refines to target limit
  - Respects budget constraints from `max_ms_exact` configuration
- Probability mass weighting strategies
  - `_compute_mass_distribution()` supports multiple strategies:
    - `nearest`: All mass on nearest neighbor (Phase 1 behavior)
    - `uniform`: Equal mass across all candidates
    - `importance`: Weighted by relevance scores from memory system
    - `recency`: Weighted by recency (fallback to importance for now)
  - Default: importance-weighted distribution for Phase 2
  - Handles zero scores gracefully with epsilon addition
- Integration with AetherraMemoryEngineAdvanced
  - STORM engine receives `core_memory` reference during initialization
  - Enables real candidate fetching in production environment
  - Maintains backward compatibility with Phase 1 tests
- Tests
  - `tests/storm/test_storm_candidates.py` (15 tests) covering:
    - Real candidate fetching from core memory
    - k_coarse parameter behavior
    - Fallback strategies (base_fallback, pure mode)
    - All four weighting strategies (nearest, uniform, importance, recency)
    - Zero score handling
    - Full recall pipeline integration

Configuration

- Feature flag: `AETHERRA_MEMORY_STORM=1` to enable STORM.
- Backend: `AETHERRA_STORM_OT_BACKEND=auto|pot|keops` (auto→POT; KeOps not wired yet).
- Budget: `AETHERRA_STORM_MAX_MS_EXACT` or `AETHERRA_STORM_MAX_MS` (ms). If exceeded, the call is marked approximate.
- Coarse filtering: `AETHERRA_STORM_K_COARSE=64` (initial candidate pool size before OT refinement).

Usage

- Direct (low-level) usage with core memory

```python
import os, asyncio
from Aetherra.aetherra_core.memory.storm.engine import StormEngine, StormConfig
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem

async def main():
    os.environ["AETHERRA_MEMORY_STORM"] = "1"
    os.environ["AETHERRA_STORM_K_COARSE"] = "128"  # Optional: larger candidate pool

    # Initialize with core memory for real candidate fetching
    core_mem = LyrixaMemorySystem()
    eng = StormEngine(config=StormConfig(enabled=True, k_coarse=128), core_memory=core_mem)

    res = await eng.recall("hello world", limit=5)
    print(res.source, res.metadata["evidence_tags"]["ot"])  # "storm", transport cost proxy
    print(f"Retrieved {len(res.items)} items from real memory")

asyncio.run(main())
```

- Hybrid usage (annotate base results)

```python
base = await eng.recall("hello", limit=3)
res = await eng.recall("hello", limit=3, base_fallback=base)
print(res.source)  # "storm_hybrid"
```

- Testing weighting strategies

```python
# Internal API (subject to change)
import numpy as np
cost_matrix = np.array([[0.5, 0.2, 0.8]])
scores = [0.9, 0.8, 0.7]

# Importance-weighted (default Phase 2)
b = eng._compute_mass_distribution(cost_matrix, scores, strategy="importance")
print(b)  # [0.375, 0.333, 0.292] - proportional to scores

# Uniform distribution
b_uniform = eng._compute_mass_distribution(cost_matrix, scores, strategy="uniform")
print(b_uniform)  # [0.333, 0.333, 0.333]
```

Notes & limitations

- Phase 1: Evidence `ot` value is a min-distance proxy to keep tests and semantics stable;
  we compute real OT plans internally and may expose plan-derived costs later.
- Phase 2: Candidate fetching requires `LyrixaMemorySystem` reference; pure STORM mode without
  core memory returns empty items (preserving PR-1 skeleton behavior).
- Phase 2: Importance weighting is now default strategy; configurable strategy selection coming in future phases.
- Phase 2: Recency weighting not yet implemented, falls back to importance for now.
- No GW (Gromov-Wasserstein) yet; KeOps not wired.
- SQLite persistence for embeddings/cells/overlaps is not yet connected.

Metrics

- Gauges/counters are updated in the in-repo stub collector. Full Prometheus wiring follows later.
- New Phase 2 metrics: candidate fetch attempts, k_coarse effectiveness, weighting strategy usage (future).

Next steps

- PR-3: SQLite persistence for embeddings and cells/overlaps/meta.
- PR-4: TDA persistence scoring and sheaf inconsistency.
- PR-5: TT/MPS compression layer and maintenance cycles.
- Phase 0: Shadow-mode validation and metrics gating before enabling by default.
- Future: Configurable mass distribution strategy via StormConfig.
- Future: True recency-based weighting using memory timestamps.
- Future: Plan-derived cost exposure in evidence tags (vs. min-distance proxy).

Try it

- Run tests for Phase 1:

```powershell
pytest -q -o addopts= tests/storm/test_storm_ot.py
```

- Run tests for Phase 2:

```powershell
pytest -q -o addopts= tests/storm/test_storm_candidates.py
```

- Run full STORM test suite:

```powershell
pytest -q -o addopts= tests/storm
```

- Ensure POT is installed (already listed in `requirements/storm.txt`).
