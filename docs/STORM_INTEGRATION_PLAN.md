# STORM Integration Plan for Aetherra

**Status:** PR-1 Complete ✅ | PR-2 Phase 1 Complete ✅ | PR-2 Phase 2 Complete ✅ | PR-3 Complete ✅ | PR-4 Complete ✅ | PR-5 Complete ✅ | Phase 0 Shadow Mode Complete ✅ | Day 8 Maintenance Complete ✅ | Hub Integration (Day 9) Complete ✅
Owner: Aetherra Memory Working Group
Audience: Memory, Engine, Kernel, Chat, Agents, Security, .aether, Coding teams
License: GPL-3.0 (inherits project license)

**PR-1 Summary:** See `docs/STORM_PR1_SUMMARY.md` for complete details.
**PR-2 Summary:** See `docs/STORM_PR2_SUMMARY.md` for Phase 1 & 2 OT implementation and candidate enrichment details.
**PR-3 Summary:** SQLite-backed persistence for embeddings/cells wired into STORM engine.
**PR-4 Summary:** Sheaf inconsistency and TDA persistence scoring computed from embeddings and exposed via evidence tags.
**PR-5 Summary:** TT/MPS compression shim (SVD-based) optionally approximates cost matrices with strict rank caps.
**Phase 0 Summary:** Shadow mode integration enables STORM to run in parallel with baseline, emitting comparison metrics without affecting production responses.
**Day 8 Maintenance Summary:** Night-cycle maintenance operations for STORM including TT rank trim, barycenter refresh, inconsistency scan, and OT cache pruning.
**Hub Integration Summary:** STORM metrics exported via Hub `/metrics` endpoint (13 series: 6 counters, 6 gauges, 1 labeled). STORM status block included in `/api/memory/status` response via `AetherraMemoryEngineAdvanced.get_system_status()`.

---

## 1) Objectives and success criteria

STORM (Sheaf-Transport Optimized Retrieval Memory) is an additive retrieval/organization module that:

- Treats memory as a sheaf of probability measures across semantic (embeddings), episodic (time), and conceptual (graphs) spaces
- Aligns query-induced measures to cell measures via Optimal Transport (OT), reconciles branches/observers via Gromov–Wasserstein
- Maintains global coherence with sheaf consistency; captures durable themes via TDA; compacts high-order associations via Tensor-Train (TT)

Success = Ship behind a flag with typed outputs, deterministic test profile, metrics/health surfaced via Hub, and no regressions in existing adapters.

KPIs:

- Retrieval quality: top-k hit rate vs. hybrid baseline; RAG answer quality (no-drop target)
- Coherence: reduced inconsistency energy vs. baseline drift
- Latency: 95p recall latency within Kernel SLOs; exact OT applied only to shortlist
- Safety: zero violations in Security gates; clean audit

---

## 2) Contract alignment (no breaking changes)

- Typed recall: `MemoryRecallResult(items, scores, source, metadata)` remains the canonical return. STORM sets `source="storm"|"storm_hybrid"` and adds `storm_meta` fields.
- Evidence mapping: Engine/Chat carry `evidence[]` with tags like `ot:0.123`, `coh:0.94`, `pers:0.22`.
- Evidence normalization tags: map numeric fields into short tokens per Chat contract
  - `transport_cost -> ot:<float>` (lower is better)
  - `sheaf_inconsistency -> coh:<float>` using the pinned formula `coh = 1.0 / (1.0 + sheaf_inconsistency)` in [0,1]
  - `persistence_bonus -> pers:<float>` in [0,1]
- Adapters: Legacy `list[dict]` callers still supported; metadata folded into `dict["meta"]`.
- Security posture: All writes flow through existing policy gates (`redact_before_persist`, privacy classes, signed-only persists). STORM never bypasses gates.

Kill switch and flag defaults:

- Default: `AETHERRA_MEMORY_STORM=0` in all envs.
- Orchestrator kill-switch: if STORM not enabled, `recall()` immediately delegates to `super().recall(...)` with no side effects (shadow/off).

---

## 3) Types and data shapes (tiny contract)

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Literal

@dataclass
class STORMMetadata:
    cell_id: str
    transport_cost: float           # W_p(μ_q, μ_cell)
    sheaf_inconsistency: float      # ||δs||^2 local
    persistence_bonus: float
    freshness: float
    branch_id: Optional[str] = None

@dataclass
class MemoryRecallResult:
    items: List[Any]                # Memory | MemoryFragment | ReplayEpisode
    scores: List[float]
    source: Literal["core","conceptual","episodic","hybrid","qfac","storm"]
    metadata: Dict[str, Any]        # include STORM fields when present
```

Edge cases to handle:

- Empty query → return empty set with metadata defaults
- Cross-branch reconciliation disabled → omit `branch_id`
- Deterministic profile → seeded embeddings/ordering; disable GPU paths
- High OT cost → degrade to hybrid recall path gracefully

Deterministic ordering in test profile:

- Add a stable scoring tie-breaker (e.g., `score_tiebreak = blake2s(id)`) so results order is reproducible when scores are identical.

---

## 4) Module structure (new)

```
Aetherra/aetherra_core/memory/storm/
├── __init__.py
├── engine.py            # STORMEngine: remember/recall, sheaf_status, branch_barycenter
├── cells.py             # cover/cells, restriction maps, sheaf energy
├── ot_backends.py       # POT/KeOps backends; numpy fallback; GW alignment
├── tensor.py            # TT/MPS utils with rank caps; numpy fallback
├── tda.py               # persistence diagrams; optional giotto-tda/persim
├── adapters.py          # AetherraMemoryEngineAdvanced integration
├── metrics.py           # Prometheus series; snapshots for Hub
├── config.py            # flags, policies, deterministic profile
├── persistence.py       # sheaf cover persistence (cells/overlaps) in SQLite + migrations
└── README.md            # developer notes
```

No replacement of canonical engines; this is additive and optional.

Contracts freeze:

- See `docs/storm_contracts.md` for frozen `STORMMetadata` fields, allowed `source` values, and determinism requirements.

---

## 5) Wiring points (existing files)

- `Aetherra/aetherra_core/memory/aetherra_memory_engine.py`: add optional `self.storm` and strategy switch in `recall(..., strategy="storm_hybrid")`.
- `aetherra_hub_server.py`: ensure `/metrics` publishes STORM series (via metrics registry) and `/api/memory/status` merges STORM `sheaf_status()` when enabled.
- Kernel loop (`aetherra_kernel_loop.py`): add night-cycle hook for TT rank trim, barycenter refresh, inconsistency scan, OT cache pruning.
  - Safety rails: (a) TT rank clamp; (b) cap barycenter refresh per cycle; (c) limit OT cache size. Emit `storm_maintenance_total` and a single `storm_maintenance_last{action="..."}` line to `/metrics`.
- Chat evidence mapping (Lyrixa pipeline): propagate `storm_meta` tags into `evidence[]`.
- Docs: add STORM section to `docs/AETHERRA_MEMORY_SYSTEM.md` (link to this plan).

---

## 6) Configuration & flags

Environment variables (with sane defaults):

- `AETHERRA_MEMORY_STORM=0|1` (default 0)
- `AETHERRA_STORM_OT_BACKEND=auto|pot|keops` (default `auto`)
- `AETHERRA_STORM_TT_MAX_RANK=32`
- `AETHERRA_STORM_K_COARSE=64`
- `AETHERRA_STORM_MAX_MS=<int>` — budget-aware recall time budget (ms) for exact OT stage
- `AETHERRA_STORM_MAX_K_EXACT=<int>` — cap on exact-OT refinements; beyond this set `metadata.approximate=true`
- `AETHERRA_PROFILE=test` → deterministic behavior (seeded ordering, numpy fallbacks)

Config file:

- `configs/storm.yaml` mirrors these envs for ops convenience and reproducible deploys.

---

## 7) Observability & dashboards

Prometheus metrics to export:

- `aetherra_storm_ot_cost_avg`
- `aetherra_storm_sheaf_inconsistency`
- `aetherra_storm_tt_rank`
- `aetherra_storm_branch_barycenters_total`
- `aetherra_storm_maintenance_total`
- `aetherra_storm_maintenance_last{action="rank_trim|barycenter_refresh|ot_cache_prune"}`
- `aetherra_storm_recall_latency_ms_p95`
- `aetherra_storm_approximate_recalls_total`

Status JSON (folded into existing endpoints):

- `/api/memory/status` storm block includes:
  - `cells, overlaps, inconsistency_energy, tt_rank`
  - `backends: { pot, keops, numpy }`
  - `tt_rank_cap, selected_backend, exact_ot_active`
  - `last_recall: { approximate: bool }`

- Hub `/metrics`: adds series above

Dashboard notes: reuse QFAC dashboards; add a mini-panel for OT cost and sheaf inconsistency trends.

Alerting (suggested rules):

- Warn if `aetherra_storm_ot_cost_avg` exceeds a threshold over 5m.
- Warn if `aetherra_storm_sheaf_inconsistency` rises steadily over 15m.
- Warn if `aetherra_storm_approximate_recalls_total` rate spikes (budget issues).

---

## 8) Algorithms and fallback strategy

Recall path (storm_hybrid):

1) Encode query `(e_q, t_q, G_q)` and form `μ_q`.

2) Coarse shortlist by multi-kernel similarity + OT lower bounds (fast path, numpy).

3) Exact OT on top-K (entropic Sinkhorn, POT/KeOps if available; numpy fallback).
     - Respect `max_ms` and `max_K_exact`; if exceeded, skip exact OT, set
         `metadata.approximate=true`, and record `status.last_recall.approximate=true`.

4) Compute sheaf inconsistency and TDA persistence bonus.

5) Score with blended `S(x|q)`; return `MemoryRecallResult` with `STORMMetadata`.

Ingest path:

- Place into nearest cell; update `μ_cell` (OT barycenter), TT cores (rank-capped TT-SVD),
  TDA summaries, restriction maps; respect policy gates.

Sheaf cover persistence & versioning:

- Persist `cells`, `overlaps`, restriction map parameters, and per-cell statistics to disk
    using SQLite with an explicit `storm_schema_version`.
- Provide a lightweight migration routine that up-converts prior versions and preserves indices.

SQLite schema (v1):

- See `configs/sql/storm_schema_v1.sql` for `cells`, `overlaps`, `storm_meta`, and a `schema_version` registry. Include a no-op `v1→v2` migration stub.

Fallbacks:

- Missing POT/KeOps → numpy-only approximate OT; still deterministic under `test` profile.
- TDA libs unavailable → disable persistence bonus; keep contract stable.
- Tensor libs unavailable → use small-rank numpy cores; cap rank strictly.

---

## 9) Testing & quality gates

New tests (pytest):

- `tests/storm/test_storm_basic.py`: store/recall happy path, metadata presence
- `tests/storm/test_storm_determinism.py`: deterministic profile ordering and costs
- `tests/storm/test_storm_backends.py`: backend selection and numpy fallback
- `tests/storm/test_storm_metrics.py`: metrics exported; /metrics snapshot stable
- `tests/storm/test_storm_branch_reconciliation.py`: GW alignment produces barycenter & residual drift

Additional fast tests:

- `tests/storm/test_storm_budget.py` — verifies approximate path + `metadata.approximate=true` when time/compute budget exceeded.
- `tests/storm/test_storm_status_backends.py` — `/api/memory/status` exposes `storm.backends` block.
- `tests/storm/test_storm_chat_evidence.py` — evidence tags (`ot:`, `coh:`, `pers:`) appear on Chat final payload.
- `tests/storm/test_storm_branch_spike.py` — simulates branch drift; asserts fallback to per-branch recall + `residual_drift` metric + `metadata.branch_fallback=true`.
- `tests/storm/test_storm_security_logs.py` — ensures OT debug logs never contain raw content (IDs/aggregates only).
- `tests/storm/test_storm_coherence_tag.py` — asserts `coh:` normalization matches the chosen formula across edge cases.
- `tests/storm/test_storm_status_selected_backend.py` — status exposes `selected_backend` and `exact_ot_active`.
- `tests/storm/test_storm_metrics_approx_counter.py` — `aetherra_storm_approximate_recalls_total` increments when approximate path used.

Coding system gates:

- Add targeted capability tests to existing tasks (see workspace tasks). Ensure no coverage drop.

KPIs validation scripts:

- Compare hybrid vs storm_hybrid recall quality on a golden set; record OT cost and inconsistency deltas.
- A/B gate: enforce no-drop in hit-rate; report ablation toggles for TDA and sheaf terms to prove additive value (pipe results to `/metrics`).

---

## 10) Security & privacy

- All writes via `redact_before_persist`, privacy classes (`public|internal|sensitive`), signed-only persistence for sensitive flows.
- Only aggregate metrics exported; no raw content leaves process.
- Deterministic profile used for CI/PR verification; reproducible results logged.
- Security log redaction check: add guard so that OT debug logs redact content fields; test verifies only IDs/aggregates appear.

Endpoint policies:

- Any additions to `/api/memory/status` remain under existing token/allowlist policies, mirroring current Hub protection.

---

## 10a) Hub Integration (Day 9) ✅

**Metrics Export** (`/metrics` endpoint):

Prometheus-format metrics available via Hub `/metrics` when STORM enabled:

Counters (6):

- `aetherra_storm_approximate_recalls_total` — Total approximate recall calls
- `aetherra_storm_maintenance_total` — Total maintenance operations
- `aetherra_storm_branch_barycenters_total` — Total barycenter computations
- `aetherra_storm_shadow_comparisons_total` — Shadow mode comparisons
- `aetherra_storm_shadow_divergences_total` — Shadow divergence count
- `aetherra_storm_shadow_errors_total` — Shadow mode errors

Gauges (6):

- `aetherra_storm_ot_cost_avg` — Average OT cost
- `aetherra_storm_sheaf_inconsistency` — Sheaf inconsistency energy
- `aetherra_storm_tt_rank` — Current TT rank
- `aetherra_storm_recall_latency_ms_p95` — 95th percentile recall latency
- `aetherra_storm_shadow_agreement_rate` — Shadow agreement rate
- `aetherra_storm_shadow_latency_ms_avg` — Shadow latency average

Labeled Gauge (1):

- `aetherra_storm_maintenance_last{action="..."}` — Last maintenance timestamp per action (rebalance_clusters, update_barycenters, scan_inconsistencies, prune_ot_cache)

**Status API** (`/api/memory/status`):

Memory status endpoint includes STORM block via `AetherraMemoryEngineAdvanced.get_system_status()`:

```json
{
  "storm": {
    "enabled": true,
    "shadow_mode": false,
    "backends": {"pot": true, "keops": false},
    "selected_backend": "pot",
    "exact_ot_active": true,
    "tt_rank_cap": 32,
    "k_coarse": 50,
    "last_recall": {"approximate": false}
  }
}
```

**Implementation Details:**

- `aetherra_hub/services/registry_client.py`: Added `get_storm_metrics()` function following async pattern
- `aetherra_hub/services/metrics_accum.py`: Added STORM metrics export section (lines ~604-638)
- `Aetherra/aetherra_core/memory/aetherra_memory_engine.py`: Added `get_status()` alias for Hub compatibility
- `Aetherra/aetherra_core/memory/memory_core.py`: Added `AetherraMemorySystem` alias, wired `LyrixaMemorySystem.engine` to use `AetherraMemoryEngineAdvanced`

---

## 10b) .aether Script Helpers (Day 9a) ✅

**Built-in Functions for STORM:**

Added three STORM functions to `.aether` script environment, enabling automation and monitoring:

1. **`storm.recall(query, limit=10)`**
   - Invokes STORM-powered memory recall from scripts
   - Returns structured result with items, scores, source
   - Gracefully falls back to baseline recall if STORM disabled
   - Example: `result = CALL storm.recall("user preferences", 5)`

2. **`storm.sheaf_status()`**
   - Queries current sheaf consistency metrics
   - Returns inconsistency value, coherence score, TT rank
   - Useful for monitoring and dashboards
   - Example: `status = CALL storm.sheaf_status()`

3. **`storm.coherence_guard(min_coherence=0.9)`**
   - Alert mechanism for sheaf coherence degradation
   - Returns alert flag if coherence drops below threshold
   - Enables automated health checks and notifications
   - Example: `guard = CALL storm.coherence_guard(0.85)`

**Implementation:**

- File: `aether.py` lines 354-487
- Three async methods: `_builtin_storm_recall`, `_builtin_storm_sheaf_status`, `_builtin_storm_coherence_guard`
- Registered in `built_in_functions` dict under nested "storm" key (lines 91-111)
- Demo script: `workflows/storm_demo.aether`

**Benefits:**

- Enables `.aether` scripts to query STORM memory programmatically
- Supports automated coherence monitoring and alerting
- Provides script-level access to STORM observability metrics
- Completes STORM observability stack: metrics + status API + script automation

---

## 11) Timeline (10 days)

Day 1–2 — Skeleton `STORMEngine` + adapters; env flags; deterministic stubs; metrics scaffolding.
Day 3–4 — Sheaf cells/overlaps; coarse candidate search; metadata in `MemoryRecallResult`.
Day 5–6 — Entropic OT on shortlist; basic TT compression; Hub `/metrics` export.
Day 7 — TDA summaries + persistence bonus; Engine RAG evidence; Chat tags.
Day 8 — Branch barycenter API; Kernel night-cycle hook ✅.
Day 9 — .aether helpers (`storm.recall`, `storm.sheaf_status`); Security gates verified.
Day 10 — A/B gate + acceptance tests via Coding System; docs badge + README blurb.

Budget-aware recall and backends probe are targeted for Day 3–4.
Sheaf persistence/migrations can land Day 4–5.
Branch guardrails ship alongside Day 8 barycenter work.

---

## 12) Open decisions (quick calls)

- Default OT backend: `auto` selects POT if installed; else numpy fallback.
- Include `configs/storm.yaml` in repo now or later (env-only to start)?
- TDA dependency policy: optional extra; document install in dev profile.
- Dashboard: extend QFAC UI vs. separate micro-panel; start with metrics only.
- Sheaf storage: choose SQLite tables (decided) for migrations and ops tooling.
- Evidence normalization constants: finalize mapping for `coh:` normalization (e.g., `coh = 1.0 / (1.0 + inconsistency)` or min–max window).

---

## 13) Next steps (PR-1 scope)

- Add module directory (no heavy deps yet) and stub `engine.py`.

  - `recall(..., strategy)` returns contract-shaped results with deterministic placeholders.
- Add env flag handling in `aetherra_memory_engine.py` (guarded, off by default).
- Export stub metrics from `metrics.py` and include them in Hub `/metrics`.
- Add tests: basic + determinism + metrics.
- Update `docs/AETHERRA_MEMORY_SYSTEM.md`: link STORM and this plan.

PR-1.1 small additions (from tweaks):

- Budget-aware recall kwargs (`max_ms`, `max_K_exact`) plumbed through `recall()`; tag `metadata.approximate`.
- `/api/memory/status` includes `storm.backends` and `tt_rank_cap`.
- `/api/memory/status` exposes `selected_backend` and `exact_ot_active`, and includes `last_recall.approximate`.
- Night-cycle emits `storm_maintenance_total` and `storm_maintenance_last{action=...}`.
- Evidence tags normalized to `ot:`, `coh:`, `pers:` tokens.

Future helpers:

- `.aether`: add `storm.coherence_guard(min_coh=...)` to narrate/flag when sheaf inconsistency exceeds threshold.

---

## PR-1 checklist (complete ✅)

- Feature flag `AETHERRA_MEMORY_STORM` off by default; recall returns typed, contract-shaped data.
- `/api/memory/status` shows `storm.backends`, `tt_rank_cap`, `selected_backend`, `exact_ot_active`.
- Metrics exported: OT cost avg, sheaf inconsistency, TT rank, branch barycenters, maintenance; plus `aetherra_storm_recall_latency_ms_p95` and `aetherra_storm_approximate_recalls_total`.
- Budget-aware recall respected; sets `metadata.approximate=true` and status snapshot includes `last_recall.approximate`.
- Evidence tags present (`ot:`, `coh:`, `pers:`) with `coh = 1/(1+sheaf_inconsistency)`.
- Night-cycle emits `storm_maintenance_total` and `storm_maintenance_last{action=...}`.
- Deterministic profile: seeds locked, numpy fallbacks, tie-breakers in scoring; tests pass.

Deliverable: Feature-flagged skeleton passing tests and not changing default behavior. ✅

---

## PR-2 Phase 1 checklist (complete ✅)

- Deterministic mock embeddings with SHA-256 seeding (`_generate_mock_embedding`)
- Distance matrix helper (`_build_distance_matrix`) for pairwise Euclidean costs
- Real OT computation using POT library (EMD preferred, Sinkhorn fallback)
- Budget enforcement: marks recall as approximate if time exceeds `max_ms_exact`
- Evidence tags wired: `ot` uses stable min-distance proxy (identical text → 0.0)
- Empty candidate handling: graceful degradation when no items to compare
- Test suite: 10 new tests in `test_storm_ot.py` covering determinism, evidence, budget, hybrid mode
- Integration tests verified: 44 tests passing in `tests/storm/`
- Env var alignment: supports both documented and legacy names for backward compatibility
- Documentation: PR-2 summary created, memory system doc updated

Deliverable: Real OT path integrated, tested, and ready for candidate enrichment. ✅

---

## PR-2 Phase 2 checklist (complete ✅)

- Real memory candidate fetching via `_fetch_candidates()` from `LyrixaMemorySystem.recall_memories()`
- Coarse-to-fine candidate selection using `k_coarse` parameter (default 64)
- Graceful fallback to base_fallback when core memory unavailable
- Empty candidate handling preserves PR-1 skeleton behavior (pure mode returns empty)
- Probability mass weighting strategies implemented (`_compute_mass_distribution`):
  - `nearest`: All mass on nearest neighbor (Phase 1 behavior)
  - `uniform`: Equal mass across all candidates
  - `importance`: Weighted by relevance scores (Phase 2 default)
  - `recency`: Placeholder with importance fallback (for future timestamps)
- Zero score handling with epsilon addition for numerical stability
- Integration with `AetherraMemoryEngineAdvanced`: core memory reference wired to STORM engine
- Test suite: 15 new tests in `test_storm_candidates.py` covering:
  - Candidate fetching from core memory with k_coarse
  - Fallback strategies (base_fallback, pure mode, core memory failure)
  - All four weighting strategies with validation
  - Full recall pipeline integration with real memory
- All 59 STORM tests passing (44 Phase 1 + 15 Phase 2)
- Documentation: PR-2 summary updated with Phase 2 details, integration plan updated

Deliverable: Enriched candidate selection with real memory integration, multiple weighting strategies, and comprehensive test coverage. ✅

---

## PR-3 SQLite Persistence (complete ✅)

- Storage module `storm/persistence.py` implemented with `StormStorage`
  - Tables: `storm_cells(content_hash PK, dim, dtype, embedding BLOB, content_excerpt, created_at)`
  - Tables: `storm_overlaps(a_hash, b_hash, weight, created_at)` (reserved for later phases)
  - Meta: `storm_meta(key, value)` with `schema_version=1`
- Engine integration
  - Optional storage initialized from `StormConfig.sqlite_path`
  - On recall: attempts to read persisted embeddings for candidates; if missing, computes deterministic embedding and persists best‑effort
  - Query embeddings are not persisted in PR‑3
  - All storage operations are best‑effort and never fail recall paths
- Tests
  - `tests/storm/test_storm_persistence.py` validates schema, upsert/get, and engine population
  - Full STORM suite passes (63 tests)

Deliverable: SQLite-backed persistence for embeddings/cells wired into STORM engine with comprehensive tests. ✅

---

## PR-4 Sheaf + TDA Scoring (complete ✅)

- Helpers implemented in `storm/tda_sheaf_helpers.py`
  - `compute_sheaf_inconsistency(embeddings)`: 1 − mean cosine similarity across pairs
  - `compute_persistence_bonus(embeddings)`: MST-based cluster tightness mapped to [0,1]
- Engine integration
  - `StormEngine.recall()` computes `sheaf_inconsistency` and `persistence_bonus` when candidates exist
  - Evidence tags map: `coh = 1/(1+sheaf_inconsistency)`, `pers = persistence_bonus`
  - Metrics: `record_sheaf_inconsistency` updated with latest value
- Tests
  - `tests/storm/test_storm_tda_sheaf.py` validates identical vs diverse sets, monotonicity, and evidence mapping
  - Full STORM suite passes (67 tests)

Deliverable: Sheaf inconsistency and TDA persistence scoring wired into STORM with deterministic helpers and tests. ✅

---

## PR-5 TT/MPS Compression (complete ✅)

- Compression shim implemented in `storm/tt_compression.py`
  - SVD-based low-rank approximation with deterministic behavior and strict rank cap
  - Public API: `approximate_cost_matrix(cost, rank_cap) -> (approx, meta)`
  - Metadata includes `applied`, `rank_used`, `shape`, and optional Frobenius error
- Engine integration
  - `StormEngine.recall()` optionally approximates the OT cost matrix before computing OT when `tt_max_rank > 0`
  - Uses approximated matrix for OT compute, but preserves evidence stability by deriving the `ot` tag from the original matrix's min-distance proxy
  - Adds `storm_meta.tt_applied` and `storm_meta.tt_rank_used`; updates TT rank metric
- Tests
  - `tests/storm/test_storm_tt_compression.py` validates approximation shape/rank, no-op when rank=0, and engine metadata behavior (applied/skip)

Deliverable: Optional rank-capped compression in the recall path with stable evidence semantics and comprehensive tests. ✅

---

## Phase 0 Shadow Mode (complete ✅)

- Configuration
  - New env variable: `AETHERRA_STORM_SHADOW_MODE=0|1` (default 0)
  - New config field: `StormConfig.shadow_mode: bool`
- Dual-path recall logic
  - When shadow_mode=True, STORM runs in parallel with baseline recall
  - Baseline result always returned to production (zero impact)
  - STORM result compared with baseline for validation
- Comparison metrics
  - `aetherra_storm_shadow_comparisons_total`: Total shadow comparisons
  - `aetherra_storm_shadow_divergences_total`: Times STORM disagreed with baseline
  - `aetherra_storm_shadow_errors_total`: Times STORM failed but baseline succeeded
  - `aetherra_storm_shadow_agreement_rate`: Exponential moving avg of agreement (0-1)
  - `aetherra_storm_shadow_latency_ms_avg`: Average STORM latency in shadow mode
- Shadow logger utilities
  - `shadow_recall()`: Execute STORM and compare with baseline
  - `compare_results()`: Compute Jaccard overlap, score deltas, agreement
  - Graceful error handling: STORM failures never affect production
- Integration
  - `AetherraMemoryEngineAdvanced.recall_typed()` detects shadow mode
  - Runs both baseline and STORM in parallel
  - Records comparison metrics via `StormMetrics`
  - Always returns baseline unchanged
- Tests
  - `tests/storm/test_storm_shadow_mode.py`: 11 tests covering shadow behavior
  - Validates zero production impact
  - Tests comparison algorithms (identical, divergent, partial overlap)
  - Tests shadow vs production mode switching
  - Tests graceful STORM failure handling
  - All 82 STORM tests passing (71 prior + 11 shadow)

Deliverable: Shadow mode integration enabling safe parallel validation of STORM without production impact. ✅

---

## Day 8 Maintenance & Night-Cycle Integration (complete ✅)

- Maintenance operations implemented in `storm/engine.py`
  - `run_maintenance()`: Async method executing 4 maintenance tasks
  - **TT rank trim**: Placeholder for future TT approximation cache cleanup
  - **Barycenter refresh**: Placeholder for future branch barycenter recomputation
  - **Inconsistency scan**: Scans stored embeddings for rising sheaf inconsistency
  - **OT cache pruning**: Placeholder for future OT transport plan cache cleanup
  - Each task updates metrics via `record_maintenance(action, timestamp)`
  - Returns dict with status and task-specific results
- Persistence enhancement
  - Added `get_all_embeddings()` to `StormStorage` for maintenance scans
  - Fetches all stored embeddings for inconsistency analysis
- Kernel integration
  - Wired `run_maintenance()` into `aetherra_kernel_loop.py::_perform_night_cycle()`
  - Detects STORM engine via `memory_system._storm_engine`
  - Graceful execution: failures logged but never block night cycle
  - Logs average inconsistency from scan results
- Metrics tracking
  - `aetherra_storm_maintenance_total`: Total maintenance operations
  - `aetherra_storm_maintenance_last{action=...}`: Timestamp of last run per action
  - `aetherra_storm_branch_barycenters_total`: Counter for barycenter refresh events
  - All maintenance metrics exported via `metrics.snapshot()`
- Tests
  - `tests/storm/test_storm_maintenance.py`: 10 comprehensive tests
  - Validates all 4 maintenance tasks execute successfully
  - Tests metrics tracking (counters, timestamps, gauges)
  - Tests inconsistency scan with/without stored embeddings
  - Tests graceful error handling (storage failures don't crash maintenance)
  - Tests idempotent behavior (multiple runs safe)
  - Tests metrics snapshot includes maintenance counts
  - All 92 STORM tests passing (82 prior + 10 maintenance)

Deliverable: Night-cycle maintenance operations for STORM with comprehensive tests and kernel integration. ✅

---

## Rollout plan

- Phase 0 — Shadow mode ✅: compute STORM in parallel, emit status/metrics only. No answers depend on it.
- Phase 1 — Controlled traffic: enable `storm_hybrid` for ≤10% via config; A/B gate on top‑k hit‑rate and answer quality.
- Phase 2 — Ramp: widen to ~50% after 24–48h of healthy metrics; keep one‑env canary; maintain one‑commit rollback (import guard) and env flag rollback.
