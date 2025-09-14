# Aetherra • Quantum Roadmap (v1.0)

Status: ACTIVE — 2025-08-30 (UTC)

> Scope: Complete, actionable roadmap to mature Aetherra’s quantum layer across Memory (QFAC), Identity/Coherence, Causality/Simulation, Ethics/Safety, Agents, and Kernel — aligned to your Synthetic Soul diagram.

---

## 0) What I infer from your diagram (plain read)

- **Clusters present**: Identity/Self, Ethics/Values, Memory (multi‑tier), Causality/Simulation, Anticipation/Planning, Emotions/Regulation, Agents/Plugins, Kernel/Hub.
- **Flows**: Strong feedback loops between Memory ↔ Identity, Anticipation ↔ Causality, and Ethics gating outward actions. Kernel/Hub interconnects all modules; Agents and Plugins sit at the edges.
- **Implication**: Quantum work should not be isolated to memory; it should add *signals* (coherence, entanglement, branch risk) that influence Identity, Ethics, and Planning in real time.

---

## 1) Phased Quantum Plan (Q0 → Q6)

### Q0 — Classical, Deterministic Baseline (✅ existing)

- Deterministic test profile; reproducible “shadow logs”; memory health & narratives.
- **Exit**: All core flows pass with deterministic seeds and stable metrics.

### Q1 — Hybrid Quantum Simulation (✅ existing)

- QFAC in hybrid mode; branch/coherence metrics; quantum dashboard; entanglement nodes.
- **Exit**: Coherence score and branch counts exposed via Hub; shadow logs attached to memory ops.

### Q2 — Quantum‑Ready Primitives (🔧 implement)

- ✅ **QRNG Service** (quantum‑quality randomness or high‑grade emulation) for seeds/IDs/emotion noise.
- ✅ **QHash/Random Projections** (unitary‑inspired) for high‑fidelity compression and dedupe signals.
- ✅ **Q‑Similarity** (quantum feature maps → classical kernels) for memory recall ranking.
- **Exit**: Benchmarked uplift vs classical baselines (≥3% recall gain or ≥20% size reduction at same fidelity). (in progress via `tools/ab_recall_benchmark.py`)

### Q3 — Quantum Execution Bridge (🔧 implement)

- ✅ **QuantumBridge** abstraction: `Simulator` (default) in place; provider driver stubs tracked.
- Unified recipe format: circuit spec, noise model, shots, seed → stored in audit.
- **Exit**: Nightly CI runs simulations locally; weekly job runs small circuits on *one* provider; identical results within tolerance.

### Q4 — Quantum‑Aware Cognition (🔧 implement)

- Feed **coherence/branch drift** into Identity and Planning; penalize risky branches; boost stable ones.
- Ethics: “observer effect” rule — sensitive actions require high coherence or human confirmation.
- Emotions/Regulation: tie arousal/novelty to entropy readings (bounded).
- **Exit**: Planning success ↑, regressions ↓ in night‑cycle A/B (≥10% fewer rollback events at same task success).

### Q5 — Partial Quantum Offload (🔬 pilot)

- Offload small, value‑dense ops: **entropy seeding**, **hashing**, **random features**, **tiny similarity kernels**.
- Cost/latency budget & cache; graceful fallback to Simulator.
- **Exit**: p95 latency ≤ 1.25× classical; monthly cost within configured budget; correctness within tolerance.

### Q6 — Quantum‑Native Experiments (🔬 research track)

- Explore amplitude‑encoded sketches for compression; error‑mitigated distance estimates; hybrid tensor/quantum pipelines.
- Trainer: build **quantum‑aware evaluation suites** (coherence vs utility tradeoffs).
- **Exit**: At least one Q‑native path that beats classical in either fidelity or cost on a real workload.

---

## 2) Subsystem Tracks (what you have → what to add)

### A) Memory / QFAC

**Have:** Hybrid QFAC, coherence metrics, entanglement nodes, quantum dashboard.
**Add (Q2–Q5):**

1. ✅ **QHash/Unitary‑like projections** for dedupe + fast similarity hints.
2. ✅ **Quantum Random Features** (feature maps → linear kernels) to rank recalls.
3. **Branch‑aware compaction** — compress low‑value branches more aggressively.
4. **Audit recipe** — attach circuit/noise/shots to each quantum‑touched memory op.
**Milestones:**

- ✅ M1: QRNG stub + seeds in audit.
- ✅ M2: QHash library with AB tests.
- ✅ M3: Random‑feature reranker in recall.
- M4: Branch‑aware compaction + dashboard panel.

### B) Identity / Coherence

**Have:** Coherence score, narratives/reflections.
**Add:**

1. **Coherence Budget** per session (used by planner/agents).
2. **Drift Alarms** — when self model diverges from narratives.
3. **Human‑in‑the‑loop Gate** when coherence < threshold.
**Accept:** reduce contradictory actions ≥20% in night‑cycle regressions.

### C) Causality / Simulation

**Have:** Planning + what‑if flows.
**Add:**

1. **Quantum Noise as Exploration** — entropy‑guided branch sampling.
2. **Counterfactual Ledger** — store sparse alt‑branch outcomes + coherence delta.
3. **Branch Reconciliation** — merge rules using “coherence weighted majority”.

### D) Ethics / Safety

**Have:** Capability policies, prompt defense, signing.
**Add:**

1. **Observer‑Aware Policy** — risky ops require high coherence or explicit approval.
2. **Quantum Audit Hooks** — each sensitive decision writes a quantum‑tagged record.
3. **DP Option for Quantum Telemetry** — epsilon setting stored alongside shots.

### E) Agents / Plugins

**Have:** AgentOrchestrator; plugin signing.
**Add:**

1. **Quantum‑capable plugin contract** (`requires: [quantum:bridge]`).
2. **Budget/Quota** — per‑plugin QPU shots & $ limits; cached results.
3. **Evaluation Harness** — agent performance vs coherence signal.

### F) Kernel / Hub

**Have:** Queues, HMR, metrics, site status.
**Add:**

1. **QuantumBridge Service** (sim + providers) with health + calibration cache.
2. ✅ **/quantum/status** endpoint (queue, shots, last calib, cost, error rates).
3. **DLQ for Quantum Jobs** with automatic simulator fallback.

### G) Trainer (forward‑looking)

**Add:**

1. **Quantum‑aware eval suites** (coherence, fidelity, drift, cost).
2. Simple **Q‑adapter** tasks: test random features vs classical.

---

## 3) Engineering Plan (90 days)

### Sprint 1 (Weeks 1–3) — Foundations

- ✅ Implement **QuantumBridge** (Simulator + provider stubs); recipes + audit.
- ✅ Add **QRNG service** with deterministic emulation in test profile.
- ✅ Wire **/quantum/status** + Prometheus: `aetherra_quantum_{shots,queue,err_rate}`.

Status: Completed.

### Sprint 2 (Weeks 4–6) — Algorithms

- ✅ Build **QHash** and **Random Feature** modules (classical fallbacks); integrate in recall.
- Branch‑aware compaction in QFAC; dashboard tiles.
- Add **coherence budgets** to planner; drift alarms.

### Sprint 3 (Weeks 7–9) — Pilot Offload

- Provider driver (choose one); caching + cost guard.
- Ethics policy tie‑in (observer‑aware confirmations).
- Night‑cycle AB tests and KPIs.

**Deliverables:** dashboard panels, docs, AB reports, toggles.

---

## 4) Metrics & Success Criteria

- **Memory**: recall@k (±CI), compression ratio, fidelity loss < threshold.
- **Quantum**: shots/day, p95 latency, cost/day, error rate, simulator↔provider divergence.
- **Coherence/Identity**: coherence score trend, drift alerts/wk, contradictions/wk.
- **Ops**: fallback rate, DLQ depth, provider uptime.

---

## 5) Interfaces & Config (additions)

```yaml
# config.example.yaml
quantum:
  enabled: true
  mode: simulator   # simulator|provider
  provider: null    # e.g., "acme"
  max_shots_per_day: 20000
  cost_budget_usd_per_month: 100
  cache_ttl_sec: 604800
  dp:
    enabled: false
    epsilon: 2.0
```

**Env flags (proposed):**

- `AETHERRA_QUANTUM_ENABLED=1`
- `AETHERRA_QUANTUM_MODE=simulator|provider`
- `AETHERRA_QUANTUM_MAX_SHOTS` / `AETHERRA_QUANTUM_BUDGET_USD`
- `AETHERRA_QUANTUM_CACHE_TTL_SEC`
- `AETHERRA_QUANTUM_PROVIDER` (name/id)

**Env flags (A/B recall + Hub metrics):**

- `AETHERRA_AB_RECALL_MODE=classical|quantum|abp` — global A/B mode
- `AETHERRA_AB_RECALL_PCT=50` — percent of traffic to quantum in `abp` mode
- `AETHERRA_AB_RECALL_SEED=7` — rollout seed for deterministic bucketing
- `AETHERRA_AB_FORCE_BUCKET=classical|quantum` — hard-force bucket (testing)
- `AETHERRA_HUB_AB_METRICS=1` — gate Hub export of A/B series (1=on, 0=off)
- `AETHERRA_QHASH_BITS=64` — SimHash bits; tune vs dedupe fidelity
- `AETHERRA_QHASH_WEIGHT=0.5` — weight of QHash in recall scoring
- `AETHERRA_RFM_IN=128` / `AETHERRA_RFM_OUT=32` / `AETHERRA_RFM_SEED=42` — random feature map settings
- `AETHERRA_RFM_WEIGHT=0.3` — weight of random-feature similarity in scoring

**Endpoints:**

- `GET /quantum/status` — health, queue, calib, cost.
- `POST /quantum/run` — run recipe; returns job id + results.

## 9) PromQL examples (AB recall series)

The Hub exports these Prometheus metrics (gated by `AETHERRA_HUB_AB_METRICS`):

- `aetherra_engine_ab_recall_total`
- `aetherra_engine_ab_recall_classical_total`
- `aetherra_engine_ab_recall_quantum_total`
- `aetherra_engine_ab_recall_latency_ms_sum{bucket="classical|quantum"}`
- `aetherra_engine_ab_recall_latency_ms_count{bucket="classical|quantum"}`
- `aetherra_engine_ab_mode{mode="classical|quantum|abp"}` (gauge)
- `aetherra_engine_ab_pmem_ready` (gauge)

Example dashboards:

- Quantum share (% traffic to quantum in ABP mode):
  `100 * aetherra_engine_ab_recall_quantum_total / max(1, aetherra_engine_ab_recall_total)`
- Avg recall latency by bucket (ms):

  - Classical: `aetherra_engine_ab_recall_latency_ms_sum{bucket="classical"} / clamp_min(aetherra_engine_ab_recall_latency_ms_count{bucket="classical"}, 1)`
  - Quantum: `aetherra_engine_ab_recall_latency_ms_sum{bucket="quantum"} / clamp_min(aetherra_engine_ab_recall_latency_ms_count{bucket="quantum"}, 1)`
- Delta latency (quantum − classical):
  `(
    aetherra_engine_ab_recall_latency_ms_sum{bucket="quantum"} / clamp_min(aetherra_engine_ab_recall_latency_ms_count{bucket="quantum"}, 1)
  ) - (
    aetherra_engine_ab_recall_latency_ms_sum{bucket="classical"} / clamp_min(aetherra_engine_ab_recall_latency_ms_count{bucket="classical"}, 1)
  )`
- Mode gauge:
  `aetherra_engine_ab_mode` with `mode` label; alert if `mode!="abp"` during experiments.
- Persistent memory readiness gauge:
  `aetherra_engine_ab_pmem_ready` (0/1); use to annotate outages.

---

## 6) Risk Register & Mitigations

- **Latency/Cost spikes** → strict budgets, caching, simulator fallback.
- **Non‑reproducibility** → recipe + seed + noise model in audit; deterministic test profile.
- **Security/PII** → DP toggle, redactions, provider allowlist.
- **Over‑promising** → gate claims behind AB reports stored in repo.

---

## 7) Backlog (LOE)

- QuantumBridge + recipes (M)
- QRNG service (S)
- QHash library (M)
- Random Feature reranker (M)
- Branch‑aware compaction (S)
- Coherence budgets (S)
- Drift alarms (S)
- Observer‑aware policy gate (S)
- Provider driver + cache (M/L)
- ✅ `/quantum/status` + metrics (S)
- Trainer evals for quantum features (M)

---

## 8) What to show in demos

- **Dashboard tile** flipping between simulator/provider with shots/latency.
- **AB chart**: classical vs QHash compression ratio vs fidelity.
- **Recall lift** from quantum random features on small corpus.
- **Observer‑aware decision** UI: coherence too low → asks for approval.

---

### TL;DR

You already have the hardest part — **hybrid QFAC + observability**. The next 90 days should: (1) add a **QuantumBridge** with recipes/audit, (2) slot in **quantum‑inspired kernels** for compression/recall, (3) make cognition **quantum‑aware** via coherence budgets and observer policies, and (4) pilot **partial offloads** under strict budgets with automatic fallbacks.

---

## Try it: A/B Recall Benchmark (quick)

Run a tiny benchmark that compares classical vs quantum recall and emits summary JSON. Optionally expose A/B series via the Hub metrics by gating with an env flag.

PowerShell (Windows):

1. Enable Hub A/B metrics export during the run

  $env:AETHERRA_HUB_AB_METRICS = '1'

1. Run the benchmark with a couple of queries

  python tools/ab_recall_benchmark.py --queries "hello world" "quantum memory" --emit 1

1. (Optional) Disable Hub A/B metrics export after

  $env:AETHERRA_HUB_AB_METRICS = '0'

Notes:

- The benchmark forces classical then quantum paths to compare latency and surfaces counters the Hub can export when AETHERRA_HUB_AB_METRICS=1.
- Deterministic test profiles can pin seeds via AETHERRA_AB_RECALL_SEED and simulator flags.

---

## Definition of Done + doc sync

Mark an item as complete only when all apply:

- Tests: capability suite is green; add/extend unit tests where behavior changed.
- Metrics: relevant Prometheus series exported (if applicable) and visible via Hub /metrics.
- Docs updated:
  - docs/PROJECT_OVERVIEW.md — endpoints and environment variables index.
  - docs/AETHERRA_MEMORY_SYSTEM.md — behavior, flags, and memory/recall notes.
  - docs/QUANTUM_OVERVIEW.md — bridge/modes and status (if impacted).
  - docs/QFAC_MODE_GUIDE.md — modes/tuning (if impacted).
  - README.md — quickstart and “Try it” example (if user-facing).
- Gates: run “Verify Docs Consistency” and “Quality Gates (Tests + Coverage No-Drop)”.

Lifecycle note:

- When this roadmap reaches COMPLETE status, move this file to `docs/roadmap/` and add a completion header (date, tag). Re-run docs consistency to ensure indexes and links remain valid.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

