# Aetherra Project Overview

This document provides a comprehensive overview of the Aetherra AI Operating System: core subsystems, services, modules, configuration, and how to validate end-to-end.

## Scope and Structure

Primary source tree: `Aetherra/`

- aetherra_core/ — OS core (engine, kernel, memory, plugins, config)
- lyrixa/ — Lyrixa assistant (intelligence, GUI, plugins, integrations)
- plugins/ — Ecosystem plugins (std + lyrixa)
- hub/ and aetherra_hub/ — Federation and external hub assets
- api/, runtime/, security/, telemetry/, tools/ — supporting systems

Other top-level entrypoints/services:

- `aetherra_os_launcher.py` — Main OS launcher (services + lifecycle)
- `aetherra_service_registry.py` — In-process registry (health, events)
- `aetherra_shared_service_registry.py` — Cross-process shared registry
- `aetherra_hub_server.py` — Local hub server (REST, telemetry; port 3011)

## Core Subsystems (aetherra_core)

- Kernel and Engine
  - engine/, kernel/, system/: lifecycle, scheduling, orchestration
  - events/, reflection/, reflection_engine/: system reflection/analysis
- Memory
  - memory/: FractalMesh and engines
    - `aetherra_memory_engine.py`, `memory_core.py`, `memory_kernel.py`
    - Fractal components: `fractal_encoder.py`, `fractal_hierarchies.py`, `fractal_mesh/`, replay/reflector
    - Quantum: `QuantumEnhancedMemoryEngine/`, `quantum_memory_engine.py`, `quantum_memory_bridge.py`, dashboards
    - QFAC: `qfac_integration.py`, `qfac_dashboard.py`, `qfac_launcher.py`, `compression_metrics.py`
  - file_system/: `compression_analyzer.py` (QFAC analyzer)
- Plugins
  - plugins/: `plugin_manager.py`, `plugin_manager_core.py`, `plugin_registry.py`, bridges and chain executor
- Configuration and System
  - config/, system/, orchestration/, ai/, cognitive/, personality/

## Lyrixa (assistant)

- Intelligence & Integration
  - intelligence/, intelligence_integration.py, consciousness_integration.py
- User Interface
  - gui/ (multi-phase UI), analytics dashboards
- Plugins and Memory
  - plugins/, memory/, reflection_engine/
- Launcher
  - `Aetherra/lyrixa/launcher.py`

## Services and Registries

- Local Registry (in-process): `aetherra_service_registry.py`
  - API: register_service, get_service, get_service_info, list_services, status/events
- Shared Registry (cross-process): `aetherra_shared_service_registry.py`
  - Persistent services.json with IPC port; supports health/status and discovery

## OS Lifecycle

Entrypoint: `aetherra_os_launcher.py`

- Boot: initialize registry, load core memory, plugins, engine, kernel loop
- Register services: `memory_system`, `plugin_manager`, `aetherra_engine`, `kernel_loop`, self-maintenance services
- Optional QFAC: register `qfac_memory_system` when `AETHERRA_QFAC_IN_OS=1`
- Health: services with no deps set HEALTHY on registration; heartbeat monitor runs

## Memory Systems

- AetherraMemoryEngine (primary)
  - Adapter over QuantumEnhancedMemoryEngine; compatibility paths for recall
- FractalMesh stack
  - Fractal encoder/hierarchies, episodic/semantic/associative layers
- QFAC (Quantum Fractal Adaptive Compression) [optional extension]
  - Analyzer: `Aetherra/aetherra_core/file_system/compression_analyzer.py`
  - Core: `qfac_integration.py` (nodes/system; auto-compression; status/report)
  - Metrics: `compression_metrics.py` (FidelityLevel, ratios)
  - Quantum bridge: `quantum_memory_bridge.py` (hardware or simulator)
  - Dashboard: `qfac_dashboard.py` (stub fallback via safe import)
  - CLI/Demo: `qfac_launcher.py` (demo, system-status, analyze, benchmark)
  - Modes: classical | hybrid | quantum (`AETHERRA_QFAC_MODE`)

## Plugins and Ecosystem

- Core plugin management via `plugin_manager.py` and `plugin_manager_core.py`
- Discovery utilities and catalog at root (e.g., `aetherra_plugin_discovery.py`)
- Stdlib plugins load at OS boot (sysmon, optimizer, selfrepair, whisper, executor)

## Hub, Federation, and Telemetry

- Local Hub Server: `aetherra_hub_server.py` (Flask/WSGI; default port 3011)
- Federation modules: `Aetherra/hub/federation.py`
- Node/JS Hub assets: `Aetherra/aetherra_hub/aetherra_hub/*` (server.js, client)

## Self-Maintenance

- Self-Improvement Engine: metrics capture, trends, optional telemetry
- Self-Repair: detection, suggestions, automated fixes (plugin)

## Configuration and Environment

- Logging and quiet mode: `AETHERRA_QUIET=1`, `AETHERRA_LOG_LEVEL=INFO|WARNING|DEBUG`
- QFAC: `AETHERRA_QFAC_MODE=classical|hybrid|quantum`
- QFAC in OS: `AETHERRA_QFAC_IN_OS=1`
- Telemetry interval: `AETHERRA_SIE_TELEMETRY_INTERVAL`
- Hub: default [http://localhost:3011](http://localhost:3011)

## Validation and Tests

- OS Smoke: `tools/os_smoke.py` (Task: Verify Aetherra OS (Headless Smoke))
- Capabilities: `tests/capabilities` (Task: Verify Claims (Capabilities Tests))
  - Includes `test_qfac_in_os.py` to verify optional QFAC registration and basic ops
- Unit: `tests/unit/test_qfac_modes.py` (classical/hybrid/quantum mode behavior and report)

## Quick Commands (PowerShell)

- Launch OS: `python aetherra_os_launcher.py`
- Launch with QFAC: `$env:AETHERRA_QFAC_IN_OS='1'; python aetherra_os_launcher.py`
- Run QFAC unit tests: `pytest -q tests/unit/test_qfac_modes.py`
- Run capabilities: `pytest -q -o addopts= tests/capabilities`

## Troubleshooting

- Missing quantum libraries: use `AETHERRA_QFAC_MODE=hybrid` or `classical` (simulated bridge)
- Dashboard import errors: automatic stub ensures headless runs don’t fail
- Imports: prefer canonical `Aetherra.*` and `aetherra_core.*`/`lyrixa.*` paths

## At-a-Glance Directory Map

```text
Aetherra/
├─ aetherra_core/
│  ├─ engine/, kernel/, system/, events/, reflection/
│  ├─ memory/ (fractal, QE, QFAC, dashboards, bridges)
│  ├─ file_system/ (compression_analyzer)
│  └─ plugins/ (manager, registry, bridges)
├─ lyrixa/ (intelligence, gui, plugins, integrations)
├─ hub/ (federation)
├─ aetherra_hub/aetherra_hub (node hub assets)
├─ plugins/ (ecosystem)
└─ telemetry/, security/, api/, runtime/, tools/
```

## References

- README.md (features, quick start, roadmap)
- docs/QFAC_MODE_GUIDE.md (modes, env, OS wiring, tests)
- aetherra_os_launcher.py (service wiring and optional QFAC registration)

## Expanded Directory and Components Map

Top level (selected, non-exhaustive with purpose):

- aetherra_os_launcher.py — Main orchestrator; registers services, optional QFAC
- aetherra_os.py — Headless OS entry (legacy-compatible)
- aetherra_hub_server.py — Local Hub HTTP API (health, stats, peers, memory graph)
- aetherra_service_registry.py — In-process registry and events bus
- aetherra_shared_service_registry.py — Cross-process, file-backed registry
- aetherra_script_service.py — Aether Script integration (routing, verification)
- aetherra_persistent_memory.py — Lightweight file/db-backed persistence
- tools/ — Smoke checks, inspectors, verifiers (see below)
- tests/ — Capabilities and unit suites
- docs/ — Guides and project status documentation
- Aetherra/ — Core source tree (OS core, Lyrixa, hub, plugins, telemetry, etc.)

Core tree highlights:

- Aetherra/aetherra_core/engine/ — aetherra_engine, lyrixa_engine, self_improvement_engine
- Aetherra/aetherra_core/kernel/ — pulse, reflector, web_bridge, quantum_bridge
- Aetherra/aetherra_core/system/ — .aether configs, bootstrap flows, logger, security system
- Aetherra/aetherra_core/plugins/ — plugin_manager, registry, chain executor, memory bridge
- Aetherra/aetherra_core/file_system/ — compression_analyzer (QFAC analyzer)
- Aetherra/aetherra_core/memory/ — primary+advanced memory engines and QFAC
  - aetherra_memory_engine.py, memory_core.py, memory_kernel.py
  - Fractal stack: fractal_encoder.py, fractal_hierarchies.py, fractal_mesh/*
  - Quantum: quantum_memory_engine.py, quantum_memory_bridge.py, quantum_dashboard/*
  - QFAC: qfac_integration.py, qfac_dashboard.py, qfac_launcher.py, compression_metrics.py
  - Observability: narrator/, pulse/, reflector/
- Aetherra/hub/ — federation manager and peer sync
- Aetherra/telemetry/optin.py — opt-in telemetry helper
- Aetherra/security/ — plugin/script signing, sandbox
- Aetherra/api/ — REST server and models for external control
- Aetherra/lyrixa/ — Lyrixa assistant (launcher, GUI, plugins, integrations)

Utilities and tools:

- tools/os_smoke.py — Headless OS smoke validation
- tools/engine_* — Analyzer, audit, usage matrix and probe
- tools/validate_* — Import map, engine imports, Aether Script verifier
- tools/verify_ui_standards.py — UI lint checker for Lyrixa UI
- demos/ — Demo flows for advanced memory systems

Optional UI/Web:

- aetherra_os_web/server.py — Web monitor that can show Aetherra status and handle messages

## Service and Endpoint Summary

Service Registry (in-process):

- register_service(name, instance, metadata, dependencies)
- get_service(name), get_service_info(name), list_services(status_filter)
- update_service_status(name, ServiceStatus), update_heartbeat(name)
- broadcast_message(message_type, data), send_message(target, message_type, data)

Hub Server HTTP endpoints (when Flask is available):

- GET /health — health and uptime
- GET /status — status and capabilities
- GET /services — service list for OS compatibility
- GET / — simple hub index page
- GET /api/plugins — list plugins
- GET /api/plugins/<plugin_id> — plugin details
- POST /api/plugins/register — register plugin (supports optional signature verification)
- GET /api/stats — hub stats (+federation counts if enabled)
- GET/POST /api/peers — list/add peers
- POST /api/peers/sync — trigger federation sync
- POST /api/peers/announce — gossip announce
- POST /api/telemetry — ingest opt-in telemetry
- GET /api/memory/graph — summarized memory graph (if optics available)

QFAC Dashboard endpoints:

- GET /qfac/metrics — returns phase metrics (from qfac_state_tracker)
- In-process API: QFACDashboard.start_dashboard/stop_dashboard/get_dashboard_summary

Other optional endpoints (when auxiliary servers are enabled):

- GET /api/health — basic API health (aux web services)
- GET/POST /api/users — example user API (aux web services)
- GET /api/users/<user_id> — user detail (aux web services)
- GET /quantum_status, GET /quantum/status — quantum dashboard probes (if quantum web dashboard enabled)

## Environment Variables Index

Common and logging:

- AETHERRA_QUIET — reduce logging noise during CI or smoke runs
- AETHERRA_LOG_LEVEL — adjust log verbosity (e.g., INFO, DEBUG)

QFAC and memory:

- AETHERRA_QFAC_MODE — classical | hybrid | quantum
- AETHERRA_QFAC_IN_OS — enable QFAC registration in OS
- AETHERRA_ENABLE_QFAC — alias for enabling QFAC
- AETHERRA_SIE_TELEMETRY_INTERVAL — self-improvement telemetry interval (seconds)

Script and plugins:

- AETHERRA_SCRIPT_VERIFY_STRICT — stricter script verification in script service
- AETHERRA_SIGN_PLUGINS — sign discovered plugins when creating catalog
- AETHERRA_SIGNING_STRICT — enforce signature verification on hub plugin register

Hub and federation:

- AETHERRA_PEERS — comma-separated list of hub peer URLs to seed federation

Other flags exist in submodules; prefer reading module docstrings for module-specific options.

Advanced/other environment variables referenced in code (optional, module-specific):

- AETHERRA_AVAILABLE, AETHERRA_ENGINE_AVAILABLE, AETHERRA_ENGINES_AVAILABLE — feature presence toggles
- AETHERRA_BOOT_MENU — enable boot menu flows
- AETHERRA_CORE, AETHERRA_CORE_ANALYSIS — core selection/analysis toggles
- AETHERRA_CORE_CLEANUP_REPORT, AETHERRA_IMPORT_UPDATE_REPORT, AETHERRA_LYRIXA_CLEANUP_REPORT, AETHERRA_PLUGINS_CLEANUP_REPORT — report filenames
- AETHERRA_DEBUG, AETHERRA_SAFE_MODE — debug/safe modes
- AETHERRA_ENGINES — engine selection
- AETHERRA_FEDERATION_INTERVAL_SEC, AETHERRA_FEDERATION_STATE — federation timing/state
- AETHERRA_GUI_ENABLED — enable GUI paths
- AETHERRA_HOME, AETHERRA_STATE_DIR — base directories for state
- AETHERRA_HUB_BASE, AETHERRA_HUB_ENABLED, AETHERRA_HUB_HOST, AETHERRA_HUB_PORT, AETHERRA_HUB_WS_PORT, AETHERRA_HUB_URL, AETHERRA_START_LOCAL_HUB — hub configuration
- AETHERRA_INTELLIGENCE_PROVIDER, AETHERRA_MODEL, AETHERRA_MAX_TOKENS, AETHERRA_TEMPERATURE — model/provider tuning
- AETHERRA_INTERFACE_TYPE — interface selection
- AETHERRA_MEMORY_QUANTUM_ENABLED, AETHERRA_USE_HYBRID — memory/quantum feature toggles
- AETHERRA_NLP_AVAILABLE — NLP feature presence
- AETHERRA_OS_MODE — runtime mode
- AETHERRA_PLUGINS_ENABLED, AETHERRA_PLUGIN_DISABLE, AETHERRA_PLUGIN_INTERACTIVE, AETHERRA_PLUGIN_SOFTLOAD — plugin controls
- AETHERRA_SERVER_AVAILABLE — server presence toggle
- AETHERRA_TELEMETRY, AETHERRA_TELEMETRY_ENDPOINT — telemetry enable/endpoint
- AETHERRA_WEB_BASE, AETHERRA_WEB_HOST, AETHERRA_WEB_PORT — web host config

## Tests Coverage Map

Capabilities (end-to-end claims):

- tests/capabilities/test_aether_e2e.py — end-to-end boot and run
- tests/capabilities/test_agent_collaboration.py — registry-based agent messaging
- tests/capabilities/test_hub_telemetry_and_federation.py — hub endpoints and federation
- tests/capabilities/test_memory_recall.py — core memory recall paths
- tests/capabilities/test_qfac_in_os.py — QFAC registered in OS, metadata, dashboard
- tests/capabilities/test_self_maintenance_services.py — self-improvement/repair wiring

Unit (selected):

- tests/unit/test_qfac_modes.py — classical/hybrid behavior, fallback, report export
- tests/unit/test_memory_kernel.py — kernel memory operations
- tests/unit/test_federation_* — federation manager and persistence
- tests/unit/test_hub_* — hub signing and non-strict/strict flows
- tests/unit/test_telemetry_optin.py — telemetry capture paths
- tests/unit/test_gui_smoke.py — GUI smoke tests
- tests/unit/test_imports.py — import integrity
- tests/unit/test_unicode_fix.py — Unicode handling correctness
- Additional: quantum-aware simulations, self-evolving behavior, live AI fallback

Test tasks available in this workspace:

- Verify Aetherra OS (Headless Smoke) — runs tools/os_smoke.py
- Verify Claims (Capabilities Tests) — runs tests/capabilities suite
- Verify UI Standards — runs UI standards verifier for Lyrixa UI

## How to Validate

- Prefer running the provided tasks for consistent validation across environments.
- For QFAC: set AETHERRA_QFAC_IN_OS=1 and AETHERRA_QFAC_MODE as desired, then run capability tests to verify registration, mode, and dashboard summary.
- Ensure hub endpoints respond when Flask is installed; otherwise, code uses a safe mock path for boot.

## Notes

- QFAC remains an optional extension; primary memory engine is AetherraMemoryEngine, with graceful degradation when quantum libraries are unavailable.
- The Hub server, federation, telemetry, and signing are designed to be present when optional dependencies are installed; tests include non-strict paths to keep CI green.
