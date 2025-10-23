# STORM On-Call Runbook

Audience: On-call, SRE, Memory/Engine owners

## Where to look first

- `/api/memory/status` storm block:
  - `selected_backend`, `exact_ot_active`, `tt_rank_cap`
  - `last_recall.approximate` (budget skip signal)
  - `coh` via `1/(1+sheaf_inconsistency)` (expect near 1.0 when healthy)
- Hub `/metrics` (Prometheus):
  - `aetherra_storm_ot_cost_avg`, `aetherra_storm_sheaf_inconsistency`
  - `aetherra_storm_recall_latency_ms_p95`, `aetherra_storm_approximate_recalls_total`
  - `aetherra_storm_tt_rank`, `aetherra_storm_branch_barycenters_total`
  - `aetherra_storm_maintenance_total`, `aetherra_storm_maintenance_last{action=...}`

## Quick actions (If X → then Y)

- High `ot:` cost → Increase `AETHERRA_STORM_K_COARSE`/`AETHERRA_STORM_MAX_K_EXACT`; ensure POT/KeOps available; check `selected_backend`.
- Low `coh:` (coherence) → Run night-cycle; confirm barycenter refresh cadence; watch inconsistency trend.
- Approximate spike → Raise `AETHERRA_STORM_MAX_MS` or reduce K; confirm Kernel SLOs and budget.
- Missing evidence tags → Ensure Engine/Chat evidence mapping (ot:/coh:/pers:) is enabled.

## Change management

- Feature flag (global kill switch): `AETHERRA_MEMORY_STORM=0` to disable.
- Backend choice: `AETHERRA_STORM_OT_BACKEND=auto|pot|keops` (auto prefers POT; KeOps only with GPU, non-test).
- Budgets: `AETHERRA_STORM_MAX_MS`, `AETHERRA_STORM_MAX_K_EXACT`.
- Persistence: SQLite at `configs/storm_sheaf.db`; schema in `configs/sql/storm_schema_v1.sql`.

## Rollback steps

- Config rollback: set `AETHERRA_MEMORY_STORM=0`; reload service.
- Code rollback: one-commit revert protected by import guard; orchestrator kill-switch path ensures `super().recall(...)` is used when disabled.
- Data safety: use `tools/storm_backup.py backup` before schema migrations.

## Alerts (suggested)

- Warn on `aetherra_storm_ot_cost_avg` above threshold over 5 minutes.
- Warn on rising `aetherra_storm_sheaf_inconsistency` over 15 minutes.
- Warn on rate spikes of `aetherra_storm_approximate_recalls_total`.

## Notes

- Test profile (`AETHERRA_PROFILE=test`) enforces deterministic behavior: seeds locked, numpy fallbacks, and tie-breakers in scoring.
- No raw content in logs/metrics; IDs and aggregates only.
