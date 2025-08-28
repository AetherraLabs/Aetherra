# Aetherra Kernel System

Updated: 2025-08-27

This document describes the Aetherra Kernel: the core runtime loop, service registry, and launcher phases that bring the AI OS online and keep it healthy. It mirrors the structure of other system docs and is grounded in the current codebase and tasks.

## Purpose and scope

- Coordinate core systems (memory, plugins, engine, scheduler) via a central kernel loop
- Provide heartbeats, health monitoring, maintenance cycles, and night cycles
- Register and message services through the Service Registry
- Orchestrate boot/shutdown via the OS Launcher in well-defined phases

## At‑a‑glance status

- Kernel loop: Implemented (priority queues, concurrent loops, metrics)
- Heartbeats: Implemented (per-service and kernel via registry)
- Health monitoring: Implemented (periodic metrics and checks)
- Maintenance: Implemented (background tasks, memory optimization)
- Night cycle: Implemented (configurable window; default 2–4 AM)
- Plugin orchestration: Implemented (scheduled tasks adapter)
- Metrics persistence: Implemented (aetherra_kernel_metrics.json)
- Metrics HTTP: New (Hub exposes /api/kernel/metrics and /metrics)
- OS status file: Implemented (temp file for cross-process detection)
- Deterministic smoke boot: Implemented (test profile)
- Optional task durability: New (best‑effort snapshot to kernel_tasks.json)
- Health broadcast: New (kernel.health events via registry)
- Backpressure: New (optional bounded queues with drop counters)
- Traceability and safety: New (trace_id on tasks, optional TTL/deadlines)
- Timeouts and resilience: New (plugin invoke timeouts + simple circuit breaker)
- Timeouts and resilience: New (plugin invoke timeouts + simple circuit breaker)
- Concurrency and retries: New (per-plugin concurrency caps, jittered retries)

## Core components

### 1) Kernel loop

File: `aetherra_kernel_loop.py`

Class: `AetherraKernelLoop`

- Injected systems: memory_system, plugin_manager, aetherra_engine, scheduler, service_registry
- Priority queues: `high_priority_queue`, `normal_priority_queue`, `background_queue`
- Concurrent loops (async tasks):
  - Heartbeat: sends `update_heartbeat("kernel_loop")` every 60s
  - Main processing: drains queues (high → normal → background), updates metrics, adaptive sleep
  - Background maintenance: periodic health check, memory optimization, plugin health
  - Health monitoring: gathers health metrics; warns on critical issues; broadcasts `kernel.health`
  - Memory optimization: light periodic core memory tune-up
  - Plugin orchestration: executes scheduled plugin tasks
- Night cycle: between 02:00–04:00 local once per day; runs deep consolidation, plugin optimization, reflection, cleanup
- Metrics: rolling averages and counters; persisted on shutdown to `aetherra_kernel_metrics.json`
- Tasks accepted by `_execute_task` today:
  - `memory_query`: forwards to memory_system
  - `plugin_invoke`: forwards to plugin_manager with safety (capability check, rate limit, timeout, circuit breaker)
  - `aetherra_thought`: forwards content to aetherra_engine
- Public API:
  - `inject_systems(...)`
  - `start_kernel_loop()` / `shutdown()`
  - `add_task(task: dict, priority: str = "normal")` (bounded when limits set; tracks pending for snapshot)
  - `get_status() -> dict` (running, uptime, cycle_count, metrics, queue sizes/limits)
  - Snapshot helpers (internal): `_snapshot_tasks()` and `_load_persisted_tasks()`
  - Each task receives a `trace_id` automatically; optional `deadline_ts` and `timeout_sec` are honored

### 2) Service Registry

File: `aetherra_service_registry.py`

Class: `AetherraServiceRegistry`

- Registers services with metadata and dependencies
- Tracks `ServiceStatus` (STARTING, HEALTHY, DEGRADED, FAILED, STOPPING)
- Heartbeats: `update_heartbeat(name)` and monitor marking stale services as DEGRADED
- Messaging:
  - Direct: `send_message(target_service, message_type, data)`
  - Broadcast: `broadcast_message(message_type, data, exclude=None)`
- Event model: subscribe/unsubscribe to registry events; internal `_broadcast_event`
- Global helpers: `get_service_registry()`, `register_service(...)`, `get_service(...)`, `update_heartbeat(...)`, `shutdown_service_registry()`
- Status snapshot: `get_registry_status()` returns counts per status and service timestamps

### 3) OS Launcher (phased boot)

File: `aetherra_os_launcher.py`

Class: `AetherraOSLauncher`

- Logging mode: quiet/log-level via env; safe Unicode logging on Windows
- Phases:
  1. Initialize Service Registry
  2. Load core systems (memory, plugins, Aetherra engine, Aether Script service, persistent memory, adaptive behavior, consciousness engines, scheduler, hub/marketplace, self-maintenance, Lyrixa chat, GUI hooks)
  3. Start Kernel Loop (inject systems, register kernel)
  4. Activate systems (set HEALTHY in registry where applicable)
  5. Validate system health
  6. Announce OS online (log summary and enqueue first thought)
  7. Main operation loop (status file write, periodic checks)
- Shutdown:
  - Graceful: stop kernel, registry, self-improvement telemetry loop, then system adapters
  - Emergency: best-effort `emergency_stop` on services if available
- Adapters (bridge real implementations to kernel contracts):
  - `MemoryAdapter`, `PluginManagerAdapter`, `EngineAdapter`, `LyrixaChatAdapter`
- Hub integration: starts built-in hub server when enabled and runs plugin discovery
- Deterministic telemetry loop for Self-Improvement Engine (best-effort)
  - Gated by telemetry opt‑in; emits minimal status to Hub `/api/telemetry`

## Small contract summary

- Kernel task contract (input):
  - `{ "type": "memory_query"|"plugin_invoke"|"aetherra_thought", "data": {...} }`
- Kernel status contract (output):
  - `{ running: bool, uptime: float, cycle_count: int, metrics: dict, queue_sizes: {high_priority:int, normal_priority:int, background:int} }`
- Registry message contract:
  - `send_message(service, message_type: str, data: any)` where services implement `handle_message(message_type, data)` or `on_message(...)`

## Configuration and environment

- General
  - `AETHERRA_QUIET=1` (reduced logs during smoke)
  - `AETHERRA_LOG_LEVEL=INFO|WARNING|...`
  - `AETHERRA_PROFILE=test` (deterministic profile used by smoke)
- Launcher config keys
  - `gui_enabled: bool` (often False in headless)
  - `hub_enabled: bool` (Hub server on/off)
- Self-improvement telemetry
  - `AETHERRA_SIE_TELEMETRY_INTERVAL` (seconds between posts)
- Kernel backpressure and durability
  - `AETHERRA_KERNEL_QSIZE_HIGH|NORMAL|BACKGROUND` (ints; 0=unbounded)
  - `AETHERRA_KERNEL_PERSIST_TASKS=1` to enable best‑effort snapshots
  - `AETHERRA_KERNEL_TASKS_PATH` to override snapshot path (default `.aetherra/kernel_tasks.json`)
  - `AETHERRA_KERNEL_TASK_DEFAULT_TTL_SEC` to auto-apply task expiration deadlines
  - `AETHERRA_KERNEL_METRICS_FLUSH_SEC` to periodically flush metrics for live dashboards
  - DLQ (dead letter queue) for dropped/expired tasks:
    - `AETHERRA_KERNEL_DLQ=1` enable
    - `AETHERRA_KERNEL_DLQ_PATH` (default `.aetherra/kernel_dlq.jsonl`)
    - `AETHERRA_KERNEL_DLQ_MAX` (default 10000 records)
- Night cycle window
  - `AETHERRA_NIGHT_START_HOUR` / `AETHERRA_NIGHT_END_HOUR` (ints 0..23)
- Optional rate limiting and capability enforcement
  - `AETHERRA_KERNEL_RATE_LIMIT_PER_MIN` (int per requester for plugin_invoke)
  - `AETHERRA_REQUIRE_CAPABILITIES=1` enables capability check `kernel:invoke_plugin`
- Plugin invocation safety
  - `AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC` (default 30) per call timeout
  - `AETHERRA_PLUGIN_CB_THRESHOLD` (failures before opening circuit; default 5)
  - `AETHERRA_PLUGIN_CB_COOLDOWN_SEC` (cooldown after opening; default 60)
- Concurrency caps and retries
  - `AETHERRA_PLUGIN_MAX_CONCURRENCY` (int; per-plugin running call cap; 0=unlimited)
  - `AETHERRA_KERNEL_RETRY_MAX` (int; max retries for plugin_invoke on timeout/error)
  - `AETHERRA_KERNEL_RETRY_BASE_DELAY_MS` (base backoff in ms; default 200; exponential with jitter)

Defaults and timing

- Heartbeats: every 60s
- Health monitor: every 30s
- Background maintenance tick: every 60s (with 5/30/60 min cadence for checks)
- Memory optimization loop: every 10 minutes
- Plugin orchestration loop: every 2 minutes
- Night cycle window: configurable (default 02:00–04:00), once per day

## Observability and tasks

- Metrics file: `aetherra_kernel_metrics.json` (written on shutdown)
- Metrics API: via Hub
  - `GET /api/kernel/metrics` → `{ hub_ts, kernel: get_status() }`
  - `GET /metrics` → Prometheus-format counters/gauges (kernel + registry)
- OS status file: OS writes `aetherra_os_status.json` to system temp dir with liveness info
- Service registry: `get_registry_status()` counts and timestamps; per-service status available
- Events: kernel broadcasts `kernel.health` with enriched payload via the Service Registry for subscribers (queue sizes/limits, circuit breaker state, DLQ count, last flush time)
  - Health payload is enriched with concurrency/retry-related metrics (e.g., plugin CB state; retry counters visible in kernel metrics)
- Logs: `aetherra_os.log` (Unicode-safe formatter) and console

VS Code tasks (Terminal → Run Task):

- Verify Aetherra OS (Headless Smoke)
  - Boots quietly without GUI and asserts core services register
- Verify UI Standards (optional UI static checks)
- Aether Verify (Quick/Strict) and Spec → Tests Gate (complementary quality gates)

PowerShell examples (optional):

```powershell
# Headless smoke boot (task equivalent)
python tools/os_smoke.py

# Check quick aether/static gates
python tools/verify_aether_scripts.py --profile test
```

## Health and fault tolerance

- All long-running loops guard exceptions and continue with backoff
- Heartbeat monitor marks stale services as DEGRADED after 5 minutes without heartbeat
- Launcher main loop monitors kernel/registry liveness and initiates shutdown on critical failure
- Graceful shutdown persists kernel metrics and tears down services

## Extension points

- Adding work to the kernel:
  - Use `kernel.add_task({...}, priority="high|normal|background")`
  - Provide handlers in injected systems (`process_query`, `invoke_plugin`, `process_message`)
- Service-to-service messaging:
  - Register with the registry and implement `handle_message`
  - Use `send_message`/`broadcast_message` for cross-component events
- Adapting new systems:
  - Follow the lightweight adapter examples in `aetherra_os_launcher.py` to meet kernel contracts without invasive changes
- Security integration:
  - With `AETHERRA_REQUIRE_CAPABILITIES=1`, kernel enforces `kernel:invoke_plugin` for plugin_invoke tasks to prevent bypassing the security layer
  - Optional simple per-requester rate limiting via `AETHERRA_KERNEL_RATE_LIMIT_PER_MIN`

## Known limitations and roadmap

- No durable task queue persistence across restarts (tasks in memory)
- Scheduling is minimal; complex cron-like semantics should live in the scheduler module
- Backpressure and rate limiting are basic; consider bounded queues and load-shedding policies
  - Concurrency capping and retry logic are conservative; future: per-plugin policies and failure classification
- Night cycle timing is fixed; future: config-driven windows and multi-phase maintenance
- Health metrics are coarse; future: expose Prometheus-style endpoints or richer telemetry

## References (code and tasks)

- Kernel loop: `aetherra_kernel_loop.py`
- OS launcher: `aetherra_os_launcher.py`
- Service registry: `aetherra_service_registry.py`
- Headless smoke test: `tools/os_smoke.py`
- Logs: `aetherra_os.log`; metrics: `aetherra_kernel_metrics.json`

See also:

- Aetherra Security System: `docs/AETHERRA_SECURITY_SYSTEM.md`
- Aetherra Memory System: `docs/AETHERRA_MEMORY_SYSTEM.md`
- Aetherra Coding System: `docs/AETHERRA_CODING_SYSTEM.md`
