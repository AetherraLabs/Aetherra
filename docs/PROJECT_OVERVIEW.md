# Aetherra Project Overview

This document provides a comprehensive overview of the Aetherra AI Operating System: core subsystems, services, modules, configuration, and how to validate end-to-end.

## Scope and Structure

Primary source tree: `Aetherra/`

- aetherra_core/ — OS core (engine, kernel, memory, plugins, config)
- lyrixa/ — Lyrixa assistant (intelligence, GUI, plugins, integrations)
- plugins/ — Ecosystem plugins (std + lyrixa)

See also: the comprehensive Memory System guide: [Memory System](docs/memory_system.md).
Stats enhancements:

- The /api/stats payload includes a lyrixa_chat object with best-effort availability:
  - { registered: bool, status?: "healthy"|"degraded"|..., registered_at?, last_heartbeat? }
  - If registry is not available, registered will be false.

---

## Auto-Generated Overview (analyze_project.py) — 2025-08-24 16:17:08

Generated at: 2025-08-24 16:17:08

### Repository Analysis Summary

This repository contains the Aetherra AI Operating System and Lyrixa assistant. It comprises ~1128 Python modules, with ~142 in the core OS and ~81 in Lyrixa.

Core (Aetherra/aetherra_core) includes engine, kernel, memory, plugins, config. The primary memory engine (AetherraMemoryEngine) wraps the QuantumEnhancedMemoryEngine, providing compatibility while delegating persistence and recall to the canonical engine.

Lyrixa (assistant) spans intelligence, gui, plugins, memory, launcher and integrates with the OS through the registry and Hub. The chat service is workspace-aware and can suggest/apply safe fixes with deterministic fallbacks when offline.

Hub & Federation includes server, federation, node_assets. When Flask is present, the local Hub exposes health, stats, plugin registry, federation sync, and a Lyrixa chat bridge.

QFAC (Quantum Fractal Adaptive Compression) is present (integration, dashboard, analyzer). It is an optional extension that can be enabled via environment flags and verified via capability tests.

Endpoints summary (Hub Flask server):

- /
- /health
Tests provide end-to-end validation (capabilities: 8) and unit coverage (unit: 18), including OS boot, registry collaboration, hub endpoints/federation, memory recall, QFAC-in-OS, and self-maintenance wiring.


- AETHERRA_PROFILE
- AETHERRA_DETERMINISTIC
- AETHERRA_TRACE
- AETHERRA_AUDIT

- AETHERRA_AUDIT_PATH
- AETHERRA_TEMPLATE_DIR
- AETHERRA_REQUIRE_STRICT
- AETHERRA_STRICT
- AETHERRA_ALLOW_UNTRUSTED_SECRET
- AETHERRA_SCRIPT_VERIFY_STRICT
- AETHERRA_SIGNING_STRICT
- AETHERRA_HUB_STRICT
- AETHERRA_SIGN_PLUGINS
- AETHERRA_TELEMETRY
- AETHERRA_HUB_HOST
- AETHERRA_HUB_PORT
- AETHERRA_HUB_WS_PORT
- AETHERRA_PEERS
- AETHERRA_QFAC_MODE
- AETHERRA_QFAC_IN_OS
- AETHERRA_STATE_DIR
- AETHERRA_HOME
- AETHERRA_QUIET
- AETHERRA_OFFLINE
// Auxiliary and optional flags detected across the codebase
- AETHERRA_AVAILABLE
- AETHERRA_DISABLE_LEGACY_ALIASES
- AETHERRA_BOOT_MENU
- AETHERRA_CORE
- AETHERRA_CORE_ANALYSIS
- AETHERRA_CORE_CLEANUP_REPORT
- AETHERRA_DEBUG
- AETHERRA_ENABLE_QFAC
- AETHERRA_ENGINES
- AETHERRA_ENGINES_AVAILABLE
- AETHERRA_ENGINE_AVAILABLE
- AETHERRA_FEDERATION_INTERVAL_SEC
- AETHERRA_FEDERATION_STATE
- AETHERRA_GUI_ENABLED
- AETHERRA_HUB_BASE
- AETHERRA_HUB_ENABLED
- AETHERRA_HUB_URL
- AETHERRA_IMPORT_UPDATE_REPORT
- AETHERRA_INTELLIGENCE_PROVIDER
- AETHERRA_INTERFACE_TYPE
- AETHERRA_LOG_LEVEL
- AETHERRA_LYRIXA_CLEANUP_REPORT
- AETHERRA_MAX_TOKENS
- AETHERRA_MEMORY_QUANTUM_ENABLED
- AETHERRA_AGENT_TIMEOUT_MS
- AETHERRA_MODEL
- AETHERRA_NLP_AVAILABLE
- AETHERRA_OS_MODE
- AETHERRA_PLUGINS_CLEANUP_REPORT
- AETHERRA_PLUGINS_ENABLED
- AETHERRA_PLUGIN_DISABLE
- AETHERRA_PLUGIN_INTERACTIVE
- AETHERRA_PLUGIN_SOFTLOAD
- AETHERRA_SAFE_MODE
- AETHERRA_SERVER_AVAILABLE
- AETHERRA_SIE_TELEMETRY_INTERVAL
- AETHERRA_START_LOCAL_HUB
- AETHERRA_TELEMETRY_ENDPOINT
// Security & Policies
- AETHERRA_KEYS_ALLOW_UNSCOPED
- AETHERRA_KEYS_MASTER
- AETHERRA_NET_STRICT
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
- AETHERRA_KERNEL_METRICS_FLUSH_SEC
- AETHERRA_KERNEL_DLQ
- AETHERRA_KERNEL_DLQ_PATH
- AETHERRA_KERNEL_DLQ_MAX
- AETHERRA_NIGHT_START_HOUR
- AETHERRA_NIGHT_END_HOUR
- AETHERRA_KERNEL_RATE_LIMIT_PER_MIN
- AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC
- AETHERRA_PLUGIN_CB_THRESHOLD
- AETHERRA_PLUGIN_CB_COOLDOWN_SEC
- AETHERRA_PLUGIN_MAX_CONCURRENCY
- AETHERRA_KERNEL_RETRY_MAX
- AETHERRA_KERNEL_RETRY_BASE_DELAY_MS
- AETHERRA_KERNEL_AGING_SEC
- AETHERRA_TEMPERATURE
- AETHERRA_USE_HYBRID
- AETHERRA_WEB_BASE
- AETHERRA_WEB_HOST
- AETHERRA_WEB_PORT
// Hot Module Reloading (HMR)
- AETHERRA_HMR_ENABLED
- AETHERRA_HMR_STRICT
- AETHERRA_HMR_ALLOWED_SOURCES
- AETHERRA_HMR_AUDIT_PATH
- AETHERRA_HMR_AUDIT_MAX_BYTES
- AETHERRA_HMR_AUDIT_MAX_BACKUPS
// CORS / PNA and registry warnings
- AETHERRA_PNA_ALLOW
- AETHERRA_REGISTRY_WARN_NO_HANDLER
- AETHERRA_REGISTRY_NO_HANDLER_RATE_SEC
- AETHERRA_REGISTRY_NO_HANDLER_SILENT
// Tokenizer configuration
- AETHERRA_TOKENIZER
- AETHERRA_TOKENIZER_MODEL
// Optional AI developer API (disabled by default)
- AETHERRA_AI_API_ENABLED
- AETHERRA_AI_API_REQUIRE_TOKEN
- AETHERRA_AI_API_TOKEN
- AETHERRA_AI_API_STREAM
// Optional Agents API (disabled by default)
- AETHERRA_AGENTS_API_ENABLED
- AETHERRA_AGENTS_API_REQUIRE_TOKEN
- AETHERRA_AGENTS_API_TOKEN
- AETHERRA_AGENTS_API_STREAM
- AETHERRA_AGENTS_STREAM_POLL_MS

#### Endpoints

- `/`
- /health
- /api/health
- /status
- /services
- /api/plugins
- /api/plugins/register
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
// Aggregated site status endpoint (preferred by UI/widget)
- /api/site_status
- /site_status
// Global OPTIONS preflight handler (CORS/PNA)
- `/&lt;param&gt;` (Flask-style catch‑all)


```text
/<param>
```

// Auxiliary endpoints that may be exposed by optional modules/dashboards

- /api/users
- `/api/users/<param>`
- /qfac/metrics
- /quantum/status
- /quantum_status
- /metrics
// Optional developer AI API (disabled by default)
- /api/ai/ask
- /api/ai/stream
// Optional Agents API (disabled by default)
- /api/agents
- /api/agents/metrics
- /api/tasks
- /api/tasks/<task_id>
- /api/tasks/<task_id>/stream
- /api/agents/evaluate
- /api/agents/evaluation

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
