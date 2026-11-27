# Runtime Evidence Integrity and Simulation Isolation Plan

Status: **PROPOSED — investigation and staged implementation, not a readiness decision**  
Source reviewed: `main@64d5d5ccecbf2c445eac80902aad537e34d30ebf` (2026-11-27).  
Owner: Aetherra runtime, Memory, Security, Guardian and subsystem maintainers.  
Scope: Aetherra-owned source and normal launcher/Hub/Observatory paths. No new autonomy, production, or unattended GO.

## Objective and non-objectives

**Objective:** Normal operation must never present fabricated measurements, mock embeddings, speculative outputs, synthetic task successes, placeholder health, or unexecuted actions as authentic observed results. An unavailable dependency must yield an explicit unavailable/degraded/blocked response with provenance, not a plausible made-up number or success. Security/Guardian decisions, approvals and evidence must retain exact authority.

**Not objectives:** delete all tests/mocks, strip scientifically meaningful simulations, automatically enable quantum hardware, replace legitimate deterministic *algorithms* with stochastic ones, migrate storage speculatively, or remove proven compatibility import aliases without reference checks. Reproducibility remains valuable in tests.

This is an evidence classification and migration plan, not a claim that every search hit is reachable in the supervised alpha profile. Inspect call sites, feature flags and startup registration before changing code.

## Classification

Every candidate must be marked with: path, callable, owner, mode/profile, entrypoint/callers, actual production reachability, data source, effects, user surface, trust authority, test evidence, and disposition.

| Kind | Definition | Allowed disposition |
| --- | --- | --- |
| REAL | Measured, executed or inferred from genuine input with documented algorithm and validation | Keep, attach evidence/provenance |
| DERIVED | Deterministic computation from real observed inputs | Keep if labeled as estimate/inference and bounded |
| SIMULATION | Deliberate model/scientific simulation or scenario | Keep behind explicit opt-in, label `simulated`; never report as actual device or event |
| FIXTURE | Synthetic test/mock data, deterministic responses and failure injection | Keep in tests or isolated dev harness; never eligible as live evidence |
| COMPATIBILITY | Import shims or adapters that delegate to real underlying behavior | Keep with ownership, contract and regression tests; not fake data by name alone |
| PLACEHOLDER | No actual measurement/execution; hardcoded output, synthetic success, stub registry or fabricated telemetry | Replace, disable, or fail closed on normal runtime |
| UNKNOWN | Backend or provenance cannot be established | Explicit unknown/unavailable; cannot be healthy or activate privileged work |

Hashing for content identity, signed audits, cache keys and deterministic scheduling does not inherently mean mock data. **Hash-to-random semantic embeddings are not semantically meaningful** and belong under PLACEHOLDER, regardless of stable output.

## Current source-confirmed candidate ledger

The rows below are **source observations**, not proof of activated exposure. Each requires a traced normal-launch call chain and relevant test.

| ID | Component and path | Observation | Proposed first action |
| --- | --- | --- | --- |
| RI-001 | `Aetherra/aetherra_core/memory/concept_clustering.py` | `_generate_embedding` seeds global PRNG from SHA-256 and creates a 384-dimensional vector | Shared real local embedder, versioned migration |
| RI-002 | `Aetherra/aetherra_core/memory/storm/{ot_helpers.py,engine.py}` | Query/candidate embeddings use SHA-derived 128-dimensional vectors, persisted and reused for OT/sheaf | Real embedder; trace all callers, invalid cache migration, shadow quality check |
| RI-003 | `aetherra_hub/services/trainer.py` | In-memory jobs transition by delay; eval score `0.75`; no model training performed | Never report these as executed training; explicit unsupported until a real worker is integrated |
| RI-004 | `aetherra_hub/blueprints/quantum.py` | `available: true`, `backend: simulated`; coherence defaults to 1.0, stable defaults true | Ground availability/backend/metrics in registered backend evidence; unknown when absent |
| RI-005 | `Aetherra/aetherra_core/kernel/quantum_bridge.py` | Mock query result and coherence 1.0 | Isolate simulator backend or return unsupported/unknown |
| RI-006 | `Aetherra/homeostasis/ethical_cognitive_integration.py` | Fallback bias 0.1, fixed alignment 0.85, integrity 0.78/0.82, meta-awareness 0.65 and fixed confidence | Replace with observed calculations, or leave fields unavailable and prevent downstream false confidence |
| RI-007 | `Aetherra/homeostasis/multi_node_integration.py` | Simulated stability and fixed available capacity 0.6 | Require actual peer/system measurements, fenced timestamps and unavailable handling |
| RI-008 | `aetherra_self_incorporation.py` ActivityMonitor | Returns fixed 5% CPU / 30% memory, treated as low load | Measured OS telemetry; missing telemetry blocks optional heavy work |
| RI-009 | `Aetherra/schedulers/night_cycle_runner.py` | Exception measuring load returns zero, allowing night cycle | No metric -> unknown and skip/defer, not idle |
| RI-010 | `Aetherra/aetherra_core/file_system/compression_analyzer.py` | "Performance" timing is calculated from byte counts rather than measured | Use monotonic measured times or distinguish predictive estimates |
| RI-011 | `aetherra_agent_fabric.py` | A fallback can return `ok: true` with `executed: false` and no executor; optional mock registry | Make top-level success false or `unsupported`; mark dev/test-only registries explicitly |
| RI-012 | `aetherra_os_launcher.py` | Test/CI early QFAC stub may register; `AETHERRA_NO_FAKE_DATA` logic sets `AETHERRA_QFAC_VALIDATOR_FAKE=1` while apparently disabling fakes | **Trace effective semantics first**; prove test/dev stub cannot pass readiness in normal full mode; verify flag inversion before changes |
| RI-013 | `aetherra_self_incorporation.py` SecurityGate | Signature validation carries explicit placeholder implementation | Align with existing strict Security signing; deny unverified artifacts |
| RI-014 | `aetherra_self_incorporation.py` LearningEngine | Recent audit helper is placeholder empty data; night optimization includes placeholder path | Display disabled/not implemented and no learning success or improvements until evidenced |
| RI-015 | `Aetherra/aetherra_core/memory/quantum_memory_bridge.py` and QFAC/quantum adapters | Explicit simulation fallback in optional experimental modes | Preserve scientific simulator with separate status `simulation`, not real quantum hardware |
| RI-016 | `docs/STUB_INVENTORY.md` | March 2026 generated inventory with stale totals and historic line numbers | Rebuild reachability-aware inventory; do not use its totals as current facts |

Also inspect: Hub/Observatory default 0/healthy/true fields, service registry status, telemetry metrics, agent tool execution and success reporting, test-mode environment parsing, model provisioning, optional plugin adapters, sensor status, health dashboards, QFAC fake metrics, and prototype scores outside Memory.

## Cross-cutting invariants (Phase 0)

1. Add a typed evidence envelope (or extend the existing canonical one; no second authority) with `kind` = measured | derived | simulated | fixture | unavailable | unknown, `source`, `observed_at`, `source_revision`, `profile`, `backend/model_revision` where relevant, `quality`, `freshness`, `error_code` and `redaction`. Do not fabricate a timestamp for missing observations.
2. `available`, `healthy`, `ready`, `completed`, `executed`, `trained`, `verified` may become true only from actual corresponding evidence and authority checks. A successful HTTP 200 is not proof of task completion.
3. No background job, night optimization, security downgrade, automatic integration or model decision may be authorized from simulated/unknown telemetry. Missing input means skip, defer, or explicit blocked status. Guard against stale values and loss of source.
4. Preserve offline/local privacy for personal memory: no model downloads or network egress during recall. Prefer already-provisioned `sentence-transformers/all-MiniLM-L6-v2` with pinned revision `c9745ed1d9f207416be6d2e6f8de32d1f16199bf` through an injectable, local-only provider.
5. Tests may inject fake producers only under explicit isolated test profiles. Test environment flags cannot silently select mocks in normal launcher; feature flags must be reviewed as policy, not ad hoc fallbacks. Tests should assert prohibition at runtime and after restart.
6. Guard against misleading aggregate UI: distinguish `unknown` from healthy, `simulated` from observed, absent scores from real zeros, and pending from completed. Keep Observatory read-only.
7. Leave historical failure receipts, signed audits, C2b ownership, Guardian/Security and Memory persistence contracts intact. No acceptance claims from passing reruns alone.

## Ordered delivery phases

### P0 — Whole-repository inventory and reachability audit (required)

- Scan **owned runtime Python/TypeScript/config** and docs for `mock|fake|stub|simulat|placeholder|hardcoded|TODO|pass|random|seed|return 0|return 1|healthy|available|success|degraded|fallback`; use AST/data-flow and targeted manual checks rather than string counts.
- Traverse launcher -> registry -> Hub -> UI, optional feature flags, environment profiles and output schema. Identify active, dormant, research-only, compatibility and tests. Cross-reference the older `STUB_INVENTORY` without trusting stale totals.
- Record each `RI-*` in a new structured source-of-truth inventory with reproducible location, current owner, callers, input/output contract, live reachability, severity, test, required replacement, and decision. Do not automatically disclose private vulnerabilities in public tickets.
- Establish baseline tests, expected failures/skips, CI compatibility and security constraints. Include `NO_FAKE_DATA`/QFAC flags and no-runtime-mocks enforcement.
- Acceptance: zero **unclassified reachable** synthetic success/health/telemetry paths, not zero words matching mock.

### P1 — Stop fabricated readiness/success and unsafe telemetry (first code changes)

- Fix or explicitly disable truthful outcome gaps: trainer's no-op completed jobs and fixed eval score; Quantum Hub availability/coherence; quantum kernel mock results; Agent Fabric fallback `ok: true`; QFAC startup stub status. For functionality that cannot genuinely execute, return `unsupported`, `unavailable`, or `simulation` (with reason); preserve backward-compatible schema only when honest.
- Replace synthetic resource, ethics, multi-node and compression metrics with measured inputs or typed unknowns. Device probes should report actual support and freshness; do not infer 0% CPU or 100% coherence from absence of a probe.
- Repair `AETHERRA_NO_FAKE_DATA`/QFAC flag semantics **only after tracing the consumer and negative tests**. Ensure full launcher cannot register or report a test stub as healthy. Mock service guards must examine actual registry identity and replace/loss events, not names alone.
- Gate all scheduled/heavy work on measured health and available budget; no synthetic approvals. Add error-injection, missing-provider, cold-start, profile-isolation, service-loss and HMR/rollback tests.
- Acceptance: no fabricated `healthy`, `available`, `completed` or success in enabled normal profiles; tests prove false-positive prevention, bounded behavior and honest UI/Hub errors.

### P2 — Shared real embedding provider and model contract

- Reuse the existing pinned offline MiniLM embedder infrastructure; extract a thread-safe injectable provider if required. Define dimension, normalization, model ID/revision, device, preprocessing policy, batching, maximum input, timeout and observability; provision before runtime.
- Replace ConceptClustering's hash-seeded embedding generator with the real provider. Do not reseed global random state. Validate semantic neighbor pairs, similarity ordering and cluster behavior.
- Replace STORM's query, candidate and sheaf embedding calls, preserving typed recall contracts. Distinguish `storm` and `storm_hybrid` behavior; fallback to **real base recall** only where explicitly configured, with `degraded` provenance, not to random-vector search.
- CRITICAL migration: STORM's `storm_cells` currently keys embeddings by content hash and `dim/dtype`, **not model ID/revision**. Existing 128-dim fake vectors cannot be silently reused as real MiniLM vectors. Introduce provenance/version-aware cache namespace or an atomic shadow index, rebuild with bounded batches, verify swap/rollback and protect user data. Concept/clusters/centroids likewise need versioned rebuild or safe isolation, not mixed vector spaces.
- Run offline qualitative retrieval evaluation plus quantitative held-out sets for ranking, STORM OT/TDA/sheaf and clustering; report baseline, recall@k, precision@k, latency, memory and failure modes. Don't promise improvement without measurements.
- Acceptance: zero hash-random embeddings on enabled runtime recall/clustering paths; model-missing fails visibly, never silently substitutes a mock; existing persisted memories remain intact across migration/restart.

### P3 — Domain-specific simulation and compatibility triage

- Review QFAC, QuantumMemoryBridge, quantum-inspired metrics, observer-effect and causal-branch simulators. They may remain as explicitly labeled research simulations; no claim of hardware execution/physical quantum advantage without evidence. Remove only false claims, fallback misclassification or privilege paths.
- Inventory compatibility shims, including moved import aliases. Preserve those that delegate to real implementations; mark test-only adapters and remove retired ones only after import/reference and Windows CLI compatibility tests.
- Verify each remaining placeholder in Self-Incorporation, script executor, agent fabric, plugin integration, perception/telemetry and Hub is either implemented, isolated, deferred with truthfully unavailable contract, or removed. Classify real deterministic heuristics as `derived`, not automatically fake.

### P4 — Integrity tests and automated anti-regression gates

- Implement source-aware lint/AST checks for synthetic status/fixed score and unauthorized fixture imports in runtime entrypoints; allow explicit reviewed exceptions with owner and rationale. Do **not** blanket-block `random` or `hashlib`.
- Add normal-launch integration tests for disabled/strict/optional profiles, missing models, missing sensors, QFAC stub flags, unexpected services, restart, and UI/Hub evidence payloads. Include negative security and unauthorized-action cases.
- Verify genuine backend behavior with real local fixtures and measured operations; use simulated inputs only for testing, clearly labeled as fixtures.
- Add a CI report with `reachable/unreachable/test-only/research/compatibility` counts and signed/evidence-linked closure. Existing CI failures and skips remain tracked separately; no automatic closure.

### P5 — Documentation, Observatory and sign-off

- Update `docs/AETHERRA_MEMORY_SYSTEM.md`, STORM/QFAC/quantum docs, system index, runbooks and public maturity language **only after verified implementation**. Keep preserved historical documents as history.
- Add Observatory provenance indicators for real/derived/simulated/unavailable; distinguish prediction from observation and current state from old snapshots.
- For each corrected `RI` item require source revision, before/after behavior, proof of caller reachability, focused negative test, full relevant integration verification, migration/rollback receipt, limitations and reviewer.
- Close a specific issue only on its acceptance evidence. This plan does not confer production readiness, unattended use, permission to act, or closure of existing unknown-cause defects.

## Suggested workstream ownership and ordering

| Priority | Workstream | Dependencies |
| --- | --- | --- |
| 0 | Inventory and cross-cutting evidence contract | None; parallel review of source |
| 1 | Truthful status/operation and missing telemetry | P0, Guardian/Security review |
| 2 | Local real embedding adapter / safe schema migration | P0, Memory ownership, baseline retrieval tests |
| 3 | STORM/clustering semantic evaluation and rollout | P2 and offline eval |
| 4 | Research simulation and compatibility shim audit | P0; independent of embedding replacement where safe |
| 5 | CI gates, docs and reviewer signoff | Continuous, finalized after P1–P4 |

**Do not batch all subsystem replacements into one PR.** Make independent bounded PRs (e.g., status truthfulness; telemetry truthfulness; QFAC flag invariants; embedding adapter; Concept Clustering migration; STORM migration; compatibility/research status; CI/Observatory docs). Existing temporal runtime PR #380 and legacy defect investigations must remain separate.

## Minimum evidence per implementation PR

- Precise `RI` rows and enabled runtime callers, source SHA, profile and model/backend revisions.
- Before/after observed outputs, explicit unknown/unavailable behavior, and evidence that no fake can be selected in full mode.
- Synthetic test fixtures clearly labeled and isolated; real backend verification where relevant.
- Negative authorization tests, rollback/data recovery tests, lifecycle/timeout budget checks.
- Performance and regression results including actual exit/skips and preserved failures.
- Updated docs and readiness limitation, no false implication of a new alpha or beta GO.

## Immediate Codex task sequence

1. Inventory all reachable runtime producers/sinks and verify RI-001–RI-016; emit a detailed machine-readable list with evidence and an actual dependency graph. Include new findings; do not limit scope to this list.
2. Inspect QFAC validator flag consumers and full-mode/no-fake boot behavior; document whether the apparent inversion creates fabricated metrics, then patch with tests if proven.
3. Implement P1 truthful health/success handling for one narrow vertical per PR, using existing Guardian and Security gates. Negative tests first.
4. Design and review Memory embedding schema migration before touching persisted STORM/concept vectors. Implement shadow migration and measured retrieval validation in separate follow-up PRs.
5. Expand anti-regression gates and update documentation after the new implementations are verified.

This document is a proposal. It is not evidence that all active paths have been audited, a completed implementation, or an approved change to runtime authority.
