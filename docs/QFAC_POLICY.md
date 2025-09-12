# QFAC Policy and Live-Metrics Gating

This document explains the operator knobs for QFAC (classical | hybrid | quantum) and how live coherence/drift metrics gate decisions.

## Modes and Policy

- AETHERRA_QFAC_MODE: desired mode (classical | hybrid | quantum). Default: classical
- AETHERRA_QFAC_POLICY: enforce | shadow | off
  - enforce (default in prod/staging): apply gates and may downgrade to classical
  - shadow: report what would happen, but do not downgrade
  - off (default outside prod/staging): accept desired mode
- AETHERRA_PROFILE: prod | production | staging | test | dev

## Validation and Backend Selection

- AETHERRA_QFAC_VALIDATED: 1/true/yes marks a validated quantum path present
- AETHERRA_QFAC_BACKEND: simulator | qiskit | ionq | aws_braket | azure | custom
- AETHERRA_QFAC_ALLOW_SIMULATOR_IN_PROD: 1 to allow simulator as a validated backend in prod

In prod/staging with policy=enforce, hybrid/quantum requires a validated backend unless the simulator override is set.

## Health Gating via Coherence/Drift

Thresholds (defaults):

- AETHERRA_QFAC_GATE_MIN: 0.85
- AETHERRA_QFAC_HARD_MIN: 0.75
- AETHERRA_QFAC_DRIFT_COOLDOWN_SEC: 300

Runtime signals (used if available):

- AETHERRA_QFAC_COHERENCE_EMA: latest coherence EMA value
- AETHERRA_QFAC_LAST_DRIFT_ALERT_EPOCH: epoch timestamp of last drift alert

The QFAC memory integration best-effort fetches live coherence metrics from the Aetherra Engine/Agent Orchestrator via the Service Registry. If live metrics are not available, env-provided metrics can be used. In prod with policy=enforce, missing EMA will deny hybrid/quantum (downgrade to classical).

## Decision Metadata

QFACPolicy.resolve_mode returns:

- mode: effective mode
- allowed: True if desired was allowed; False if downgraded
- reason: reason string (e.g., no-validated-backend, ema-below-gate-min, recent-drift-alert)
- thresholds: snapshot of thresholds and backend/validation flags
- metrics_used: {ema, last_drift_alert}

QFACMemorySystem exposes the last decision under `get_system_status()["qfac_policy"]`.

### Prometheus Metrics (Exported via /metrics)

The Hub surfaces policy gating state for observability and shadow-mode auditing:

- `aetherra_qfac_policy_mode_current` (gauge): 0=classical, 1=hybrid, 2=quantum effective mode.
- `aetherra_qfac_policy_allowed` (gauge 0/1): 1 if desired mode accepted; 0 if downgraded.
- `aetherra_qfac_policy_info{key="reason",value="..."}` (gauge=1): reason string for last decision.
- `aetherra_qfac_policy_info{key="policy",value="..."}` (gauge=1): active policy mode (`enforce|shadow|off`).

Operational Usage:

- Alert when `aetherra_qfac_policy_mode_current` < 1 for sustained periods while `AETHERRA_QFAC_MODE` requests `hybrid|quantum`.
- Create audit dashboards listing top `reason` label values to justify downgrades.
- In shadow mode (`policy=shadow`), track potential production impact before switching to `enforce`.

## Live-Metrics Source Path

- Service Registry -> Aetherra Engine instance
- Engine.agent_orchestrator.get_system_status() or Engine.get_system_status()["agent_orchestrator"]
- coherence_policy: { ema, last_drift_alert, gate_min, hard_min, window_size }

If none are available, the system falls back to environment metrics.

## Examples

- Non-prod (test/dev), policy off:
  - Desired=hybrid, EMA low -> allowed (reason: non-prod-allow)
- Prod, policy enforce, validated backend, EMA >= gate_min, no recent drift -> allowed
- Prod, policy enforce, missing EMA -> downgraded (reason: missing-coherence-ema)
- Prod, policy shadow, missing validation/metrics -> not downgraded, reason starts with shadow-would-deny:

## Safety Defaults

- Fail-closed in prod/staging: classical unless validation and health thresholds pass.
- Operators can set policy=shadow to audit effects before enabling enforce.
