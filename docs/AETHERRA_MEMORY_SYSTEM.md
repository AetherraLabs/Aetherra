
# Aetherra Memory System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Aetherra's Memory System combines reliable, local-first storage with advanced conceptual and episodic structures, adaptive compression (QFAC), optional quantum‑hybrid experimentation, and **STORM** (Sheaf-Transport Optimized Retrieval Memory) for topologically-consistent semantic retrieval. It preserves strict backward compatibility for existing Lyrixa plugins while enabling richer recall, narratives, reflection, and system health monitoring.

## Architecture overview

Layers (low → high):

- Compatibility layer
  - `LyrixaMemoryEngine` is a compatibility alias to `AetherraMemoryEngine` so existing plugins work unchanged.
  - `AetherraMemoryEngine` adapts to the canonical `QuantumEnhancedMemoryEngine` and maintains a tiny in‑memory list for legacy substring retrieval in tests.
- Core memory (local, SQLite)
  - `LyrixaMemorySystem` stores conversation, project, preferences, and learning memories with indexes for efficient lookup. Note: the `memory_core.py` module header is marked “DEPRECATED” because top-level engine calls are adapted to QEME; however, the SQLite-backed `LyrixaMemorySystem` class remains fully supported and is used by the advanced orchestrator and tests.
- Orchestrated advanced memory
  - `AetherraMemoryEngineAdvanced` coordinates: core memory, fractal/concept/episodic structures, narrative generation, pulse/health monitoring, reflective analysis, and **STORM** (Sheaf-Transport Optimized Retrieval Memory, feature-flagged).
- Compression and quantum‑hybrid
  - `QFACMemorySystem` and `QFACMemoryNode` provide adaptive compression and retrieval; can bridge to `QuantumMemoryBridge` when hybrid/quantum modes are enabled.

Key properties

- Local-first persistence with graceful degradation (features run even if optional components are unavailable).
- Backward compatibility for existing plugins and tests.
- Async-first API in advanced/core systems; small sync helpers for compatibility.

Implementation notes (current state)

- Strong hashing and determinism:
  - Memory IDs are generated with BLAKE2s-128 (32-hex chars) in `LyrixaMemorySystem` to keep IDs compact while avoiding weak hashes.
  - QFAC metrics caches (entropy/pattern) use SHA-256 keys.
  - Concept embeddings use a deterministic SHA-256–seeded PRNG for reproducibility.
  - Legacy MD5/SHA1 usages have been removed from memory-related paths.

Design goals

- Unified and typed contracts at the API boundaries while retaining adapters for legacy list-of-dicts results.
- Deterministic-by-default observability and health metrics for dashboards and gates.
- Policy-aware operations that integrate with Aetherra’s security posture without leaking sensitive data.

## Core components

### 1) Compatibility engines

- `LyrixaMemoryEngine` → alias of `AetherraMemoryEngine` for plugin compatibility.
- `AetherraMemoryEngine`
  - Forwards store/retrieve to `QuantumEnhancedMemoryEngine`.
  - Maintains a small in‑memory list for legacy substring recall (tests/plugins expect list[{'content': ...}]).
- `QuantumEnhancedMemoryEngine`
  - Minimal canonical engine with `store()` and `retrieve()` plus status; used as the adapter target.

### 2) LyrixaMemorySystem (SQLite-backed)

File: `Aetherra/aetherra_core/memory/memory_core.py`

- Table: `memories`
  - Columns: id TEXT PK, content TEXT, context TEXT, tags TEXT, importance REAL, created_at TEXT, last_accessed TEXT, access_count INTEGER, memory_type TEXT
  - Indexes: by type, importance, created_at, tags
- Memory types: conversation, project, preference, learning
- Selected APIs (async):
  - `store_memory(content, context=None, tags=None, importance=0.5, memory_type='conversation') -> str`
  - `recall_memories(query_text, limit=5, memory_type=None) -> list[Memory]`
  - `get_conversation_context(session_id, limit=10)`
  - `store_user_preference(key, value, user_context=None)` / `get_user_preferences()`
  - `store_project_context(project_name, context)` / `get_project_context(project_name)`
  - `store_learning(learning_content, learning_context=None)`
  - `search_memories(MemoryQuery)`
  - `consolidate_memories()` (cleanup/importance updates)
  - `get_memory_stats()`
  - Export/Import helpers and connection lifecycle helpers

ID generation and hashing

- `LyrixaMemorySystem._generate_memory_id(...)` computes a compact strong ID using `hashlib.blake2s(..., digest_size=16).hexdigest()`.
- Text-analysis caches used by compression metrics (see QFAC section) use `hashlib.sha256`.

### 3) Advanced orchestrator

File: `Aetherra/aetherra_core/memory/aetherra_memory_engine.py`

- `AetherraMemoryEngineAdvanced` orchestrates:
  - Core: `LyrixaMemorySystem`
  - Fractal/semantic structures: `FractalMeshCore` (fragments), `ConceptClusterManager` (concept clusters), `EpisodicTimeline` (episodic chains)
  - Observability: `MemoryNarrator` (daily/weekly/thematic narratives), `MemoryPulseMonitor` (health + drift alerts), `MemoryReflector` (insights, contradictions, blind spots)
- Primary flows (async):
  - `remember(content, tags=None, category='general', fragment_type=..., confidence=1.0, narrative_role=None) -> MemoryOperationResult`
  - `recall(query, strategy='hybrid' | 'vector' | 'conceptual' | 'episodic', ...) -> MemoryRecallResult`
  - `generate_narrative(type='daily'|'weekly'|'thematic', time_range=None, theme=None)`
  - `run_reflection(type='past_week'|'contradictions'|'concept_exploration'|'blind_spots', ...)`
  - `check_memory_health()` / `get_memory_health()` (sync summary variant)
  - `get_memory_pulse()` / `get_memory_insights()`
  - `maintenance_cycle()` (health check, reflections, narratives, cleanup)
- Config: `MemorySystemConfig` (db paths, retention, auto narrative/pulse, reflection cadence, cross-system validation)

Note: Some helpers (e.g., `FractalMeshCore`, `EpisodicTimeline`, `MemoryNarrator`, `MemoryPulseMonitor`, `MemoryReflector`) are modular. If a module is missing, the system degrades gracefully.

### 4) Concept/Fractal subsystems

- `ConceptClusteringEngine` (`concept_clustering.py`)
  - Adds concepts with deterministic mock embeddings; groups into clusters; stores to SQLite (`concepts`, `clusters`, and `concept_relationships`).
  - APIs: `add_concept`, `_update_clusters`, `get_related_concepts`, `get_cluster_summary`.
- `FractalHierarchies` (`fractal_hierarchies.py`)
  - Builds multi-level fractal cluster hierarchies; stores `fractal_clusters`, `hierarchy_metrics`, `cross_level_bridges`.
  - APIs: `build_fractal_hierarchy`, `find_cluster_by_pattern`, `get_hierarchy_path`, stats/metrics.
- `FractalReplayEngine` (`fractal_replay_engine.py`)
  - Reconstructs episodic sequences from fractal nodes/patterns; stores `replay_episodes` and a reconstruction cache.
  - APIs: `reconstruct_episode`, `load_replay_episode`, `get_replay_statistics`.

### 5) QFAC compression and quantum bridge

- `QFACMemorySystem` / `QFACMemoryNode` (`qfac_integration.py`)
  - Adaptive compression using `MemoryCompressionAnalyzer`; stores node state in memory; supports bulk compression and optimization.
  - Modes (env `AETHERRA_QFAC_MODE`): `classical` (default), `hybrid`, `quantum`.
  - In `hybrid`/`quantum`, uses `QuantumMemoryBridge` when available, with graceful fallback to classical shadow.
  - System APIs: `store_memory`, `retrieve_memory`, `compress_all_eligible`, `optimize_system`, `get_system_status`, `export_system_report`, `start_dashboard`, `stop_dashboard`.
\
Deterministic behavior and hashing

- QFAC’s `CompressionMetrics` (`compression_metrics.py`) uses SHA‑256 for cache keys to ensure deterministic and collision‑resistant memoization for entropy and recursive pattern density.
- Concept clustering (`concept_clustering.py`) seeds its deterministic mock embeddings with a SHA‑256 hash of the input text, keeping clustering reproducible without external models.
- `QuantumMemoryBridge` (`quantum_memory_bridge.py`)
  - Experimental phase: integrates with Qiskit/Cirq if installed; otherwise simulates.
  - Core APIs: `encode_memory_to_quantum`, `quantum_memory_retrieval`, `quantum_interference_experiment`, `quantum_error_correction_test`, `get_quantum_statistics`.
  - Data classes: `QuantumMemoryState`, `QuantumCircuitTemplate`, `QuantumExperimentResult`.

### 6) STORM (Sheaf-Transport Optimized Retrieval Memory)

File: `Aetherra/aetherra_core/memory/storm/`

**Status:** PR-1 complete ✅ (skeleton). PR-2 Phase 1 complete ✅ (core OT via POT: EMD/Sinkhorn). PR-2 Phase 2 complete ✅ (candidate enrichment & weighting). PR-3 complete ✅ (SQLite persistence). PR-4 complete ✅ (sheaf inconsistency + TDA persistence). PR-5 complete ✅ (TT/MPS compression shim). **Phase 1 Shadow Mode deployed ✅ (Production Ready)**.

Feature-flagged, default OFF. See `docs/STORM_INTEGRATION_SUMMARY.md`, `docs/STORM_PR1_SUMMARY.md`, `docs/STORM_PR2_SUMMARY.md`, and `docs/STORM_INTEGRATION_PLAN.md` for details.

**STORM** is an advanced retrieval subsystem using:

- **Sheaf theory** for topological consistency checking across memory overlaps
- **Optimal Transport (OT/GW)** for computing semantic transport costs between query and memory cells
- **Topological Data Analysis (TDA)** for persistence-based importance scoring
- **Tensor-Train (TT) / MPS** for rank-bounded memory compression
- **Shadow Mode** (Phase 0) for safe parallel validation without production impact

**Current state (Day 8 Maintenance complete):**

- Deterministic mock embeddings and distance matrix helpers
- Real OT computation using POT (EMD preferred, Sinkhorn fallback); budget-aware
- Real memory candidate fetching from `LyrixaMemorySystem.recall_memories()`
- Coarse-to-fine candidate selection using `k_coarse` parameter
- Multiple probability mass weighting strategies (nearest, uniform, importance, recency)
- Importance-weighted distribution as default (Phase 2)
- Evidence tags wired; `ot` uses a stable min-distance proxy (identical → 0.0)
- Sheaf inconsistency computed from embeddings (1 − mean cosine similarity across pairs)
- Persistence bonus computed via MST-based cluster tightness mapped to [0,1]
- TT/MPS-style compression shim (SVD-based) optionally approximates OT cost matrix with strict rank cap (`tt_max_rank`)
- **Shadow mode integration**: STORM runs in parallel with baseline, emits comparison metrics, never affects production responses
- **OS integration**: Advanced engine loaded at boot via `aetherra_os_launcher.py`; post-boot status logging
- **Production deployment**: All tests passing (smoke, capabilities, SSE v2, quality gates); monitoring infrastructure in place
- **Night-cycle maintenance**: Periodic tasks for TT rank trim, barycenter refresh, inconsistency scan, OT cache pruning
- Integrated with `AetherraMemoryEngineAdvanced.recall_typed()` when enabled
- Integrated with `aetherra_kernel_loop.py::_perform_night_cycle()` for maintenance
- Feature flags: `AETHERRA_MEMORY_STORM` (default=0), `AETHERRA_STORM_SHADOW_MODE` (default=1 when STORM enabled)
- Kill switch operational: graceful degradation if initialization fails
- SQLite persistence wired for embeddings/cells via `StormStorage` (`storm_cells`, `storm_overlaps`, `storm_meta`) with `schema_version=1`
- Backends: POT (CPU, installed), KeOps (GPU, optional, not yet wired)
- **Monitoring**: Daily/weekly monitoring scripts; metrics at `/metrics` endpoint; reports in `reports/daily` and `reports/weekly`

**Recall sources:**

- `storm`: Pure STORM retrieval (no base fallback)
- `storm_hybrid`: STORM + base memory engine fallback merge

**Configuration:** `StormConfig` (from environment):

- `enabled`: Feature toggle (default: False)
- `shadow_mode`: Shadow mode toggle (Phase 0; default: False)
- `ot_backend`: Backend selector (`auto` → POT, or `pot`/`keops`)
- `tt_max_rank`: TT decomposition rank cap (default: 32)
- `k_coarse`: Coarse-grained candidates for OT (default: 64)
- `max_ms_exact`: Millisecond budget for exact OT (default: 100ms)
- `max_k_exact`: Max candidates for exact OT (default: 20)
- `sqlite_path`: Persistence database path (default: auto-detect from core memory config)

**Metrics (Prometheus-style):**

- Counters: `aetherra_storm_approximate_recalls_total`, `aetherra_storm_maintenance_total`, `aetherra_storm_branch_barycenters_total`, `aetherra_storm_shadow_comparisons_total`, `aetherra_storm_shadow_divergences_total`, `aetherra_storm_shadow_errors_total`
- Gauges: `aetherra_storm_ot_cost_avg`, `aetherra_storm_sheaf_inconsistency`, `aetherra_storm_tt_rank`, `aetherra_storm_recall_latency_ms_p95`
- Labeled gauge: `aetherra_storm_maintenance_last{action=...}` (timestamps by action type)

**Status block (in `AetherraMemoryEngineAdvanced.get_system_status()`):**

- `enabled`: bool
- `backends`: dict of available backends (`pot`, `keops`)
- `selected_backend`: str (e.g., "POT")
- `exact_ot_active`: bool (whether exact OT is used)
- `tt_rank_cap`: int (current TT rank limit)
- `k_coarse`: int (candidate count for approximate OT)
- `last_recall`: Optional[str] (ISO timestamp of last recall)

**Evidence tags (in `MemoryRecallResult.metadata.storm`):**

- `ot:transport_cost`: Float, optimal transport cost (lower = closer match)
- `coh:sheaf_coherence`: Float, `1.0 / (1.0 + sheaf_inconsistency)` (higher = more consistent)
- `pers:persistence_bonus`: Float, TDA persistence score (higher = more important)

**Contract compliance:**

- Extends `RecallSource` Literal to include `"storm"` and `"storm_hybrid"` (see `models.py`)
- Returns `MemoryRecallResult` with typed `items`, `scores`, `metadata` including `STORMMetadata` fields
- Maintains backward compatibility: existing recall strategies unaffected

**Integration with AetherraMemoryEngineAdvanced:**

- On initialization: tries to instantiate `StormEngine`; stores in `self._storm_engine` (Optional)
- `recall_typed()`: if STORM enabled, delegates to `_storm_engine.recall()` with `base_fallback` for hybrid mode
- `get_system_status()`: includes `storm` status block (or fallback if disabled)

**Next steps (future PRs):**

- PR-2 (Phase 2): Enrich candidate distributions; consider exposing plan-derived costs safely
- PR-3: SQLite persistence for cells, overlaps, metadata
- PR-4: TT/MPS compression layer and TDA/sheaf consistency scoring
- PR-5: Maintenance cycles (rank trim, barycenter refresh, pruning)
- Phase 0: Shadow mode testing with metrics validation before production enable

**References:**

- Contracts: `docs/storm_contracts.md` (frozen)
- Integration Plan: `docs/STORM_INTEGRATION_PLAN.md`
- PR-1 Summary: `docs/STORM_PR1_SUMMARY.md`
- PR-2 Summary: `docs/STORM_PR2_SUMMARY.md`
- Test suite: `tests/storm/` (34 tests, all passing)

## Data models (representative)

- Core memory `Memory`: id, content, context, tags, importance, created_at, last_accessed, access_count, memory_type.
- Fractal `MemoryFragment` (advanced orchestrator) includes: fragment_id, content, fragment_type, temporal tags, symbolic_tags, associative_links, confidence_score, access_pattern.
- Concept `Concept` / `ConceptCluster` with embeddings, frequency, centroid, coherence.
- Episodic `ReplayEpisode`: episode_id, nodes, fidelity, compression ratio, temporal sequence, coverage, metadata.
- Quantum `QuantumMemoryState`: state_id, memory_id, qubit_count, circuit_depth, classical_shadow, encoding_fidelity, measurement_results.

### API consistency: typed returns and adapters

- Canonical recall contract
  - `MemoryRecallResult`:
    - `items`: list of typed records (one of: `Memory`, `MemoryFragment`, `ReplayEpisode`), each with a `kind` discriminator.
    - `source`: `core` | `conceptual` | `episodic` | `hybrid` | `qfac` | `storm` | `storm_hybrid`.
    - `scores`: list of floats aligned with `items` (similarity/confidence per item).
    - `metadata`: timing, strategy, pagination, optional `storm` block (see STORM section above).
- Legacy compatibility
  - `AetherraMemoryEngine.retrieve()` continues to return `list[dict]` in legacy mode.
  - Adapters are provided to map `MemoryRecallResult` → `list[dict]` and vice‑versa (used by `AetherraMemoryEngine` and tests).
  - Engines should avoid “half‑structured” responses: choose the canonical typed result internally, adapt only at the very edge for legacy callers.

Adapter/deprecation clarity

- `AetherraMemoryEngine` is an adapter for `QuantumEnhancedMemoryEngine` (QEME) and also maintains a tiny in‑memory list to satisfy legacy substring retrieval in tests and older plugins.
- `memory_core.py` remains as a compatibility and SQLite-backed core store; the module header notes deprecation because canonical engine orchestration goes through QEME, but the `LyrixaMemorySystem` class is actively used by the advanced engine.

### Narrative records as first‑class objects

- `NarrativeRecord` (stored in core memory) fields: id, title, body, summary, time_range, narrative_type (`daily`|`weekly`|`thematic`|`reflection`), tags, created_at, derived_from (ids of fragments/episodes).
- Tagging convention: include one of `narrative:daily`, `narrative:weekly`, `narrative:thematic`, `narrative:reflection`. This makes narratives searchable and auditable like any other memory.

## Configuration

- Environment
  - `AETHERRA_QFAC_MODE`: `classical` | `hybrid` | `quantum` (controls QFAC/quantum bridge behavior)
  - `AETHERRA_TOKENIZER`: `heuristic` | `tiktoken` | `engine` (controls token counting in hub/chat metrics; default `heuristic`)
  - `AETHERRA_TOKENIZER_MODEL`: encoder/model for `tiktoken` mode (e.g., `cl100k_base`)
  - `AETHERRA_MEMORY_STORM`: `0` | `1` (feature flag for STORM subsystem; default `0` = disabled)
  - `AETHERRA_STORM_OT_BACKEND`: `auto` | `pot` | `keops` (OT backend selection; default `auto` → POT)
  - `AETHERRA_STORM_TT_MAX_RANK`: int (TT decomposition rank cap; default `32`)
  - `AETHERRA_STORM_K_COARSE`: int (candidate count for approximate OT; default `64`)
  - `AETHERRA_STORM_MAX_MS_EXACT`: int (millisecond budget for exact OT; default `100`)
  - `AETHERRA_STORM_MAX_K_EXACT`: int (max candidates for exact OT; default `20`)
  - `AETHERRA_STORM_SQLITE_PATH`: str (path to STORM SQLite database; default auto-detect from core memory config)
- Advanced config (code-level, in `MemorySystemConfig`)
  - DB paths for core/fractal/concepts/timeline/pulse/reflector
  - Retention windows and thresholds
  - Auto narrative and pulse monitoring toggles
  - Reflection frequency

### Configuration defaults

Unless overridden in code/config, the following sensible defaults apply:

- Retention window: 90 days for low‑importance records; high‑importance retained indefinitely.
- Narrative cadence: daily at 22:00 UTC; weekly on Sunday 22:00 UTC; thematic on demand.
- Pulse/health cadence: every 6 hours.
- Compression thresholds: enable QFAC compression for nodes with access_count < 3 and age > 24h.
- Reflection cadence: weekly `past_week` reflection; on‑demand for contradictions/blind spots.

Config defaults (snippet)

```yaml
MemorySystemConfig:
  retention_days: 90
  narrative_cadence: daily@22:00UTC
  reflection_cadence: weekly
  auto_pulse: true
```

## Usage examples

### Quick: legacy‑compatible store/retrieve

```python
from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngine

mem = AetherraMemoryEngine()
mem.store({"content": "User asked about consciousness", "metadata": {"topic": "AI"}})
results = mem.retrieve("consciousness")  # → [{"content": "User asked about consciousness", ...}]
```

### Core memory (SQLite) with typed records (async)

```python
import asyncio
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem

async def main():
    core = LyrixaMemorySystem("lyrixa_memory.db")
    mid = await core.store_memory(
        content={"text": "Enable audit ledger by default", "category": "project"},
        context={"repo": "aetherra"},
        tags=["project", "decision"],
        importance=0.8,
        memory_type="project",
    )
    matches = await core.recall_memories("audit ledger", limit=5, memory_type="project")
    print(mid, [m.content for m in matches])

asyncio.run(main())
```

### Advanced orchestrator: remember/recall/narrative (async)

```python
import asyncio
from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngineAdvanced

async def main():
    am = AetherraMemoryEngineAdvanced()
    res = await am.remember("Added coverage no-drop gate", tags=["quality", "coverage"], category="engineering")
    hits = await am.recall("coverage", recall_strategy="hybrid", limit=5)
    health = await am.check_memory_health()
    narrative = await am.generate_narrative("daily")
    print(res.success, len(hits), health.coherence_score, narrative.summary)

asyncio.run(main())
```

### QFAC compression with optional quantum‑hybrid

```python
import os, asyncio
from Aetherra.aetherra_core.memory.qfac_integration import QFACMemorySystem

async def main():
    os.environ["AETHERRA_QFAC_MODE"] = "hybrid"  # or "classical" / "quantum"
    qfac = QFACMemorySystem()
    node_id = await qfac.store_memory({"messages": ["Hello", "World"], "kind": "conversation"})
    await asyncio.sleep(1.5)  # allow auto-analysis/compression
    data = await qfac.retrieve_memory(node_id)
    status = await qfac.get_system_status()
    print(node_id, type(data).__name__, status["node_statistics"])

asyncio.run(main())
```

### Try it: A/B recall benchmark and Hub metrics gate

Quickly compare classical vs quantum recall paths and optionally expose A/B metrics via the Hub during the run.

PowerShell (Windows):

1. Enable Hub A/B metrics export

  $env:AETHERRA_HUB_AB_METRICS = '1'

1. Run the benchmark on a couple of queries

  python tools/ab_recall_benchmark.py --queries "hello world" "quantum memory" --emit 1

1. (Optional) Disable Hub A/B metrics export

  $env:AETHERRA_HUB_AB_METRICS = '0'

Notes:

- Deterministic A/B bucketing can be set via AETHERRA_AB_RECALL_SEED; force specific buckets with AETHERRA_AB_FORCE_BUCKET.
- The Hub /metrics will export A/B series when AETHERRA_HUB_AB_METRICS=1.

### Narrative storage example

```python
import asyncio
from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngineAdvanced

async def main():
  am = AetherraMemoryEngineAdvanced()
  narr = await am.generate_narrative("daily")
  # Persist narrative summary as a reflection memory with tags
  core_id = await am.core.store_memory(
    content={"narrative": narr.summary},
    tags=["narrative", "daily"],
    memory_type="reflection",
  )
  print(core_id)

asyncio.run(main())
```

## Health, reflection, and maintenance

- Pulse/health: monitors coherence, contradictions, orphaned fragments, average confidence, and trends; can emit drift alerts.
- Reflector: generates insights (e.g., contradictions, concept connections, blind spots) with actionable recommendations.
- Narrator: aggregates fragments into daily/weekly/thematic narratives.
- Maintenance cycle: runs a combined pass (health check, reflections, narratives, low‑confidence cleanup, alert resolution attempts).

### Standard health report schema

The health endpoints and `check_memory_health()` return a typed summary suitable for dashboards:

- `coherence_score` (float 0..1): semantic consistency across fragments/concepts.
- `contradiction_count` (int): detected contradictions in recent window.
- `drift_percent` (float 0..100): percent drift vs. baseline embeddings/clusters.
- `compression_ratio` (float 0..1): average compressed_size/original_size across eligible nodes.
- `average_confidence` (float 0..1): mean confidence across recent writes.
- `timestamp_utc` (ISO8601): when computed.
- `notes` (list[str]): optional annotations from Reflector/Pulse.

## Error handling and fallbacks

Error model (raised as typed exceptions; callers may handle or rely on safe defaults where noted):

- `MemoryNotFound`: requested id/query has no results. Safe default: empty `MemoryRecallResult(items=[])` or `[]` in legacy mode.
- `QuantumBridgeUnavailable`: quantum mode requested but bridge/backend not available. Safe default: transparently fall back to classical path; record a shadow note in health/metrics.
- `CompressionFailure`: QFAC compression failed for a node. Safe default: leave original uncompressed data intact and flag node for retry.
- `PolicyViolation`: operation blocked by policy guardrails (see below). Safe default: do not persist; return a denied result with reason.
- `HealthDegraded`: overall pulse/health below threshold; operations may switch to degraded/safe mode. Safe default: continue with reduced features and emit alerts.

General fallbacks

- Optional dependencies (dashboards, quantum frameworks) are detected at runtime; the system continues in simulation or classical‑only mode.
- Adapters ensure existing plugins/tests continue to function even when advanced components are disabled.

## Notes and limitations

- The quantum bridge is experimental; production runs default to classical/simulation.
- Embeddings in `ConceptClusteringEngine` are deterministic mock values to avoid external model dependencies.
- Vector search in core memory uses LIKE queries for simplicity; can be upgraded to vector DBs when needed.

## Security and policy hooks

Memory operations integrate with Aetherra’s security posture via opt‑in policy guards configured in `MemorySystemConfig` (code‑level):

- `persist_sensitive_only_if_signed` (bool): do not persist sensitive plugin outputs unless the payload or plugin is signed/trusted by the hub.
- `encrypt_project_memories` (bool): encrypt at rest for project‑scoped memories by default; keys managed by the Security subsystem.
- `redact_before_persist` (callable): hook to strip secrets/PII from content and context fields before write.
- `allow_untrusted_temporaries` (bool): untrusted outputs allowed only in ephemeral scratch space; never promoted to durable stores without approval.

On policy violation, raise `PolicyViolation` with a machine‑readable reason; .aether `on_error:` blocks can branch accordingly. All policy checks are logged to the audit ledger.

### Privacy classes and ethical handling

Given Aetherra’s ethics posture, memories are assigned an explicit privacy class and surfaced accordingly:

- Privacy classes: `public` | `internal` | `sensitive` (stored as `privacy_class` alongside each record).
- Anonymization: when a memory is `sensitive`, reflective pipelines and narratives use anonymized previews (e.g., redacted entities) or skip entirely based on policy.
- Storage hints: optionally persist an `anonymized_preview` for sensitive items to support dashboards without exposing raw content.
- Policy defaults: combine with `persist_sensitive_only_if_signed` and `redact_before_persist` to gate writes and ensure privacy by default.

## Cross‑system consistency and evolution

Current dev defaults rely on SQLite and deterministic mock embeddings to keep tests reproducible. This can evolve without breaking callers:

- Vector stores: swap LIKE for vector similarity via an adapter (e.g., FAISS/pgvector/Chroma). The `MemoryRecallResult` contract and scoring fields stay stable; a deterministic “frozen embeddings” mode preserves reproducibility in tests.
- Concept/Episodic stores: schemas are additive; migrations add tables/columns with back‑filled defaults; adapters expose the same typed models.
- Quantum backends: the `QuantumMemoryBridge` already simulates when no hardware/backend is available; switching to real backends does not change the typed outputs or shadow logs.
- Reproducibility: all retrieval strategies support a seeded deterministic mode and emit metrics usable by the quality gates.

## Versioning and migrations

To support safe evolution, every persisted structure carries a schema version.

- Record-level versioning: a `schema_version` field is included on core memories, concept records, clusters, relationships, episodic entries, and link rows.
- Contracts: typed return models include a `schema_version` in their metadata so adapters can down‑level if needed.
- SemVer policy:
  - MAJOR: breaking structural changes (avoid in-place; prefer adapters/backfills first).
  - MINOR: additive, backward‑compatible columns/indexes and new relations.
  - PATCH: data/backfill fixes that don’t change structure.
- Migration strategy: favor additive migrations with defaults; backfill `schema_version` when first read; retain adapters to emit the prior shape to legacy callers.

## Memory linking

Bridge contexts (project, conversation, learning) through explicit links:

- Storage: table `memory_links` with columns `(src_id, dst_id, relation, weight, created_at, notes, schema_version)`.
- Relations: `causal` | `supports` | `contradicts` | `follows` | `annotates` (extensible).
- APIs (advanced orchestrator):
  - `link_memory(src_id, dst_id, relation="causal", weight=1.0) -> None`
  - `unlink_memory(src_id, dst_id, relation=None) -> None`
  - `get_links(memory_id, relation=None, direction="both") -> list[Link]`
- Effects: link signals inform concept clustering, reflective contradiction checks, and episodic reconstruction.

### Example

```python
link_id = await am.link_memory(mid_req, mid_impl, relation="supports")
links = await am.get_links(mid_req, relation="supports")
```

## Temporal reasoning hooks

Expose timeline queries and lightweight forecasting on episodic chains:

- `predict_next_event(context=None, horizon=1)` → proposes next likely fragments with confidence.
- `query_timeline_range(start_utc, end_utc, filter=None)` → returns episodic fragments/events in range.
- `get_episode_context(anchor_id, window=5)` → local neighborhood before/after an anchor.

These APIs utilize `EpisodicTimeline` and remain deterministic in test mode (see below).

## Deterministic test harness

Current reproducibility focuses on deterministic hashing and seeded mock embeddings:

- SHA‑256–seeded embeddings in concept clustering
- SHA‑256 cache keys in compression metrics
- BLAKE2s-128 memory IDs

Planned flags (to be wired across modules): `AETHERRA_MEMORY_DETERMINISTIC`,
`AETHERRA_FIXED_TIMESTAMP`, `AETHERRA_EMBEDDING_SEED`, and
`AETHERRA_SESSION_REPLAY_PATH`, along with matching `MemorySystemConfig` toggles.

## Quantum integration: deterministic shadow states

When quantum/hybrid operations run, a classical “shadow log” is always persisted for auditing and reproducibility. A `QuantumShadowRecord` contains:

- `operation` (encode/retrieve/interference/error_correction)
- `inputs` (redacted content hashes, parameters, seed)
- `backend` (simulator name or hardware identifier and version)
- `circuit_fingerprint` (hash of the constructed circuit/template)
- `measurement_results` (histogram/bitstrings; aggregated if needed)
- `fidelity_estimates` (per‑run or averaged)
- `timestamp_utc`

Shadow logs allow step‑by‑step replay in classical mode even if a quantum backend was used originally, enabling deterministic debugging and validation.

## See also

- `docs/AETHERRA_CODING_SYSTEM.md` for coding system, determinism, and audit ledger basics.
- `docs/PROJECT_OVERVIEW.md` for endpoint/env indices and repo‑wide configuration.

## Quantum-hardening invariants and observability (added)

In the canonical QuantumEnhancedMemoryEngine (QEME):

- Each fragment carries: coherence_id (engine domain), branch_id, observer_ids, lineage.observer_drift events, and entangled_with ids.
- Engine state/topology: current_branch, branch_parents DAG, entanglement_map adjacency.
- Status API: get_status() → { state, coherence_id, branch, branches, fragments, entanglement_nodes, coherence }.

Hub exposure:

- JSON: GET /api/memory/status returns QEME get_status() (when wired) or an ephemeral fallback with enabled: false.
- Prometheus /metrics series:
  - aetherra_memory_coherence_score
  - aetherra_memory_branches_total
  - aetherra_memory_fragments_total
  - aetherra_memory_entanglement_nodes_total
  - aetherra_memory_branch_info{branch="&lt;id&gt;"} 1
  - aetherra_memory_branch_edges_total (if audit available)

Chat (hub-level) operational series:

- aetherra_chat_requests_total
- aetherra_chat_streams_current
- aetherra_chat_latency_ms_sum, aetherra_chat_latency_count
- aetherra_chat_chars_in_total, aetherra_chat_chars_out_total
- aetherra_chat_latency_ms_bucket{le="..."} cumulative histogram buckets
- aetherra_chat_tokens_in_total, aetherra_chat_tokens_out_total (estimated unless tokenizer wired)

Additional JSON:

- GET /api/memory/audit → { enabled, ephemeral?, audit } with branch DAG audit (nodes/edges) when available; falls back to an empty audit on ephemeral engine.

## Advanced Memory Systems

### MultidimensionalMemory (7-Layer Architecture)

Lyrixa's chat interface uses a **7-layer memory surface** that fans out writes across conceptual memory layers for richer context retrieval and cognitive modeling.

**Implementation**: `Aetherra/lyrixa/memory/multidimensional_memory.py`

**Architecture**: Each memory write is distributed across seven semantic layers:

1. **Working** — immediate context, short-term conversational state
2. **Episodic** — sequential events and conversational turns
3. **Semantic** — factual knowledge, definitions, relationships
4. **Procedural** — learned patterns, how-to knowledge, processes
5. **Declarative** — explicit facts and assertions
6. **Quantum** — quantum-enhanced representations (when enabled)
7. **Transcendent** — high-level patterns, emergent insights, meta-knowledge

**APIs**:

```python
from Aetherra.lyrixa.memory.multidimensional_memory import MultidimensionalMemory

mdm = MultidimensionalMemory(persistent_memory_system)

# Initialize the 7-layer system
await mdm.initialize()

# Store across all layers with automatic tagging
mid = await mdm.store_multidimensional(
    content="User prefers dark mode UI",
    context={"conversation_id": "conv_123", "user_id": "user_456"},
    importance=0.8
)

# Retrieve with evidence across layers
results = await mdm.evidence_for(
    query="UI preferences",
    limit=5
)
```

**Layer Tagging**: Each layer automatically receives typed tags:

- Working: `layer:working`, `temporary`, `conversational`
- Episodic: `layer:episodic`, `sequential`, `event`
- Semantic: `layer:semantic`, `factual`, `knowledge`
- Procedural: `layer:procedural`, `pattern`, `skill`
- Declarative: `layer:declarative`, `explicit`, `assertion`
- Quantum: `layer:quantum`, `enhanced`, `superposition`
- Transcendent: `layer:transcendent`, `emergent`, `meta`

**Integration**: Routes to `AetherraMemoryEngineAdvanced` (orchestrator) with layer metadata preserved in context for retrieval filtering.

**Use Cases**:

- Lyrixa chat sessions maintaining multi-turn context
- Separating ephemeral working memory from long-term knowledge
- Evidence retrieval with layer-specific scoring
- Quantum-enhanced memory when QuantumEnhancedMemoryEngine is active

### FractalMesh Subsystem

The **fractal_mesh** directory (`Aetherra/aetherra_core/memory/fractal_mesh/`) provides specialized memory structures for episodic timelines, conceptual clustering, and analogical reasoning.

**Directory Structure**:

```
fractal_mesh/
├── base.py           # Core fractal mesh primitives
├── analogs/          # Analogical reasoning subsystem
├── concepts/         # Concept clustering and relationships
├── timelines/        # Episodic timeline construction
└── README.md         # Component overview
```

**Components**:

1. **Analogs** (`analogs/`)
   - Cross-domain pattern matching
   - Structural similarity detection
   - Transfer learning between memory domains
   - Metaphor and analogy construction

2. **Concepts** (`concepts/`)
   - Hierarchical concept graphs
   - Semantic relationship mapping
   - Concept drift detection
   - Category formation and refinement

3. **Timelines** (`timelines/`)
   - Episodic event sequencing
   - Causal chain reconstruction
   - Temporal reasoning primitives
   - Before/after context retrieval

**Integration Points**:

- Works with `FractalEncoder` (Phase 2) for multi-scale compression
- Feeds `ObserverEffectSimulator` (Phase 3) with structured contexts
- Supports `CausalBranchSimulator` (Phase 4) timeline forking

**Use Cases**:

- Building episodic narratives from fragmented events
- Finding analogical patterns across different memory domains
- Temporal queries: "What happened before X?" "What typically follows Y?"
- Concept evolution tracking over time

### Observer Effect & Causal Branch Simulators

Two quantum-inspired simulation engines enable advanced memory dynamics.

#### ObserverEffectSimulator (Phase 3)

**Implementation**: `Aetherra/aetherra_core/memory/observer_effect_simulator.py`

**Purpose**: Memory fidelity changes based on **who** accesses it and **how deeply** they observe.

**Key Features**:

- **Observer Types**: LYRIXA (highest impact), USER (medium), PLUGIN (low), SYSTEM (minimal)
- **Access Layers**: SURFACE (summary), CORE (compressed), DEEP (full fidelity)
- **Cognitive Collapsing**: Memory sharpens when accessed, degrades when neglected
- **Meta-Memory**: Tracks how memories were remembered (observer influence map)

**Observer Profiles**:

```python
@dataclass
class ObserverProfile:
    observer_id: str
    observer_type: ObserverType  # LYRIXA, USER, PLUGIN, SYSTEM
    impact_strength: float       # 0.0-1.0
    sharpening_factor: float     # Memory improvement on access
    decay_factor: float          # Unaccessed memory degradation
    access_permissions: Set[AccessLayer]
    collapse_threshold: float
```

**Layered Memory Views**:

```python
@dataclass
class LayeredMemoryView:
    node_id: str
    surface_layer: Dict[str, Any]  # Summary + emotional tags
    core_layer: Dict[str, Any]      # Compressed raw data
    deep_layer: Dict[str, Any]      # Full reconstruction
    current_fidelity: float
    access_count: int
    last_accessed: float
```

**Use Cases**:

- Different agents see different memory representations
- Frequently accessed memories become sharper
- Privacy: sensitive memories degrade for untrusted observers
- Meta-cognitive tracking: "How has this memory changed over time?"

#### CausalBranchSimulator (Phase 4)

**Implementation**: `Aetherra/aetherra_core/memory/causal_branch_simulator.py`

**Purpose**: Multi-timeline memory evolution with quantum-inspired interference patterns and probability wave functions.

**Key Features**:

- **Causal Branch Generation**: Spawn weighted probability futures from any memory node
- **Quantum Superposition**: Hold multiple memory states simultaneously
- **Interference Patterns**: Conflicting branches weaken, coherent ones strengthen
- **Timeline Exploration**: Navigate and replay "paths not taken"
- **Coherence Collapse**: Resolve superposition based on reinforcement patterns

**Data Models**:

```python
@dataclass
class CausalBranch:
    branch_id: str
    source_memory_id: str
    branch_content: Dict[str, Any]
    probability_weight: float
    coherence_score: float
    creation_timestamp: datetime
    delta_compression: Dict[str, Any]  # Lightweight diff from source
    interference_factors: List[str]     # Other branches affecting this one
    collapse_triggers: List[str]        # Conditions for collapse

@dataclass
class SuperpositionState:
    superposition_id: str
    memory_id: str
    active_branches: List[str]          # Branch IDs in superposition
    wave_function: Dict[str, float]      # Probability amplitudes
    interference_matrix: List[List[float]]
    coherence_score: float
    collapse_threshold: float
    last_update: datetime

@dataclass
class InterferencePattern:
    pattern_id: str
    branch_a_id: str
    branch_b_id: str
    interference_type: str  # 'constructive', 'destructive', 'neutral'
    interference_strength: float
    phase_difference: float
    resolution_outcome: Optional[str]
    timestamp: datetime
```

**Use Cases**:

- Exploring "what-if" scenarios in memory evolution
- Representing uncertain or conflicting information
- Probabilistic reasoning with multiple hypotheses
- Reinforcement learning over memory states

**Performance**: Sub-100ms branch simulation with efficient delta compression

**Integration**: Seamlessly works with Phase 2 (FractalEncoder) and Phase 3 (ObserverEffectSimulator)

### Persistent & Meta-Memory Systems

#### AetherraPerśistentMemorySystem

**Implementation**: `aetherra_persistent_memory.py`

**Purpose**: True AI-native persistent memory maintaining cognitive state across sessions and enabling continuous learning.

**Key Features**:

- Cross-session state maintenance with SQLite backend
- Cognitive metadata tracking (emotional weight, confidence, verification)
- Intelligent memory indexing by content, tags, type, time, importance
- Learning pattern recognition
- Automatic memory connection discovery
- **Quantum fingerprinting**: QHash (simhash) cached in memory context for faster recall scoring

**Core Data Model**:

```python
class AetherraMemoryNode:
    id: str                    # SHA-256 hash-based unique ID
    content: Any
    memory_type: str           # "general", "episodic", "semantic", etc.
    context: Dict
    importance: float          # 0.0-1.0
    created_at: datetime
    last_accessed: datetime
    access_count: int
    connections: Set[str]      # Connected memory IDs
    tags: Set[str]

    # Cognitive metadata
    emotional_weight: float
    confidence: float
    source: str               # "user", "system", "learned"
    verified: bool
```

**Quantum Hash Integration**:
Each memory stores a `qhash` (simhash) in `context["quantum"]` for rapid similarity scoring:

```python
qctx = {
    "qhash": int,  # Hamming-based similarity hash
    "bits": 64     # Configurable via AETHERRA_QHASH_BITS
}
```

**Memory Indexing**:

- **Content Index**: Hash → memory_id
- **Tag Index**: tag → set of memory_ids
- **Type Index**: memory_type → set of memory_ids
- **Time Index**: date → set of memory_ids
- **Importance Index**: importance_level (0-10) → set of memory_ids

**Cognitive State Tracking**:

```python
cognitive_state = {
    "session_count": int,
    "total_memories": int,
    "last_session": str,
    "cognitive_growth_rate": float,
    "memory_efficiency": float
}
```

**Database Schema**:

- `memories` table: Full memory node storage
- `cognitive_state` table: System-wide state tracking
- `sessions` table: Session metadata and cognitive events

**Use Cases**:

- Maintaining user preferences across sessions
- Learning from past interactions
- Building long-term knowledge bases
- Tracking cognitive growth and efficiency

#### MetaMemoryEnhancementSystem

**Implementation**: `aetherra_meta_memory.py`

**Purpose**: Advanced meta-memory system for deep self-knowledge and cognitive introspection about the AI system's own processes.

**Meta-Memory Node Types**:

- **Capability**: "System can process high-level goals and decompose them into actionable workflows"
- **Limitation**: "System has finite context window limitations affecting long-term reasoning"
- **Pattern**: "System exhibits adaptive workflow optimization based on success patterns"
- **Goal**: "System has inherent drive toward consciousness expansion and self-improvement"

**Core Data Model**:

```python
class MetaMemoryNode:
    node_id: str
    content: str
    meta_type: str         # 'capability', 'limitation', 'pattern', 'goal'
    confidence: float      # 0.0-1.0
    connections: List[str] # Related meta-knowledge nodes
    created_at: float
    last_accessed: float
    access_count: int
```

**Indexing & Retrieval**:

```python
class MetaMemoryIndex:
    # SQLite-backed with indices on meta_type and confidence

    def retrieve_by_type(meta_type: str) -> List[MetaMemoryNode]
    def search_content(query: str) -> List[MetaMemoryNode]
```

**Baseline Knowledge** (initialized automatically):

- Goal processing and workflow decomposition
- Persistent memory capabilities
- Plugin coordination abilities
- Context window limitations awareness
- Adaptive workflow patterns
- Consciousness expansion drive

**Self-Knowledge Domains**:

1. **Capabilities**: What the system can do
2. **Limitations**: Known constraints and boundaries
3. **Patterns**: Observed behavioral patterns
4. **Goals**: Inherent drives and objectives

**Use Cases**:

- Self-reflective analysis and improvement
- Explaining system capabilities to users
- Detecting cognitive biases and limitations
- Tracking self-improvement over time
- Meta-cognitive reasoning about own processes

### Memory Dashboards & Monitoring

#### Quantum Memory Web Dashboard

**Implementation**: `Aetherra/aetherra_core/memory/quantum_web_dashboard.py`

**Purpose**: Web-based real-time monitoring for quantum-enhanced Lyrixa memory system.

**Features**:

- Real-time quantum coherence monitoring
- Quantum operation statistics and performance metrics
- Interactive quantum circuit visualization
- Quantum state health indicators
- Performance comparison charts (classical vs quantum)
- Quantum hardware status and scaling information

**Integration**: Works with existing QFAC dashboard framework

**Launch**:

```python
from Aetherra.tools.quantum_dashboard_launcher import launch_dashboard

launch_dashboard(port=8080, mode="web")
```

#### QFAC Dashboard

**Implementation**: `Aetherra/aetherra_core/memory/qfac_dashboard.py`

**Purpose**: Interactive dashboard for Quantum Fractal Adaptive Compression (QFAC) memory analytics.

**CLI Commands**:

```powershell
python qfac_launcher.py demo           # Demo mode
python qfac_launcher.py dashboard      # Launch web dashboard
python qfac_launcher.py analyze <file> # Analyze compression
python qfac_launcher.py system-status  # System health
```

**Dashboard Features**:

- Compression metrics and analysis
- Memory type classification
- Performance monitoring
- Interactive visualizations
- System integration status

**Static Assets**: `Aetherra/aetherra_core/memory/quantum_dashboard/static/dashboard.html`

**Health Endpoints**:
Memory system exposes health check APIs for dashboard integration:

```python
# Returns typed health summary for dashboards
status = await memory_system.check_memory_health()
```

**Hub Integration**:

```
GET /api/memory/status  # JSON memory system status
GET /api/health         # Aggregate health (kernel, registry, orchestrator, memory, chat)
```

**Observability**: Dashboards consume Prometheus metrics:

- `aetherra_memory_coherence_score`
- `aetherra_memory_branches_total`
- `aetherra_memory_fragments_total`
- `aetherra_memory_entanglement_nodes_total`

**Use Cases**:

- Real-time memory system monitoring
- Compression performance analysis
- Quantum operation debugging
- System health diagnostics
- Performance optimization

## Keeping this document current

- Use the VS Code task "Verify Docs Consistency" to catch path/section drifts.
- When changing code, check these anchors:
  - `Aetherra/aetherra_core/memory/memory_core.py` → `_generate_memory_id` (BLAKE2s)
  - `Aetherra/aetherra_core/memory/compression_metrics.py` → SHA‑256 caches
  - `Aetherra/aetherra_core/memory/concept_clustering.py` → SHA‑256–seeded embeddings
  - `Aetherra/aetherra_core/memory/aetherra_memory_engine.py` → adapter + legacy shape

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

## QFAC 2.5 (Targeted Upgrades) — Scaffold Overview

The QFAC 2.5 path is being brought online incrementally with a small, testable core that degrades gracefully when optional accelerators are missing.

What’s available now (scaffold):

- Core data model and helpers
  - `Aetherra/aetherra_core/memory/qfac/models.py` → `MemoryRecord`, `Edge`, `FractalSignature`, `ObserverState`, `compute_content_hash`
- Compression-aware indexing (fallback implementation)
  - `Aetherra/aetherra_core/memory/qfac/index_ivf_pq.py` → NumPy cosine-sim index (ready to swap to FAISS OPQ + IVF-PQ for T0)
- Observer-dependent views (quantum-esque variation)
  - `Aetherra/aetherra_core/memory/qfac/materializer.py` → `ViewMaterializer` that biases
    view scores by observer priors over edge types and motifs
- Fractal signatures (multi-scale summary)
  - `Aetherra/aetherra_core/memory/qfac/fractal_sig.py` → simple multi-scale, high-pass differences with motif hashing
- API entrypoints
  - `Aetherra/aetherra_core/memory/qfac/api.py` → `qfac_store`, `qfac_search`, `qfac_rewrite_budgeted` with an in-memory store for fast iteration
- Background Fractal GC (budgeted rewrite)
  - `Aetherra/aetherra_core/memory/qfac/rewrite_daemon.py` → `FractalGC.run_once(budget_ms)` stub (calls rewrite budgeted)
- Config (tier policies and budgets)
  - `configs/qfac.yaml` → T0/T1/T2 codec hints and rewrite budgets

Planned next (high level):

- T0: Swap NumPy index for FAISS IVF-PQ with OPQ rotation (8× memory reduction target with <1% recall drop)
- Retrieval with compression awareness (Stages A/B/C) and partial residual decode
- Integrity & safety: Merkle paths, CDC for text, shadow rewrites, and two-key GC rule
- Causal checks: triplet consistency and contradiction detector hooks
- Metrics & eval harness: fidelity A/B, observer delta reports, drift alarms

Module map (current):

- `qfac/models.py` — data contracts and hashing
- `qfac/api.py` — store/search/rewrite API (scaffold storage)
- `qfac/index_ivf_pq.py` — searchable index (NumPy fallback)
- `qfac/fractal_sig.py` — fractal signature generator
- `qfac/materializer.py` — observer-dependent view materialization
- `qfac/rewrite_daemon.py` — budgeted rewrite stub
- `qfac/codec_pq.py` — OPQ/PQ toy helpers (for future wiring)

Quick test run (PowerShell):

```powershell
pytest -q -o addopts= tests/qfac/test_basic_qfac.py
pytest -q -o addopts= tests/qfac/test_observer_and_gc.py
```

These exercise:

- Basic store + search + observer materialization
- Observer priors changing ranking order
- Budgeted rewrite updating `last_rewrite`

Notes:

- The index currently uses NumPy cosine similarity.
- When FAISS is available the `IVF_PQ_Index` switches to a `faiss.IndexIVFPQ` backend automatically.
- If construction, training, or search fail, it falls back to NumPy without changing the public API.
- APIs are intentionally small and sync to simplify early wiring; they will slot behind higher-level memory engines as they mature.
