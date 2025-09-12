# Aetherra Project Overview

This document provides a comprehensive overview of the Aetherra AI Operating System: core subsystems, services, modules, configuration, and how to validate end-to-end.

## Scope and Structure

Primary source tree: `Aetherra/`

- aetherra_core/ — OS core (engine, kernel, memory, plugins, config)
- lyrixa/ — Lyrixa assistant (intelligence, GUI, plugins, integrations)
- plugins/ — Ecosystem plugins (std + lyrixa)

See also: the comprehensive Memory System guide: [Memory System](docs/memory_system.md).
Stats enhancements:

- The Hub stats endpoint (api stats) payload includes a lyrixa_chat object with best-effort availability:
  - { registered: bool, status?: "healthy"|"degraded"|..., registered_at?, last_heartbeat? }
  - If registry is not available, registered will be false.

---

## Auto-Generated Overview (analyze_project.py) — 2025-09-11 (refreshed)

Generated at: 2025-09-11 (manual refresh of key deltas)

### Deprecation Notice (Active)

The monolithic legacy hub launcher script `aetherra_hub_server.py` is deprecated and retained only as a thin shim issuing a `DeprecationWarning`. Invoke the Hub via:

```bash
python -m aetherra_hub.compat
```

Enforcement layers prevent new imports of the legacy script (quality gate + pre-commit). See `docs/DEPRECATION_TRACKER_LEGACY_HUB.md`.

### Repository Analysis Summary

This repository contains the Aetherra AI Operating System and Lyrixa assistant. It comprises ~1128 Python modules, with ~142 in the core OS and ~81 in Lyrixa.

Core (Aetherra/aetherra_core) includes engine, kernel, memory, plugins, config. The primary memory engine (AetherraMemoryEngine) wraps the QuantumEnhancedMemoryEngine, providing compatibility while delegating persistence and recall to the canonical engine.

Lyrixa (assistant) spans intelligence, gui, plugins, memory, launcher and integrates with the OS through the registry and Hub. The chat service is workspace-aware and can suggest/apply safe fixes with deterministic fallbacks when offline.

Hub & Federation includes server, federation, node_assets. When Flask is present, the local Hub exposes health, stats, plugin registry, federation sync, and a Lyrixa chat bridge.

QFAC (Quantum Fractal Adaptive Compression) is present (integration, dashboard, analyzer). It is an optional extension that can be enabled via environment flags and verified via capability tests.

Metrics determinism update: Kernel and Orchestrator latency histograms now export zero-value buckets on first scrape to stabilize CI tests (`test_metrics_histograms_end_to_end`).

Endpoints summary (Hub Flask server):

- /
- /health
- /api/health
- /status
- /services
- /api/plugins
- /api/plugins/register
- /api/memory/narratives
- /memory/narratives
- /api/trainer/jobs
- /api/trainer/status
- /api/trainer/evals
- /api/trainer/evals/<eval_id>
Tests provide end-to-end validation (capabilities: 8) and unit coverage (unit: 18), including OS boot, registry collaboration, hub endpoints/federation, memory recall, QFAC-in-OS, and self-maintenance wiring.

Additional parity test added: `tests/integration/test_hub_compat_parity.py` (ensures deprecated shim emits warning & surface parity until removal).


- AETHERRA_PROFILE
- AETHERRA_DETERMINISTIC
- AETHERRA_TRACE
- AETHERRA_AUDIT

- AETHERRA_AUDIT_MIN_CONF
- AETHERRA_AUDIT_WINDOW_H
- AETHERRA_MEMORY_DIR
// Auxiliary and optional flags detected across the codebase
- AETHERRA_AVAILABLE
- AETHERRA_DISABLE_LEGACY_ALIASES
- AETHERRA_BOOT_MENU
- AETHERRA_ENGINES_AVAILABLE
- AETHERRA_ENGINE_AVAILABLE
- AETHERRA_FEDERATION_INTERVAL_SEC
- AETHERRA_GUI_ENABLED
- AETHERRA_HUB_ENABLED
- AETHERRA_IMPORT_UPDATE_REPORT
- AETHERRA_INTELLIGENCE_PROVIDER
- AETHERRA_INTERFACE_TYPE
- AETHERRA_LOG_LEVEL
- AETHERRA_LYRIXA_CLEANUP_REPORT
- AETHERRA_MAX_TOKENS
- AETHERRA_MEMORY_QUANTUM_ENABLED
- AETHERRA_AGENT_TIMEOUT_MS
- AETHERRA_MODEL
- AETHERRA_PLUGIN_SOFTLOAD
- AETHERRA_SAFE_MODE
- AETHERRA_SERVER_AVAILABLE
- AETHERRA_START_LOCAL_HUB
- AETHERRA_TELEMETRY_ENDPOINT
// Security & Policies
- AETHERRA_KEYS_ALLOW_UNSCOPED
- AETHERRA_KEYS_MASTER
- AETHERRA_PLUGIN_SIGNING_STRICT
- AETHERRA_REQUIRE_CAPABILITIES
- AETHERRA_HUB_CONTROL_ENABLED
- AETHERRA_HUB_CONTROL_TOKEN
// Plugin quotas
- AETHERRA_PLUGIN_MAX_MEM_MB
- AETHERRA_PLUGIN_MAX_RUNTIME_SEC
// Telemetry DP controls
- AETHERRA_TELEMETRY_DP
- AETHERRA_TELEMETRY_DP_EPS
// Kernel settings
- AETHERRA_KERNEL_HEARTBEAT_SEC
- AETHERRA_KERNEL_QSIZE_HIGH
- AETHERRA_KERNEL_QSIZE_NORMAL
- AETHERRA_KERNEL_QSIZE_BACKGROUND
- AETHERRA_KERNEL_PERSIST_TASKS
- AETHERRA_KERNEL_TASKS_PATH
- AETHERRA_KERNEL_TASK_DEFAULT_TTL_SEC
- AETHERRA_KERNEL_DLQ
- AETHERRA_KERNEL_DLQ_PATH
- AETHERRA_KERNEL_DLQ_MAX
- AETHERRA_NIGHT_START_HOUR
- AETHERRA_NIGHT_END_HOUR
- AETHERRA_KERNEL_RATE_LIMIT_PER_MIN
- AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC
- AETHERRA_USE_HYBRID
- AETHERRA_WEB_BASE
- AETHERRA_WEB_HOST
- AETHERRA_HMR_STRICT
- AETHERRA_HMR_ALLOWED_SOURCES
- AETHERRA_HMR_AUDIT_PATH
- AETHERRA_HMR_AUDIT_MAX_BYTES
- AETHERRA_HMR_AUDIT_MAX_BACKUPS
// Security hardening (Phase 0 additions)
- AETHERRA_AI_API_ENABLED
- AETHERRA_AI_API_STREAM
- AETHERRA_AI_API_REQUIRE_TOKEN
- AETHERRA_AI_API_TOKEN
- AETHERRA_NET_STRICT (auto-enabled default allowlist in prod if unset)
- AETHERRA_SCRIPT_VERIFY_STRICT
- AETHERRA_SIGNING_STRICT
- AETHERRA_PROD_UNSAFE_ALLOW (temporary override to bypass prod guard; do NOT use in real prod)
- AETHERRA_HMR_ENABLED
- AETHERRA_HMR_ALLOWED_SOURCES
- AETHERRA_HMR_STRICT
// CORS / PNA and registry warnings
- AETHERRA_PNA_ALLOW
- AETHERRA_REGISTRY_WARN_NO_HANDLER
- AETHERRA_REGISTRY_NO_HANDLER_SILENT
// Tokenizer configuration
- AETHERRA_TOKENIZER
- AETHERRA_TOKENIZER_MODEL
// Optional AI developer API (disabled by default)
- AETHERRA_AGENTS_API_REQUIRE_TOKEN
- AETHERRA_AGENTS_API_TOKEN
- AETHERRA_AGENTS_API_STREAM
- AETHERRA_AGENTS_STREAM_POLL_MS

- /api/plugins/<plugin_id>
- /api/stats
- /api/peers
- /api/peers/sync
- /api/peers/announce
- /api/telemetry
- /api/lyrixa/chat
- /api/memory/graph
- /api/memory/status
- /api/memory/audit
- /api/memory/narratives
- /memory/narratives
- /api/trainer/jobs
- /api/trainer/status
- /api/registry/status
- /api/kernel/metrics
- /api/kernel/status
- /api/klm/status
- /api/klm/metrics
- /api/keb/status
- /api/keb/metrics
- /api/kernel/control/pause
- /api/kernel/control/resume
- /api/kernel/control/drain
- /api/kernel/control/queue_limits
Note: Aggregated site status endpoint (preferred by UI/widget)
- /api/site_status
- /site_status
Note: Global OPTIONS preflight handler (CORS/PNA)
- `/&lt;param&gt;` (Flask-style catch‑all)


```text
/<param>
```

Note: Auxiliary endpoints that may be exposed by optional modules/dashboards

- /api/users
- `/api/users/<param>`
- /qfac/metrics
- /quantum/status
- /quantum/run
- /api/quantum/status
- /api/quantum/run
- /quantum_status

Note: Optional developer AI endpoints (disabled by default)

- /api/ai/ask
- /api/ai/stream
- /api/ai/stream_ws

### Metrics (Security & HMR Enhancements)

Prometheus metrics added in Phase 0 for improved observability:

| Metric                                          | Type    | Description                                                                          |
| ----------------------------------------------- | ------- | ------------------------------------------------------------------------------------ |
| aetherra_chat_auth_missing_token_total          | counter | Requests rejected due to missing required auth token (stream path disabled in prod)  |
| aetherra_chat_auth_invalid_token_total          | counter | Requests rejected due to provided but invalid token                                  |
| aetherra_hmr_denied_total                       | counter | Total HMR controller initializations or reload attempts denied                       |
| aetherra_hmr_denied_reasons_total{reason="..."} | counter | Breakdown of HMR denies by reason (e.g. requirements_not_met, init_failure)          |
| aetherra_kernel_plugin_invoke_timeout_sec       | gauge   | Effective (post-clamp) plugin invoke timeout in seconds (prod ceiling 120, warn >60) |
| aetherra_unsafe_override_present                | gauge   | 1 if any unsafe production override env var detected, else 0                         |
| aetherra_unsafe_override_info{override="..."}   | gauge   | One line per unsafe override present (value always 1)                                |

#### Operational notes

- Missing token metric only increments when API stream path is disabled due to configuration gap under a production profile.
- Invalid token metric increments when a token is required and a non-empty, incorrect token is supplied.
- HMR denial reasons surface misconfiguration or hardening gates preventing unsafe hot reload in production.
- /ws/ai/stream
- /api/openapi.json

#### Recommended Production Baseline (Security Hardening)

Set (minimum):

- `AETHERRA_PROFILE=prod`
- `AETHERRA_AI_API_ENABLED=1` only if AI developer endpoints required; otherwise leave unset
- `AETHERRA_AI_API_REQUIRE_TOKEN=1` and set `AETHERRA_AI_API_TOKEN` to strong random value (32+ chars)
- `AETHERRA_NET_STRICT=1` (or rely on auto-enable) and define `AETHERRA_NETWORK_ALLOWLIST` minimally (e.g. `localhost,127.0.0.1,.aetherra.dev`)
- `AETHERRA_HMR_STRICT=1` with explicit `AETHERRA_HMR_ALLOWED_SOURCES` (comma list of vetted paths/repos); omit entirely to disable HMR in prod
- `AETHERRA_SCRIPT_VERIFY_STRICT=1` and `AETHERRA_SIGNING_STRICT=1` to enforce script + plugin signature verification
- Kernel queue sizes explicitly sized if high throughput expected: `AETHERRA_KERNEL_QSIZE_HIGH`, `AETHERRA_KERNEL_QSIZE_NORMAL`, `AETHERRA_KERNEL_QSIZE_BACKGROUND` (avoid relying solely on defaults for capacity planning)

Avoid / Monitor:

- `AETHERRA_PROD_UNSAFE_ALLOW` (temporary escape hatch) — SHOULD NOT be set in real production. If present, raise immediate ops alert.
- `AETHERRA_ALLOW_UNBOUNDED=1` — only for debugging; allows unbounded queues / DLQ disable.

Audit Procedure (CI or runtime):

1. Scrape `/metrics` and ensure absence of `aetherra_chat_auth_missing_token_total > 0` (indicates misconfigured token requirement).
2. Query for unexpected increments:
   - `increase(aetherra_chat_auth_invalid_token_total[5m]) > 0` — possible probing.
   - `increase(aetherra_hmr_denied_total[10m]) > 0` — repeated HMR misconfig attempts.
3. Periodically verify exported `aetherra_kernel_plugin_invoke_timeout_sec` within accepted SLO window (e.g. <= 60s) — alerts on drift above 60.
4. Check for unsafe override gauges:

- `aetherra_unsafe_override_present == 1` — at least one override set (critical)
- `aetherra_unsafe_override_info` series enumerate each specific override (label `override`)

#### Prometheus Alert Examples

```yaml
groups:
  - name: aetherra-security
    rules:
      - alert: AetherraMissingTokenMisconfig
        expr: aetherra_chat_auth_missing_token_total > 0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Aetherra AI API missing token rejections detected"
          description: "Production profile is rejecting requests due to missing token; verify AETHERRA_AI_API_TOKEN / REQUIRE_TOKEN settings."
      - alert: AetherraInvalidTokenProbing
        expr: increase(aetherra_chat_auth_invalid_token_total[15m]) > 5
        for: 5m
        labels:
          severity: medium
        annotations:
          summary: "Elevated invalid token attempts"
          description: "More than 5 invalid token rejections in 15m window. Possible credential stuffing or probing."
      - alert: AetherraHMRTrouble
        expr: increase(aetherra_hmr_denied_total[30m]) > 0
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "HMR denies occurring"
          description: "Hot module reload denied in production. Inspect aetherra_hmr_denied_reasons_total for root cause."
      - alert: AetherraPluginTimeoutSLOExceeded
        expr: aetherra_kernel_plugin_invoke_timeout_sec > 60
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Plugin invoke timeout above 60s"
          description: "Effective plugin timeout exceeds recommended SLO (<=60s). Investigate long-running plugins or misconfiguration."
      - alert: AetherraUnsafeOverridePresent
        expr: aetherra_unsafe_override_present == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Unsafe production override detected"
          description: "One or more unsafe overrides enabled. Inspect aetherra_unsafe_override_info{override=...} and remove environment vars (AETHERRA_PROD_UNSAFE_ALLOW / AETHERRA_ALLOW_UNBOUNDED)."
```

Note: Unsafe override gauges are emitted only when at least one of the overrides is present; in normal production they will be absent or `aetherra_unsafe_override_present` = 0.
Note: Optional Agents endpoints (disabled by default)
- /api/agents
- /api/agents/metrics
- /api/tasks
- /api/tasks/<task_id>
- /api/tasks/<task_id>/stream
- /api/agents/evaluate
- /api/agents/evaluation

### HMR Safety Defaults and Metrics

In production (`AETHERRA_PROFILE=prod`):

- HMR only enables if `AETHERRA_HMR_STRICT=1` and `AETHERRA_HMR_ALLOWED_SOURCES` is non-empty.
- When unset, audit rotation uses safe defaults: `AETHERRA_HMR_AUDIT_MAX_BYTES=5242880` and `AETHERRA_HMR_AUDIT_MAX_BACKUPS=3`.
- The Hub exposes HMR configuration on:
  - Prometheus `/metrics` as `aetherra_hmr_enabled`, `aetherra_hmr_strict`, `aetherra_hmr_allowed_sources_count`, `aetherra_hmr_audit_max_bytes`, and `aetherra_hmr_audit_max_backups`.
  - JSON `/api/kernel/metrics` under the `hmr` key.

#### Services

None

#### Tests

Capabilities:

- tests/capabilities/test_aether_e2e.py
- tests/capabilities/test_agent_collaboration.py
- tests/capabilities/test_hub_telemetry_and_federation.py
- tests/capabilities/test_lyrixa_chat.py
- tests/capabilities/test_lyrixa_chat_endpoint.py
- tests/capabilities/test_memory_recall.py
- tests/capabilities/test_qfac_in_os.py
- tests/capabilities/test_self_maintenance_services.py

---

### Environment Variables — Quantum and A/B Recall

The following environment variables control quantum features, recall A/B experiments, and related Hub metric exports:

- `AETHERRA_AB_RECALL_MODE` — classical | quantum | abp (global A/B mode)
- `AETHERRA_AB_RECALL_PCT` — integer percent of traffic to quantum in abp mode
- `AETHERRA_AB_RECALL_SEED` — rollout seed for deterministic bucketing
- `AETHERRA_AB_FORCE_BUCKET` — classical | quantum (force bucket for testing)
- `AETHERRA_HUB_AB_METRICS` — 1/0 gate for exporting A/B series via Hub /metrics
// Legacy hub import enforcement (deprecation safety)
- `LEGACY_HUB_IMPORT_ENFORCE` — 1/0 (default 1) disable only for emergency to bypass quality gate blocking imports of deprecated hub script.
- `LEGACY_HUB_IMPORT_ALLOW` — 1/0 (default 0) local override to bypass pre-commit hook blocking deprecated hub imports.
- `AETHERRA_QHASH_BITS` — SimHash bits for quantum‑inspired hashing
- `AETHERRA_QHASH_WEIGHT` — weight of QHash in recall scoring blend
- `AETHERRA_RFM_IN` — input dimension for Random Feature Maps
- `AETHERRA_RFM_OUT` — output dimension for Random Feature Maps
- `AETHERRA_RFM_SEED` — seed for Random Feature Maps
- `AETHERRA_RFM_WEIGHT` — weight of random‑feature similarity in scoring
- `AETHERRA_QUANTUM_MODE` — simulator | provider (bridge mode)
- `AETHERRA_QUANTUM_PROVIDER` — provider name/id when in provider mode
- `AETHERRA_QUANTUM_MAX_SHOTS` — daily max shots budget
- `AETHERRA_QUANTUM_BUDGET_USD` — monthly cost budget in USD
- `AETHERRA_QUANTUM_CACHE_TTL_SEC` — cache TTL in seconds for quantum results
- `AETHERRA_QUANTUM_DETERMINISTIC` — 1/0 deterministic simulator behavior
- `AETHERRA_QUANTUM_RECALL` — enable quantum‑enriched recall path
- `AETHERRA_QUANTUM_AUDIT` — 1/0 include quantum audit records
- `AETHERRA_RELEASE_PRIVKEY` — Optional Ed25519 private key (hex) used by signing helpers (e.g., future release manifest signature). If unset, signing is skipped.

### Environment Variables — Observer-Aware Policy (Q4)

These flags control the orchestrator’s observer-aware safety gates, coherence thresholds, and drift alerts exposed via the Hub metrics exporter (if enabled).

- `AETHERRA_OBSERVER_AWARE_ENABLED` — 1/0 to enable policy gating (default: 1)
- `AETHERRA_COHERENCE_GATE_MIN` — soft gate min coherence score (default: 0.65)
- `AETHERRA_COHERENCE_HARD_MIN` — hard deny min coherence score (default: 0.40)
- `AETHERRA_DRIFT_ALERT_MIN` — min delta to emit a drift alert (default: 0.50)
- `AETHERRA_SENSITIVE_ACTIONS` — CSV list of sensitive action ids that always require human approval
- `AETHERRA_COHERENCE_EST` — optional override (0..1) for engine’s coherence estimator (testing)

### Prometheus: quick queries

- Latest coherence EMA
  - aetherra_orchestrator_coherence_ema
- Alerts when drift was seen in the last 10 minutes
  - max_over_time(aetherra_orchestrator_last_drift_alert_present[10m])
- Deny/hold counters (rate)
  - rate(aetherra_orchestrator_observer_denied_total[5m])
  - rate(aetherra_orchestrator_observer_pending_human_total[5m])

### Q4: Observer-aware policy and coherence telemetry

The orchestrator enforces observer-aware gating based on task sensitivity and engine-estimated coherence, and exports gauges and counters via the Hub metrics exporter (if enabled).

Environment flags:

- `AETHERRA_OBSERVER_AWARE_ENABLED` — 1/0 master switch for policy gating (default 1).
- `AETHERRA_COHERENCE_GATE_MIN` — soft gate minimum coherence; below this, sensitive tasks require human approval (default 0.65).
- `AETHERRA_COHERENCE_HARD_MIN` — hard block threshold; tasks below this are denied (default 0.40).
- `AETHERRA_DRIFT_ALERT_MIN` — minimum absolute delta in EMA coherence to trigger a drift alert (default 0.50).
- `AETHERRA_SENSITIVE_ACTIONS` — comma-separated keywords for sensitive actions (e.g., "delete,apply,deploy").
- `AETHERRA_COHERENCE_EST` — optional override for engine coherence estimator (float 0..1) for testing.

Exported metrics (when the metrics exporter is enabled):

- Gauges:
  - `aetherra_orchestrator_coherence_gate_min`
  - `aetherra_orchestrator_coherence_hard_min`
  - `aetherra_orchestrator_coherence_ema`
  - `aetherra_orchestrator_coherence_window_size`
  - `aetherra_orchestrator_last_drift_alert_present` (1 if present)
- Counters (under `aetherra_orchestrator_…`):
  - `observer_gates_triggered_total`
  - `observer_pending_human_total`
  - `observer_denied_total`
  - `drift_alerts_total`

PromQL examples:

```promql
# Any drift in the last 5 minutes
increase(aetherra_orchestrator_drift_alerts_total[5m]) > 0

# Pending human approvals trending up
rate(aetherra_orchestrator_observer_pending_human_total[10m]) > 0

# EMA currently below soft gate
aetherra_orchestrator_coherence_ema < aetherra_orchestrator_coherence_gate_min
```

---

## Human Style Layer (Chat UX)

A small, deterministic style layer shapes assistant responses to feel more human while remaining safe and testable.

Environment variables:

- `AETHERRA_STYLE_ENABLED` — 1/0 to enable the layer (default 1)
- `AETHERRA_STYLE_PERSONA` — persona label (default "Lyrixa")
- `AETHERRA_STYLE_TONE` — friendly | enthusiastic | concise (default friendly)
- `AETHERRA_STYLE_ASK_QUESTION` — 1/0 to optionally append a follow-up question (default 1)
- `AETHERRA_STYLE_EMOJI` — 1/0 to allow one safe emoji (default 0)
- `AETHERRA_STYLE_MAX_LEN` — integer max characters to clamp output (default 0 disabled)
- `AETHERRA_STYLE_SEED` — integer seed for deterministic choices (default 13)

Prometheus metrics (if metrics exporter is enabled):

- `aetherra_style_contractions_total`
- `aetherra_style_questions_total`
- `aetherra_style_empathy_total`

PromQL examples:

```promql
rate(aetherra_style_questions_total[5m])
sum by () (aetherra_style_empathy_total)
```

---

## Environment Variables — Chat and Base URLs (Aug 31, 2025)

The chat system and demos recognize these common variables:

- `AETHERRA_BASE_URL` — Base URL for Hub/API when clients are external to the process
- `AETHERRA_CHAT_MAX_TOKENS` — Default output token cap for chat completions
- `AETHERRA_CHAT_SAFETY_MODE` — Safety preset: strict | standard (affects policy gates)
- `AETHERRA_CHAT_TEMPERATURE` — Default sampling temperature for chat
- `AETHERRA_DEMO` — 1/0 to enable demo paths/features in UIs and tools
- `AETHERRA_LLM_MODEL` — Preferred default LLM model identifier
// Chat transport, versioning, and idempotency
- `AETHERRA_AI_API_WS` — 1/0 to enable WebSocket transport endpoints; when enabled, clients can use ws://.../ws/ai/stream
- `AETHERRA_CHAT_VERSION_REQUIRED` — If set to `2`, require header `X-Aetherra-Chat-Version: 2` on chat endpoints (reject otherwise)
- `AETHERRA_IDEMPOTENCY_ENFORCE` — 1/0 to enforce idempotent handling using `client_message_id` with TTL cache
- `AETHERRA_IDEMPOTENCY_TTL_SEC` — TTL seconds for idempotency cache entries (duplicates within this window are rejected)

Safety and policy tuning for chat (also surfaced in the Hub policy snapshot/header and SSE policy event):

- `AETHERRA_CHAT_CAPS_STANDARD` — Optional CSV override for capability grants when safety mode is standard
- `AETHERRA_CHAT_CAPS_STRICT` — Optional CSV override for capability grants when safety mode is strict
- `AETHERRA_NETWORK_ALLOWLIST` — CSV list of allowed hosts/wildcards for URL usage in prompts (e.g., `localhost,127.0.0.1,*.aetherra.dev`)
- `AETHERRA_DP_ENABLED` — 1/0 to surface Differential Privacy flags in policy snapshot
- `AETHERRA_DP_EPSILON` — Epsilon value used when DP is enabled (informational; surfaced in policy)
- `AETHERRA_SECURITY_LEDGER` — 1/0 to enable best‑effort JSONL security ledger writes on high‑risk intercepts
- `AETHERRA_SECURITY_LEDGER_PATH` — File path for the security ledger (default: `${AETHERRA_STATE_DIR}/security_ledger.jsonl`)
- `AETHERRA_RETRY_AFTER_SEC` — Default seconds for HTTP 429 Retry‑After on rate limiting (overridable per deployment)

These augment the existing variables listed above and are surfaced by the Docs Consistency tool.

---

## Environment Variables Index

This index lists environment variables detected in the codebase. Values are read with sane defaults; set only those you need.

Core toggles and networking:

- `AETHERRA_AGENTS_API_ENABLED`
- `AETHERRA_AUDIT_PATH` — File path for general audit logs produced by tools/services (distinct from HMR audit path).
- `AETHERRA_AI_API_ENABLED`
- `AETHERRA_AI_API_REQUIRE_TOKEN`
- `AETHERRA_AI_API_STREAM`
- `AETHERRA_AI_API_TOKEN`
- `AETHERRA_DEBUG` — 1/0 master debug toggle; increases log verbosity across subsystems.
- `AETHERRA_ALLOW_UNTRUSTED_SECRET`
- `AETHERRA_AGENT_PER_METRICS`
- `AETHERRA_ENABLE_QFAC`
- `AETHERRA_FEDERATION_STATE`
- `AETHERRA_MODE` — Deployment mode hint (dev|test|prod); some scripts use this in addition to AETHERRA_PROFILE.
- `AETHERRA_HMR_ENABLED`
- `AETHERRA_HUB_BASE`
- `AETHERRA_HUB_HOST`
- `AETHERRA_HUB_PORT`
- `AETHERRA_HUB_STRICT`
- `AETHERRA_HUB_WS_PORT`
- `AETHERRA_NET_STRICT`
- `AETHERRA_POLICY_HOME` — Override directory for security policy files (capabilities.json, net_policy.json); default: `~/.aetherra/policy`. Useful for CI/tests or sharing policy across instances.
- `AETHERRA_OS_MODE`
- `AETHERRA_PEERS`
- `AETHERRA_QFAC_IN_OS`
- `AETHERRA_QFAC_MODE`
- `AETHERRA_QUIET`
- `AETHERRA_REQUIRE_STRICT`
- `AETHERRA_SCRIPT_VERIFY_STRICT`
- `AETHERRA_SIGNING_STRICT`
- `AETHERRA_SIGN_PLUGINS`
- `AETHERRA_STATE_DIR`
- `AETHERRA_STRICT`
- `AETHERRA_STRICT_SPDX` — Set to `1` to enable strict SPDX header verification (scans tests/frontend and optional dirs). Default lenient mode when unset.
- `AETHERRA_TELEMETRY`
- `AETHERRA_TEMPLATE_DIR`
- `AETHERRA_WEB_PORT`

- `AETHERRA_KEYS_ALLOW_PLAINTEXT` — 1/0 to allow storing API keys in plaintext (development only; encryption at rest recommended).
- `AETHERRA_PRINCIPAL` — Caller identity propagated to services for policy and audit (e.g., user/session id).
- `AETHERRA_QFAC_POLICY` — enforce | shadow | off (policy mode for quantum path gating).
- `AETHERRA_QFAC_BACKEND` — simulator | qiskit | ionq | aws_braket | azure | custom.
- `AETHERRA_QFAC_GATE_MIN` — float soft gate threshold (e.g., 0.85).
- `AETHERRA_QFAC_HARD_MIN` — float hard deny threshold (e.g., 0.75).
- `AETHERRA_QFAC_WINDOW_SIZE` — int window size used for reporting.
- `AETHERRA_QFAC_COHERENCE_EMA` — float EMA coherence (optional runtime signal).
- `AETHERRA_QFAC_DRIFT_COOLDOWN_SEC` — int seconds cooldown between drift alerts.
- `AETHERRA_QFAC_LAST_DRIFT_ALERT_EPOCH` — float epoch seconds of last drift alert.
- `AETHERRA_QFAC_VALIDATED` — 1/0 declares validated quantum path present.

Launcher and bootstrap controls:

- `AETHERRA_SKIP_DOTENV` — 1/0 to skip loading .env at startup (useful in CI or hermetic envs)
- `AETHERRA_SKIP_LAUNCHER_AI_DEFAULTS` — 1/0 to disable launcher’s default AI flags; rely strictly on explicit env/config
- `AETHERRA_HUB_SKIP_OPTIONALS` — 1/0 to skip optional subsystems on Hub start (e.g., federation dashboards)
- `AETHERRA_TEST_ENFORCE_DISABLED_UNTIL_SET` — 1/0 to force AI developer APIs disabled unless tokens/flags explicitly set (test hardening)

Kernel scheduling, retry, and metrics:

- `AETHERRA_KERNEL_AGING_SEC`
- `AETHERRA_KERNEL_METRICS_FLUSH_SEC`
- `AETHERRA_KERNEL_RETRY_BASE_DELAY_MS`
- `AETHERRA_KERNEL_RETRY_MAX`
- `AETHERRA_REGISTRY_NO_HANDLER_RATE_SEC`
- `AETHERRA_SIE_TELEMETRY_INTERVAL`

- `AETHERRA_ALLOW_UNBOUNDED` — 1/0 override to allow unbounded queues or DLQ disabled in prod (safety bypass; not recommended).
- `AETHERRA_NIGHT_TZ` — IANA time zone for night cycle window (e.g., "UTC", "America/Los_Angeles").
- `AETHERRA_NIGHT_UTC` — 1/0 to pin night cycle scheduling to UTC.
- `AETHERRA_NIGHT_STAGGER_MAX_SEC` — Max jitter seconds to stagger start within the window.
  - Night cycle safety: In prod/staging the Kernel emits `aetherra_kernel_night_schedule_guard_pass=0` if neither `AETHERRA_NIGHT_TZ` nor `AETHERRA_NIGHT_UTC=1` is set (fail‑closed). Set one explicitly to pass the guard.

Plugins runtime:

- `AETHERRA_PLUGIN_CB_COOLDOWN_SEC`
- `AETHERRA_PLUGIN_CB_THRESHOLD`
- `AETHERRA_PLUGIN_DISABLE`
- `AETHERRA_PLUGIN_INTERACTIVE`
- `AETHERRA_PLUGIN_MAX_CONCURRENCY`
- `AETHERRA_PLUGIN_CAP_CONCURRENCY_MAP` — JSON map capability→concurrency cap; lower cap overrides global per‑plugin cap.
- `AETHERRA_TRAINER_ENABLED`

Chat and client defaults:

- `AETHERRA_BASE_URL`
- `AETHERRA_CHAT_DEBUG` — 1/0 to emit verbose chat pipeline diagnostics (routing, policy, providers).
- `AETHERRA_CHAT_MAX_TOKENS`
- `AETHERRA_CHAT_SAFETY_MODE`
- `AETHERRA_CHAT_TEMPERATURE`
- `AETHERRA_DEMO`
- `AETHERRA_LLM_MODEL`
// Chat transport, versioning, and idempotency
- `AETHERRA_AI_API_WS`
- `AETHERRA_CHAT_VERSION_REQUIRED`
- `AETHERRA_IDEMPOTENCY_ENFORCE`
- `AETHERRA_IDEMPOTENCY_TTL_SEC`
// Chat safety & policy extensions
- `AETHERRA_CHAT_CAPS_STANDARD`
- `AETHERRA_CHAT_CAPS_STRICT`
- `AETHERRA_NETWORK_ALLOWLIST`
- `AETHERRA_DP_ENABLED`
- `AETHERRA_DP_EPSILON`
- `AETHERRA_SECURITY_LEDGER`
- `AETHERRA_SECURITY_LEDGER_PATH`
- `AETHERRA_RETRY_AFTER_SEC`
- `AETHERRA_LYRIXA_FORCE_OFFLINE` — 1/0 to force Lyrixa to operate offline (no external AI API calls; use deterministic fallbacks).

- `AETHERRA_SSE_REPLAY_MAX_AGE_S` — Max age in seconds for SSE replay buffer entries.
- `AETHERRA_SSE_REPLAY_MAX_EVENTS` — Max number of SSE replay events retained.
- `AETHERRA_STREAM_SOFT_TIMEOUT_S` — Soft timeout for streaming sessions before graceful finalization.
- `AETHERRA_ENGINE_WAIT_MS` — Milliseconds to wait for engine registration at Hub start.
  - Scratchpad redaction default: If `scratchpad_policy` is omitted on `/api/ai/stream` or `/api/ai/ask`, Hub defaults to `redacted`. `persisted` requires capability `evidence.view`; `ephemeral` always allowed.
- `AETHERRA_TEST_RESET_ENGINE` — 1/0 to reset/unregister engine at Hub start during tests.
- `AETHERRA_HUB_RESET_ENGINE_ON_START` — 1/0 to force engine reset on Hub start.
- `AETHERRA_HUB_DEBUG_METRICS` — 1/0 to enable extra Hub metrics debug logging for troubleshooting.
// Enforcement (deprecated hub)
- `LEGACY_HUB_IMPORT_ENFORCE`
- `LEGACY_HUB_IMPORT_ALLOW`

Developer tooling (format/lint):

- `AETHERRA_FORMAT_LINT` — 1/0 to run code formatter as part of lint tasks.
- `AETHERRA_LINT_FIX` — 1/0 to enable auto-fix for supported linters where safe.
- `AETHERRA_LINT_FLAKE8` — 1/0 to include flake8 checks in lint runs.
- `AETHERRA_LINT_MYPY` — 1/0 to include mypy type checks in lint runs.

Transcendence metrics and baselines:

- `AETHERRA_TRANSCENDENCE_BASELINE` — Float baseline used by transcendence/consciousness metrics adapters (e.g., 0.700).

---

## Endpoints (canonical)

Primary Hub endpoints added/updated in this release (canonical list; see full inventory above for all routes):

- /api/memory/narratives
- /memory/narratives
- /api/trainer/jobs
- /api/trainer/jobs/<job_id>
- /api/trainer/status
- /api/trainer/evals
- /api/trainer/evals/<eval_id>

These are served by the local Hub when Flask is available. Some routes may be gated by feature flags or environment variables noted earlier.
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
