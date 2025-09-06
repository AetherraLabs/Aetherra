# Aetherra — Project Status and Architecture Map (2025-08-11)

This document summarizes what the project is, how it’s organized, what’s working today, and what to do next.

## Summary at a Glance

- Core vision: AI-native OS where Lyrixa is the cognitive interface and .aether encodes intent (see Aetherra_Lyrixa_Description.md and Aether Script Language Specification.md).
- Status: Phase 6 UI and intelligence are implemented; service registry, kernel loop, plugin hub, and mock fallbacks exist; quantum/consciousness scaffolding is wired.
- Launchers: aetherra_os_launcher.py (full OS orchestration), aetherra_os.py (entry with GUI routing), Aetherra/lyrixa/launcher.py (Lyrixa backend orchestrator), Aetherra/lyrixa/lyrixa_basic.py (main Lyrixa GUI entry).
- UI: PySide6 + embedded web panels; Phase 3–6 features present (auto-generation, cognitive UI, plugin UI, personality/state memory).
- Memory: Persistent and “quantum” bridges are present; real engine is pluggable with mocks when unavailable.
- Plugins + Hub: Discovery, hub server, and plugin UI wiring exist; marketplace/hub integration present (with graceful fallback).
- Risks: Mixed packaging/licensing in pyproject files, some import path drift, mocks indicate areas needing real implementations; documentation is ahead of some code.

---

## Architecture Overview

- Orchestrator (OS):
  - aetherra_os_launcher.py — async master launcher orchestrating registry, memory, plugins, scheduler, engine, .aether interpreter, hub, GUI, and consciousness. Includes robust mock fallbacks to keep the OS bootable.
  - aetherra_os.py — user-facing entry; starts backend in a thread and launches designated GUI (hybrid or web).
  - aetherra_kernel_loop.py — kernel loop integration (injected systems, task scheduling).
  - aetherra_service_registry.py — service discovery/health with heartbeats (ServiceStatus).

- Lyrixa (Cognitive Interface):
  - Aetherra/lyrixa/launcher.py — unified Lyrixa OS launcher (starts backend services, connects to Hub, wires conversation manager, quantum bridge, plugin UI, and GUI).
  - Aetherra/lyrixa/gui/main_window.py — PySide6 hybrid window embedding web panels; implements:
    - Phase 2 Live Context Bridge (LyrixaContextBridge)
    - Phase 3 Auto-Generation (Phase3AutoGenerator)
    - Phase 4 Cognitive UI (CognitiveStateMonitor)
    - Phase 5 Plugin UI Manager (PluginUIManager)
    - Phase 6 Personality/State Memory (GUIPersonalityManager)
    - Consciousness panel (native + web fallback).

- Memory + Intelligence:
  - aetherra_persistent_memory.py, Aetherra/lyrixa/memory/, quantum_memory_bridge.py — persistent store and quantum bridge scaffolding.
  - Lyrixa conversation/intelligence managers are referenced from Aetherra.aetherra_core modules (wired in GUI and launcher; gracefully skipped if missing).

- Plugins + Hub:
  - aetherra_plugin_discovery.py, aetherra_hub_server.py, aetherra_plugin_catalog.json — discovery, hub, and catalog.
  - In launchers: plugin manager is loaded and hub integration attempted; when hub is down, the system continues via mock services.

- Consciousness Layer:
  - Aetherra/lyrixa/consciousness_integration.py — ConsciousnessBridge for cross-system messaging/state; syncs and emits events; designed to coordinate Aetherra Core and Lyrixa Core consciousness metadata.
  - aetherra_os_launcher.py wires Phase 7/8 consciousness engines if available, otherwise mocks.

- Web UI (embedded + separate):
  - Aetherra/lyrixa/gui/ — Vite/React web panels packaged for embedding; Tailwind config and assets present; additional Aetherra/gui/web server referenced by aetherra_os.py.

- Tests + Tooling:
  - tests/ directory contains smoke/integration tests.
  - pyproject.toml (root) has an extensive pytest/coverage config.
  - requirements.txt consolidates runtime deps; GUI requires PySide6 (optional) and web stack for Vite UI.

---

## Launch & Operations

- Preferred OS launcher: python aetherra_os_launcher.py (or use aetherra_os.py to launch with GUI routing).
- Lyrixa-only entry: python Aetherra/lyrixa/lyrixa_basic.py (GUI by default; use --cli for CLI mode). The legacy launcher at Aetherra/lyrixa/launcher.py remains for backend wiring.
- GUI: PySide6 app with embedded web panels; if PySide6 is missing, Lyrixa launcher offers CLI mode.
- Hub: Built-in server on port 3001 when enabled; plugin discovery auto-syncs to hub.
- Health: Service registry tracks service states; periodic heartbeats; kernel loop status metrics.

---

## What’s Working Today

- End-to-end boot with graceful degradation:
  - Service registry, kernel loop injection, and async lifecycle.
  - Memory system, plugin manager, native engine, scheduler, and .aether interpreter are attempted; if import fails, robust mocks keep system running.
- Lyrixa UI Phases 3–6:
  - Auto-generated panels from system state; cognitive state visualization; plugin-driven UI; personality and state memory; chat panel wiring.
- Hub + Plugins:
  - Discovery + hub sync paths; plugin UI loader events; marketplace operations proxied when hub is online.
- Consciousness wiring:
  - Consciousness bridge and quantum/cosmic/transcendence stubs integrated; CLI status surfaces metrics when available.

---

## Gaps and Risks (Technical Debt)

- Packaging and licensing:
  - Root LICENSE is GPL-3.0, while Aetherra/pyproject.toml lists MIT; also lists builtin modules (sqlite3, pathlib) as dependencies. Consolidate to a single policy (GPL-3.0) and fix deps.
- Import path consistency:
  - Mixed namespaces (Aetherra., aetherra_core., lyrixa_core.) and some legacy paths; launchers include multiple fallbacks. Standardize import map and add runtime checks.
- Real vs mock implementations:
  - Many systems boot via mocks if imports fail (memory, plugins, engines, consciousness). Identify which real modules are authoritative and complete missing pieces.
- UI duplication:
  - Embedded panels vs separate web server references; ensure a single source-of-truth for panels and a stable DX to build/serve them.
- Docs vs code drift:
  - README claims “Production Ready, Phase 6 Complete + Discord bot,” while AETHERRA_RELEASE_STATUS.md targets Phase 6.2. Also, the Discord bot is internal-only and excluded from public releases—ensure docs make this clear and exclude it from packaging.

---

## .aether Language — Current State vs Spec

- Spec is defined (Aether Script Language Specification.md) with goals, memory, assignments, calls, conditionals, loops, workflow blocks, and built-ins.
- Runtime:
  - aetherra_os_launcher.py wires aetherra_script_service via get_aether_script_service() if available; mocks otherwise.
  - Next lift: implement/verify parser + executor to fully match the published EBNF and built-ins; add tests for workflows, conditionals, and memory ops.

---

## Next Steps (Actionable Roadmap)

Short (1–2 weeks)

- Package hygiene: unify licensing (GPL-3.0), fix Aetherra/pyproject deps, ensure PySide6 is optional but discoverable; align requirements/lock files.
- Import map: add docs/import_map.md (if missing) and a small validator to flag non-canonical imports in CI.
- .aether MVP completeness: verify aetherra_script_service implementation; add parser/executor tests for the EBNF sections (goal, memory, assignment, call, conditional, loop, workflow).
- GUI stability: add a minimal “GUI smoke test” that imports LyrixaBasicWindow from Aetherra/lyrixa/lyrixa_basic_gui.py and instantiates it offscreen (CI compatible). The hybrid window remains supported but is not the primary entry.

Medium (3–6 weeks)

- Personality–Consciousness bridge (Phase 6.2): implement state coupling between CognitiveStateMonitor and GUIPersonalityManager; expose metrics and UX responses.
- Plugin lifecycle: round out activate/deactivate/reload paths in LyrixaContextBridge and reconcile with plugin manager APIs.
- Hub hardening: health checks + retry/backoff + offline sync queue; richer plugin metadata and signed manifests.
- Memory: converge on a concrete default memory engine; add health, metrics, and a persistent schema migration story.

Longer (6–12 weeks)

- Distributed/hub federation: multi-node discovery, signed plugin bundles, and shared memory graph optics.
- Security posture: key management (docs/api-keys.md), sandboxing, and static risk analysis for .aether workflows.
- Telemetry opt-in: anonymized ops metrics with privacy guardrails.

---

## Federation, Signing, Telemetry — Current Status and Quickstart (2025-08-12)

Status

- Federation: Hub exposes peers endpoint and federated catalog; peers can be pre-seeded via environment. Memory graph optics available at GET /api/memory/graph.
- Signing: Discovery can sign plugin manifests; Hub can enforce signature verification on registration.
- Telemetry: Opt-in emitter available; Hub ingests at POST /api/telemetry and tracks counters in /api/stats (telemetry_received, last_telemetry_at).

Quickstart

- Environment flags (also mirrored in docs/api-keys.md):
  - AETHERRA_SIGN_PLUGINS=1 — sign manifests in discovery when a secret is set via API keys (plugin_signing_secret).
  - AETHERRA_SIGNING_STRICT=1 — Hub requires valid signatures on /api/plugins/register.
  - AETHERRA_PEERS=<http://host1:3001>,<http://host2:3001> — seed federation peers at Hub startup.

Examples

- PowerShell (Windows):

```powershell
[System.Environment]::SetEnvironmentVariable("AETHERRA_SIGN_PLUGINS", "1", "User")
[System.Environment]::SetEnvironmentVariable("AETHERRA_SIGNING_STRICT", "1", "User")
[System.Environment]::SetEnvironmentVariable("AETHERRA_PEERS", "http://localhost:3002,http://localhost:3003", "User")
```

- Bash:

```bash
export AETHERRA_SIGN_PLUGINS=1
export AETHERRA_SIGNING_STRICT=1
export AETHERRA_PEERS=http://localhost:3002,http://localhost:3003
```

Notes

- To generate and store a signing secret, use `from Aetherra.security.api_keys import set_key; set_key("plugin_signing_secret", "<base64-secret>")`.
- When strict mode is on, unsigned or invalidly signed manifests are rejected (HTTP 400).
- Memory graph optics returns sample nodes/edges and counts for UI and observability.

## Validation Targets (What to Prove Next)

- Boot matrix: full OS boot on Windows/macOS/Linux with and without GUI; mocks acceptable but measured.
- .aether conformance: unit tests for each grammar construct and built-in; end-to-end workflow demo.
- UI regression: deterministic screenshot tests of key panels; “Verify UI Standards” tool passing.
- Plugin discovery/hub: scan, sync, and UI render path validated in CI.

---

## Directory Pointers (Where Things Live)

- OS + Orchestration: aetherra_os_launcher.py, aetherra_os.py, aetherra_kernel_loop.py, aetherra_service_registry.py
- Lyrixa Frontend: Aetherra/lyrixa/lyrixa_basic.py (main GUI), Aetherra/lyrixa/lyrixa_basic_gui.py (window), Aetherra/lyrixa/launcher.py (backend orchestrator), Aetherra/lyrixa/gui/* (hybrid PySide6 + web panels)
- Consciousness Bridge: Aetherra/lyrixa/consciousness_integration.py
- Memory: aetherra_persistent_memory.py, Aetherra/lyrixa/memory/*, quantum_memory_bridge.py
- Plugins/Hub: aetherra_plugin_discovery.py, aetherra_hub_server.py, Aetherra/lyrixa/plugins/*
- Tests: tests/*, root pyproject.toml pytest config
- Docs: README.md (top-level), Aetherra/README.md, Aetherra/lyrixa/README.md, AETHERRA_RELEASE_STATUS.md

---

## Appendix — Current Release Signals

- AETHERRA_RELEASE_STATUS.md indicates Phase 6.1 complete and readiness for 6.2.
- Top-level README markets Phase 6 and Discord Bot integration; mark the bot as internal-only and ensure “Discord Bot/” is excluded from public distributions.

---

Updated: 2025-08-11

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
