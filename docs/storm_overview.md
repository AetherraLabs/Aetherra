# STORM Overview (Sheaf–Transport Optimized Retrieval Memory)

A one–pager for engineers and ops.

## Quick troubleshooting (If X → then Y)

| Symptom                     | Likely cause                          | Action                                                                                                           |
| --------------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| High `ot:` cost             | Shortlist too small or slow backend   | Increase `AETHERRA_STORM_K_COARSE`/`max_K_exact`; ensure POT/KeOps available; check `selected_backend` in status |
| Low `coh:` value            | Sheaf inconsistency rising            | Run night‑cycle; verify barycenter refresh cadence; watch `aetherra_storm_sheaf_inconsistency`                   |
| Frequent `approximate=true` | Budget exceeded                       | Raise `AETHERRA_STORM_MAX_MS` or reduce K; confirm SLOs                                                          |
| Missing tags in Chat        | Evidence mapping disabled             | Ensure Engine/Chat maps `storm_meta` to `ot:/coh:/pers:`                                                         |
| Status shows numpy only     | Optional deps missing or test profile | Install POT/KeOps; `AETHERRA_PROFILE=test` prefers deterministic numpy                                           |

## What it is

- Additive memory retrieval/orchestration module.
- Treats memory as a sheaf of probability measures across semantic (embeddings), episodic (time), and conceptual (graphs) spaces.
- Uses Optimal Transport (OT) and Gromov–Wasserstein (GW) for alignment and branch/observer reconciliation.
- Maintains coherence via sheaf inconsistency energy.
- Boosts durable themes with TDA persistence.
- Compacts high‑order associations with Tensor‑Train (TT).

## Minimal contract

- Returns canonical `MemoryRecallResult` with `source="storm|storm_hybrid"`.
- `metadata.storm_meta = {cell_id, transport_cost, sheaf_inconsistency, persistence_bonus, freshness, branch_id?}`.
- Evidence tags in Chat: `ot:<float>`, `coh:<float>`, `pers:<float>`.

## Scoring (informal)

S(x|q) = kernels_sem/epis/concept − OT cost − sheaf inconsistency + persistence bonus + freshness.

Coherence tag math:

- Use `coh = 1.0 / (1.0 + sheaf_inconsistency)` in [0,1] everywhere (evidence tags and status JSON).

## Backends matrix

- OT: POT | KeOps | numpy fallback (auto‑select).
- TT: numpy (rank‑capped); future: optional torch path.
- TDA: optional (giotto‑tda/persim); disabled if unavailable.

Preference:

- Auto picks POT by default; choose KeOps only if GPU is present and `AETHERRA_PROFILE!=test`.

## Flags (env)

- `AETHERRA_MEMORY_STORM=0|1`
- `AETHERRA_STORM_OT_BACKEND=auto|pot|keops`
- `AETHERRA_STORM_TT_MAX_RANK=32`
- `AETHERRA_STORM_K_COARSE=64`
- `AETHERRA_STORM_MAX_MS=120` (example)
- `AETHERRA_STORM_MAX_K_EXACT=16` (example)
- `AETHERRA_PROFILE=test` (deterministic)

## Budgets and SLOs

- Recall accepts `max_ms` and `max_K_exact`.
- If budget exceeded, skip exact OT and set `metadata.approximate=true`.

## Deterministic profile

- Lock seeds, fix ANN ordering, add tie‑breakers; prefer numpy fallbacks.

## Troubleshooting

- High OT cost: increase K_coarse/K_exact; check backend (KeOps/POT) availability in `/api/memory/status` → `storm.backends`.
- High inconsistency: run night‑cycle; check barycenter refresh cadence.
- Missing evidence tags: ensure `storm_meta` mapping in Engine/Chat path.

## Links

- `docs/STORM_INTEGRATION_PLAN.md`
- `docs/storm_ops.md`
