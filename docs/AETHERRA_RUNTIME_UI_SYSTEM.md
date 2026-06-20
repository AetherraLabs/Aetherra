# Aetherra Runtime UI System

Updated: 2026-06-20

## Purpose

The Runtime UI is Aetherra's operator-facing Cognitive Observatory. It should
make the living system visible without turning Aetherra into a desktop clone,
chatbot window, or generic admin dashboard.

The UI's first responsibility is observation:

- Show what Aetherra is.
- Show what Aetherra is doing.
- Show which systems are healthy, active, degraded, or contained.
- Show Guardian, Security, Homeostasis, Maintenance, Aether Script, Memory,
  Agent, Consciousness, Self-Improvement, and Self-Incorporation activity.
- Avoid direct dangerous controls until Guardian and Security mediated control
  paths are ready.

## Status

Functional foundation complete.

Current foundation:

- `Aetherra/runtime_ui/observatory.py`
- `Aetherra/runtime_ui/scene.py`
- `aetherra_hub/blueprints/runtime_ui.py`
- `Aetherra/lyrixa/gui/src/App.tsx`
- `Aetherra/lyrixa/gui/src/index.css`
- `tests/unit/test_runtime_ui_observatory.py`
- `tests/unit/test_runtime_ui_scene.py`
- `tests/unit/test_runtime_ui_snapshot.py`
- `tests/unit/test_runtime_ui_contract.py`
- `tests/unit/test_runtime_ui_manifest.py`
- `tests/unit/test_runtime_ui_payload.py`
- `tests/unit/test_runtime_ui_query.py`
- `tests/unit/test_runtime_ui_api.py`

The API foundation is renderer-agnostic, and the first visual alpha shell now
renders that contract through the existing Vite/React/Three build path. The
served app is a read-only Cognitive Observatory shell, not the legacy Lyrixa
dashboard.

Visual alpha shell:

- Uses the Runtime UI bootstrap contract as its primary data source.
- Renders a full-screen living architecture map with 3D subsystem nodes and
  active relationships.
- Falls back to a bounded local snapshot when the Hub API is unavailable during
  static artifact inspection.
- Shows Guardian, Security, Homeostasis, Memory, subsystem status, activity,
  authority, and recent events.
- Exposes no mutation controls and keeps `controls_enabled: false` as the
  expected foundation posture.

## Design Direction: Cognitive Observatory

The first launch should feel like entering an active system:

- Black space, not emptiness.
- Subtle drifting particles and living connections.
- `AETHERRA` as the central presence.
- A concise status report:
  - Guardian active
  - Security active
  - Homeostasis active
  - Memory stable
- No desktop, taskbar, clutter, or legacy app shell.

The core view is a living architecture map. Subsystems are observable nodes, not
flat cards:

- Security
- Guardian
- Homeostasis
- Memory
- Consciousness
- Agents
- Self-Improvement
- Self-Incorporation
- Maintenance
- Aether Script
- Kernel
- Integration Validation

Connections brighten when active, dim when idle, and reflect degraded or
contained state when safety systems intervene.

## Lyrixa's Role

Lyrixa is not the primary UI and not a separate application. In the Runtime UI,
Lyrixa becomes a contextual guide:

- Explains the subsystem currently being viewed.
- Gives curator-style context.
- Helps the user understand what they are seeing.
- Does not become a chatbot-first interface.
- Does not bypass Guardian, Security, or Self-Incorporation controls.

## Initial Views

### Observatory Overview

The main living architecture map. It shows system status, subsystem activity,
connections, and recent events.

### Guardian View

Shows intent declarations, risk assessment, allow/deny/approval/containment
decisions, and audit references.

### Homeostasis View

Shows health, pressure, diagnosis, pending actions, recovery state, and
verification outcomes.

### Maintenance View

Shows observe -> diagnose -> propose -> review -> enforce -> execute -> verify
-> learn cycles.

### Aether Script View

Shows validation, signature status, static risk, execution gate results, and
workflow state.

### Memory View

Eventually becomes a navigable memory landscape. Initial foundation should show
health, narrative threads, memory pressure, and safe summary metadata only.

### Self-Improvement View

Shows observation, hypothesis, simulation, and proposal streams. It must not
apply changes directly.

### Self-Incorporation View

Shows discovery, classification, dry-run plan, approval state, staged execution,
rollback token status, and verification result.

### Consciousness View

Shows perception, attention, appraisal, deliberation, action, and reflection
state where the runtime exposes real reasoning or trace data.

### Architect Mode

Shows services, capabilities, events, agents, queues, Memory systems, Guardian
decisions, Maintenance cycles, Kernel activity, and validation state.

## Authority Rules

The Runtime UI does not own system authority.

| Action Type | Rule |
| --- | --- |
| Observe status | Allowed by default |
| Inspect audit/event records | Read-only; redact sensitive values |
| Request approval | Guardian mediated |
| Execute maintenance action | Guardian + Security + Self-Incorporation mediated |
| Apply self-improvement | Never direct; proposal -> Guardian -> approved execution |
| Modify memory or code | Never direct from UI foundation |

## Legacy UI Policy

Existing UI files are legacy evidence, not the new product direction.

- Old PySide, Lyrixa GUI, dashboards, demo UIs, and plugin UI fragments should
  not define the Runtime UI architecture.
- Useful implementation ideas may be extracted, but old UI shells should not be
  preserved merely because they exist.
- Useless files may be removed after reference checks and focused verification.
- Overly broad or mismatched names should be renamed only when the file remains
  necessary.
- Bulk deletion must avoid dependency bundles, manifests, generated packages,
  and files still required by tests or runtime imports.

See also:

- `docs/UI_REBUILD_AND_CLEANUP_PLAN.md`
- `docs/UI_MIGRATION_MAP.md`

## Functional Foundation Criteria

The Runtime UI reaches foundation-complete when:

- The read-only observatory state model is stable.
- The future frontend has a canonical data contract.
- Current legacy UI surfaces are classified as keep, legacy, remove, or rename.
- No direct dangerous action exists in the UI foundation.
- Focused tests validate observatory state, subsystem status, connections, and
  event serialization.
- Contract validation reports the bootstrap payload as coherent.
- The build order and system dashboards point to this document.

The Runtime UI reaches alpha-shell readiness when:

- The app builds with the existing frontend toolchain.
- The first viewport immediately communicates Aetherra as a living system.
- The visual shell consumes `/api/runtime-ui/bootstrap` when available.
- The shell remains useful in read-only fallback mode for local artifact
  inspection.
- No legacy dashboard layout, desktop metaphor, or dangerous control surface is
  presented.
- The Hub frontend catch-all can serve the generated build artifact from
  `Aetherra/lyrixa/gui/dist` without committing generated assets.

## Implementation Notes

The current foundation provides:

- `ObservatoryState`
- `ObservatorySubsystem`
- `ObservatoryConnection`
- `ObservatoryEvent`
- `build_observatory_state()`
- `ObservatoryScene`
- `ObservatorySceneNode`
- `ObservatorySceneConnection`
- `build_observatory_scene()`
- `build_runtime_ui_manifest()`
- `get_subsystem_profile()`
- `subsystem_guidance()`
- `collect_runtime_ui_system_status()`
- `collect_runtime_ui_events()`
- `build_runtime_ui_bootstrap_payload()`
- `build_runtime_ui_status_payload()`
- `build_runtime_ui_activity_payload()`
- `parse_observatory_mode()`
- `parse_limit()`
- `validate_runtime_ui_payload()`
- Runtime Observatory alpha shell in `Aetherra/lyrixa/gui/src/App.tsx`

These models are intentionally renderer-agnostic. A future 3D or graph-based
client can render them without importing legacy UI code.

## Hub API

The Runtime UI API discovery endpoint is:

```text
GET /api/runtime-ui/manifest
```

The manifest tells clients:

- Contract version.
- Supported modes, subsystems, and activity channels.
- Canonical Runtime UI endpoints.
- Current safety posture.
- Authority ownership for observe, approve, enforce, execute, and verify.

The initial foundation manifest must report `read_only: true`,
`controls_enabled: false`, and `legacy_ui_enabled: false`.

Compact health/readiness uses:

```text
GET /api/runtime-ui/status
```

This endpoint reports the Runtime UI API foundation status, contract version,
safety posture, endpoint map, and current contract validation result.

The preferred first-load endpoint for a future Observatory client is:

```text
GET /api/runtime-ui/bootstrap
```

The bootstrap payload combines:

- Runtime UI manifest.
- Current Observatory state.
- Renderer scene metadata.
- Bounded recent activity events.

Supported query parameters:

| Parameter | Values | Purpose |
| --- | --- | --- |
| `mode` | `first_launch`, `overview`, `architect`, `subsystem` | Selects presentation guidance for the initial state |
| `user` | bounded display name | Optional greeting personalization |
| `limit` | 1 to 100 | Maximum activity events returned |

Contract validation uses:

```text
GET /api/runtime-ui/contract/validate
```

This endpoint builds the current bootstrap payload and verifies that:

- The manifest, Observatory state, scene, and activity blocks are present.
- All read-only flags remain true and controls remain disabled.
- Scene nodes match Observatory subsystems.
- Scene connections reference known nodes.
- Activity events use supported visual channels.

The canonical read-only Observatory endpoint is:

```text
GET /api/runtime-ui/observatory
```

Supported query parameters:

| Parameter | Values | Purpose |
| --- | --- | --- |
| `mode` | `first_launch`, `overview`, `architect`, `subsystem` | Selects presentation guidance for the renderer |
| `user` | bounded display name | Optional greeting personalization |

Response shape:

```json
{
  "ok": true,
  "observatory": {
    "mode": "overview",
    "core_label": "AETHERRA",
    "greeting": "System Online",
    "read_only": true,
    "subsystems": [],
    "connections": [],
    "events": []
  }
}
```

The endpoint is intentionally read-only and sends `Cache-Control: no-store`.
It must not activate systems, mutate memory/code, approve actions, or execute
maintenance work. It may expose bounded status metadata that a future Cognitive
Observatory renderer can visualize.

Focused subsystem views use:

```text
GET /api/runtime-ui/subsystems/{subsystem_name}
```

This endpoint returns:

- The selected subsystem status.
- Related Observatory connections.
- A view profile with purpose, authority owner, expected panels, related API
  endpoints, and safety rules.
- Lyrixa guidance for the selected subsystem.

Subsystem names accept hyphenated or underscored forms where applicable, such as
`self-improvement` or `self_improvement`.

Renderer scene metadata uses:

```text
GET /api/runtime-ui/scene
```

This endpoint returns the full read-only Observatory state plus a stable
renderer-agnostic scene contract:

- Normalized 3D node coordinates.
- Subsystem visual groups.
- Node radius and emphasis values.
- Connection pulse and thickness values.
- Accessibility labels.

The scene contract is not a visual implementation. It is the stable spatial
model future WebGL, canvas, native, or accessibility-first clients can render
without importing legacy UI code.

## Understanding Rule

### What It Does

The Runtime UI System exposes Aetherra's current state as a read-only Cognitive
Observatory contract. It provides normalized Observatory state, subsystem view
profiles, scene metadata, activity events, bootstrap payloads, health status,
and contract validation through the Hub API.

### Why It Exists

It exists to make Aetherra visible as a living system without reviving the old
desktop-style or chatbot-first UI direction. It gives a future renderer one
canonical contract for showing system health, relationships, activity,
authority boundaries, and safety state.

### Authority It Owns

Runtime UI owns observation and presentation contracts:

- Read-only system state representation.
- Renderer-agnostic scene metadata.
- Subsystem profiles and Lyrixa guidance.
- Bounded activity stream metadata.
- Runtime UI manifest, status, bootstrap, and contract validation payloads.

### Authority It Does Not Own

Runtime UI does not own operational authority:

- It does not approve actions; Guardian owns approval.
- It does not enforce policy; Security owns enforcement.
- It does not execute changes; Self-Incorporation owns approved execution.
- It does not verify correction success; Homeostasis owns verification.
- It does not mutate memory, code, plugins, scripts, policies, or runtime state.
- It does not expose raw audit logs or sensitive internal records.

### How It Fails

Runtime UI fails safely by remaining observational:

- Invalid modes return `invalid_mode`.
- Invalid activity limits return a validation error.
- Unknown subsystems return `unknown_subsystem` with valid subsystem names.
- Contract validation can report degraded status without enabling controls.
- Missing Guardian status is represented as unknown metadata instead of raising
  privileged runtime failures.
- All Runtime UI endpoints use no-store responses and remain read-only.

### How It Interacts

Runtime UI interacts with Aetherra through bounded read models:

- Guardian, Security, Homeostasis, Maintenance, Aether Script, Memory,
  Consciousness, Agents, Self-Improvement, Self-Incorporation, Kernel, and
  Integration Validation appear as observable subsystems.
- Hub exposes the Runtime UI API routes.
- Future frontend clients should consume `/api/runtime-ui/bootstrap` first.
- OpenAPI exposes the Runtime UI contract for tooling.
- Contract validation proves the manifest, Observatory state, scene, and
  activity payloads remain internally coherent.

Runtime UI observes the system. It does not govern, enforce, execute, or repair
the system.

Activity stream metadata uses:

```text
GET /api/runtime-ui/activity
```

Supported query parameters:

| Parameter | Purpose |
| --- | --- |
| `channel` | Optional visual channel filter, such as `governance` or `regulation` |
| `source` | Optional subsystem/event source filter |
| `limit` | Bounded event count from 1 to 100 |

Events are normalized before they reach the UI:

- `severity` is constrained to known levels.
- `visual_channel` tells the renderer how to represent the event.
- `action_required` identifies critical operator attention without granting any
  control authority.
- `details` must stay bounded and redacted; raw audit logs should not be
  exposed here.

Runtime UI routes are included in:

```text
GET /api/openapi.json
```

## Verification

```powershell
python -m pytest -q -o addopts= --basetemp .pytest_tmp tests\unit\test_runtime_ui_observatory.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp tests\unit\test_runtime_ui_scene.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp tests\unit\test_runtime_ui_snapshot.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp tests\unit\test_runtime_ui_contract.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp tests\unit\test_runtime_ui_manifest.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp tests\unit\test_runtime_ui_payload.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp tests\unit\test_runtime_ui_query.py
python -m pytest -q -o addopts= --basetemp .pytest_tmp tests\unit\test_runtime_ui_api.py
python -m ruff check --select E9,F63,F7,F82,F841 Aetherra\runtime_ui aetherra_hub\blueprints\runtime_ui.py aetherra_hub\blueprints\openapi.py tests\unit\test_runtime_ui_observatory.py tests\unit\test_runtime_ui_scene.py tests\unit\test_runtime_ui_snapshot.py tests\unit\test_runtime_ui_contract.py tests\unit\test_runtime_ui_manifest.py tests\unit\test_runtime_ui_payload.py tests\unit\test_runtime_ui_query.py tests\unit\test_runtime_ui_api.py
python -m py_compile Aetherra\runtime_ui\__init__.py Aetherra\runtime_ui\observatory.py Aetherra\runtime_ui\scene.py Aetherra\runtime_ui\contract.py Aetherra\runtime_ui\manifest.py Aetherra\runtime_ui\profiles.py Aetherra\runtime_ui\snapshot.py Aetherra\runtime_ui\payload.py Aetherra\runtime_ui\query.py aetherra_hub\blueprints\runtime_ui.py aetherra_hub\blueprints\openapi.py tests\unit\test_runtime_ui_observatory.py tests\unit\test_runtime_ui_scene.py tests\unit\test_runtime_ui_snapshot.py tests\unit\test_runtime_ui_contract.py tests\unit\test_runtime_ui_manifest.py tests\unit\test_runtime_ui_payload.py tests\unit\test_runtime_ui_query.py tests\unit\test_runtime_ui_api.py
```

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
