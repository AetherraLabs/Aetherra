# STORM PR-2: Algorithm Implementation Plan

> **Status:** Planning Phase
> **Target:** Real OT/GW implementation with POT backend
> **Prerequisites:** PR-1 complete ✅, POT library installed ✅

---

## Scope Overview

**Goal:** Replace stub recall logic with real Optimal Transport (OT) and Gromov-Wasserstein (GW) algorithms using the POT library.

**What's IN scope:**
- Implement real OT distance computation using `ot.emd2()` or `ot.sinkhorn2()`
- Implement GW distance computation using `ot.gromov_wasserstein2()`
- Mock embedding generation for query and memory cells (deterministic, SHA-256 seeded)
- Distance matrix construction from embeddings
- Budget-aware recall with `max_ms_exact` and `max_k_exact` enforcement
- Metrics recording for OT costs, latency, exact vs. approximate counts
- Integration tests with real recall flows
- Documentation updates

**What's OUT of scope (defer to later PRs):**
- SQLite persistence (PR-3)
- TDA persistence scoring (PR-4)
- Sheaf inconsistency computation (PR-4)
- TT/MPS compression (PR-5)
- Real embeddings (beyond mock deterministic generation)
- KeOps GPU backend (PR-6)
- Maintenance cycles (PR-7)

---

## Algorithm Design

### 1. Embedding Generation (Mock, Deterministic)

Since we don't have real embeddings yet, we'll use deterministic mock embeddings:

```python
def _generate_mock_embedding(text: str, dim: int = 128) -> np.ndarray:
    """Generate deterministic mock embedding using SHA-256 seeded PRNG."""
    seed = int.from_bytes(hashlib.sha256(text.encode()).digest()[:4], 'big')
    rng = np.random.RandomState(seed)
    # Generate unit-normalized vector
    vec = rng.randn(dim)
    return vec / np.linalg.norm(vec)
```

**Properties:**
- Deterministic: same text → same embedding
- Normalized: all embeddings have unit norm
- High-dimensional: 128-d by default (configurable)
- Fast: hash-based seeding

### 2. Distance Matrix Construction

For OT, we need a cost matrix `M[i,j]` = distance between candidate cell `i` and query embedding.

```python
def _build_distance_matrix(
    query_emb: np.ndarray,
    cell_embs: List[np.ndarray]
) -> np.ndarray:
    """Build cost matrix for OT. Shape: (n_cells, 1) → broadcasted to (n_cells, 1)."""
    # Compute L2 distances
    M = np.array([np.linalg.norm(query_emb - cell_emb) for cell_emb in cell_embs])
    return M.reshape(-1, 1)  # Column vector for single query
```

For **Gromov-Wasserstein** (inter-structure comparison), we'd compute two distance matrices (one for query neighborhood, one for cell neighborhood) and use `ot.gromov_wasserstein2()`.

### 3. OT Computation

**Exact OT (EMD):**
```python
transport_cost = ot.emd2(a, b, M)
```
- `a`: source distribution (uniform over candidates)
- `b`: target distribution (single point for query)
- `M`: cost matrix
- Returns: scalar Wasserstein distance

**Approximate OT (Sinkhorn):**
```python
transport_cost = ot.sinkhorn2(a, b, M, reg=0.1)
```
- Same inputs, but with entropic regularization `reg`
- Faster convergence, approximate solution
- Good for large candidate sets

### 4. Budget-Aware Recall Flow

```python
async def recall(
    self,
    query: str,
    limit: int = 5,
    base_fallback: Optional[MemoryRecallResult] = None
) -> MemoryRecallResult:
    # 1. Generate query embedding
    query_emb = self._generate_mock_embedding(query)

    # 2. Get candidate cells (from base_fallback or empty stub)
    candidates = base_fallback.items if base_fallback else []

    # 3. Generate embeddings for candidates
    cell_embs = [self._generate_mock_embedding(c.content) for c in candidates]

    # 4. Build distance matrix
    M = self._build_distance_matrix(query_emb, cell_embs)

    # 5. Decide exact vs. approximate
    use_exact = len(candidates) <= self._config.max_k_exact

    # 6. Compute OT distances with timeout
    start = time.perf_counter()
    scores = []
    for i, cell_emb in enumerate(cell_embs):
        if use_exact:
            # Exact EMD
            a = np.array([1.0])
            b = np.array([1.0])
            cost = ot.emd2(a, b, M[i:i+1, :])
        else:
            # Sinkhorn
            a = np.array([1.0])
            b = np.array([1.0])
            cost = ot.sinkhorn2(a, b, M[i:i+1, :], reg=0.1)
        scores.append(-cost)  # Negative for sorting (lower cost = better match)

        # Check budget
        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms > self._config.max_ms_exact:
            # Switch to approximate for remaining
            use_exact = False

    # 7. Sort by score, take top-k
    sorted_indices = np.argsort(scores)[::-1][:limit]
    top_items = [candidates[i] for i in sorted_indices]
    top_scores = [scores[i] for i in sorted_indices]

    # 8. Build result
    result = MemoryRecallResult(
        items=top_items,
        source="storm" if not base_fallback else "storm_hybrid",
        scores=top_scores,
        metadata={
            "strategy": "ot_emd" if use_exact else "ot_sinkhorn",
            "storm": {
                "transport_cost_avg": float(np.mean([abs(s) for s in top_scores])),
                "exact_ot_used": use_exact,
                "candidate_count": len(candidates),
                "elapsed_ms": int((time.perf_counter() - start) * 1000)
            }
        }
    )

    # 9. Record metrics
    self._metrics.record_approximate_recall()
    self._metrics.record_ot_cost(result.metadata["storm"]["transport_cost_avg"])
    self._metrics.record_recall_latency_p95(result.metadata["storm"]["elapsed_ms"])

    return result
```

---

## Implementation Checklist

### Phase 1: Core OT Implementation
- [ ] Add `_generate_mock_embedding()` method to `StormEngine`
- [ ] Add `_build_distance_matrix()` helper
- [ ] Replace stub `recall()` logic with real OT computation
- [ ] Implement exact EMD path (`ot.emd2`)
- [ ] Implement approximate Sinkhorn path (`ot.sinkhorn2`)
- [ ] Add budget enforcement (`max_ms_exact`, `max_k_exact`)

### Phase 2: Evidence Tags
- [ ] Compute `ot:transport_cost` from OT distance
- [ ] Add placeholder `coh:sheaf_coherence` (1.0 for now, real in PR-4)
- [ ] Add placeholder `pers:persistence_bonus` (0.0 for now, real in PR-4)
- [ ] Wire evidence tags into `MemoryRecallResult.metadata.storm`

### Phase 3: Metrics Integration
- [ ] Record `ot_cost_avg` from computed distances
- [ ] Record `recall_latency_ms_p95` from timing
- [ ] Update `approximate_recalls_total` counter
- [ ] Add flag for exact vs. approximate in metadata

### Phase 4: Testing
- [ ] Create `tests/storm/test_storm_ot.py` with OT-specific tests
- [ ] Test exact OT with small candidate sets
- [ ] Test Sinkhorn with large candidate sets
- [ ] Test budget enforcement (timeout switching)
- [ ] Test deterministic embedding generation (reproducibility)
- [ ] Test score ordering (lower cost = better rank)
- [ ] Integration test with `AetherraMemoryEngineAdvanced.recall_typed()`

### Phase 5: Documentation
- [ ] Update `docs/STORM_PR2_SUMMARY.md` (create)
- [ ] Update `docs/STORM_INTEGRATION_PLAN.md` header to show PR-2 status
- [ ] Add algorithm notes to `docs/AETHERRA_MEMORY_SYSTEM.md`
- [ ] Document embedding generation strategy (mock deterministic)

---

## Test Strategy

### Unit Tests (OT Logic)
```python
@pytest.mark.asyncio
async def test_ot_exact_small_set():
    """Test exact EMD with small candidate set."""
    engine = StormEngine(StormConfig(enabled=True, max_k_exact=10))

    # Create mock base result with 5 items
    base = MemoryRecallResult(
        items=[
            Memory(id=f"m{i}", content=f"test content {i}", ...)
            for i in range(5)
        ],
        source="core",
        scores=[0.5] * 5,
        metadata={}
    )

    result = await engine.recall("test query", limit=3, base_fallback=base)

    assert len(result.items) == 3
    assert result.metadata["storm"]["exact_ot_used"] is True
    assert "transport_cost_avg" in result.metadata["storm"]
```

### Integration Tests (Full Recall Flow)
```python
@pytest.mark.asyncio
async def test_storm_recall_via_memory_engine():
    """Test STORM recall through AetherraMemoryEngineAdvanced."""
    import os
    os.environ["AETHERRA_MEMORY_STORM"] = "1"

    engine = AetherraMemoryEngineAdvanced()

    # Store some memories
    await engine.remember("Paris is the capital of France", tags=["geography"])
    await engine.remember("Berlin is the capital of Germany", tags=["geography"])

    # Recall with STORM
    result = await engine.recall_typed("capital of France", strategy="hybrid")

    assert result.source == "storm_hybrid"
    assert len(result.items) > 0
    assert "storm" in result.metadata
```

---

## Open Questions & Decisions

### Q1: Embedding dimension?
**Decision:** Start with 128-d for mock embeddings. Configurable via `AETHERRA_STORM_EMB_DIM` env var (default 128).

### Q2: Sinkhorn regularization parameter?
**Decision:** Use `reg=0.1` as default. May tune based on empirical testing. Add `AETHERRA_STORM_SINKHORN_REG` env var.

### Q3: Distance metric for embeddings?
**Decision:** L2 (Euclidean) distance for simplicity. Can switch to cosine distance later if needed.

### Q4: How to handle empty candidate sets?
**Decision:** Return empty result with source="storm", graceful degradation. Log warning if base_fallback is None and STORM is sole strategy.

### Q5: Should we implement GW distance in PR-2?
**Decision:** NO. Defer GW to PR-4+ when we have real neighborhood structures. For now, focus on standard OT with embeddings.

---

## Success Criteria

**PR-2 is complete when:**
1. ✅ POT library integrated and tested
2. ✅ Real OT distances computed (EMD or Sinkhorn)
3. ✅ Budget-aware recall enforced
4. ✅ Evidence tags wired (with placeholders for TDA/sheaf)
5. ✅ Metrics recorded correctly
6. ✅ All existing tests still pass (backward compatibility)
7. ✅ New OT-specific tests pass (10+ new tests)
8. ✅ Integration tests pass with real recall flows
9. ✅ Documentation updated
10. ✅ Feature flag still default-off, kill switch operational

**Performance targets (non-blocking):**
- Exact OT: < 10ms for k ≤ 20 candidates
- Sinkhorn: < 50ms for k ≤ 100 candidates
- Budget enforcement: graceful degradation within 10% of `max_ms_exact`

---

## Next Steps After PR-2

1. **PR-3:** SQLite persistence (store computed embeddings, avoid recomputation)
2. **PR-4:** TDA persistence scoring + sheaf inconsistency
3. **PR-5:** TT/MPS compression layer
4. **PR-6:** KeOps GPU backend support
5. **PR-7:** Maintenance cycles (rank trim, barycenter refresh, pruning)
6. **Phase 0:** Shadow mode testing with real workloads

---

## References

- **POT Documentation:** https://pythonot.github.io/
- **OT Tutorial:** https://pythonot.github.io/auto_examples/plot_OT_1D.html
- **Sinkhorn Algorithm:** https://pythonot.github.io/gen_modules/ot.bregman.html
- **STORM Contracts:** `docs/storm_contracts.md`
- **PR-1 Summary:** `docs/STORM_PR1_SUMMARY.md`
