# STORM Ops Guide

How to operate and observe STORM in production and test profiles.

## Status and capabilities

- `/api/memory/status` includes a `storm` block:
  - `cells, overlaps, inconsistency_energy, tt_rank`
  - `backends: { pot: bool, keops: bool, numpy: bool }`
  - `tt_rank_cap: int`
  - `selected_backend: "pot"|"keops"|"numpy"`
  - `exact_ot_active: bool`
  - `last_recall: { approximate: bool }`

## Metrics (Prometheus)

- `aetherra_storm_ot_cost_avg`
- `aetherra_storm_sheaf_inconsistency`
- `aetherra_storm_tt_rank`
- `aetherra_storm_branch_barycenters_total`
- `aetherra_storm_maintenance_total`
- `aetherra_storm_maintenance_last{action="rank_trim|barycenter_refresh|ot_cache_prune"}`
- `aetherra_storm_recall_latency_ms_p95`
- `aetherra_storm_approximate_recalls_total`

## Night‑cycle safety rails

- TT rank clamp to `AETHERRA_STORM_TT_MAX_RANK`.
- Cap barycenter refreshes per cycle.
- Limit OT cache size.
- Emit a single maintenance summary to `/metrics`.

Storage:

- Sheaf cover (cells/overlaps) persists in SQLite with `storm_schema_version` and lightweight migrations.

## Budgets and SLOs

- Pass `max_ms` and `max_K_exact` to recall.
- If budget exceeded → skip exact OT and tag `metadata.approximate=true`.

## Evidence tags in Chat

- Ensure Engine/Chat maps STORM fields to tags:
  - `ot:<float>` — transport cost (lower is better)
  - `coh:<float>` — normalized coherence (higher is better), using `coh = 1 / (1 + sheaf_inconsistency)`
  - `pers:<float>` — persistence bonus

## Deterministic profile (CI/test)

- Lock seeds and ANN ordering; add a tie‑breaker in scoring.
- Prefer numpy fallback backends for reproducibility.

## Troubleshooting

- High OT cost → verify backends and budgets; increase shortlist or enable KeOps.
- Rising inconsistency → check night‑cycle cadence; review branch barycenters.
- Missing tags → confirm `storm_meta` mapping in Engine/Chat path.

## Security and privacy

- No raw content in logs or metrics.
- Keep OT debug logs at ID/aggregate level (tests enforce this).
