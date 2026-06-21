# Aetherra Lyrixa System

Updated: 2026-06-20

This document explains how Lyrixa functions within Aetherra OS, what behaviors are expected, and how Lyrixa connects to the rest of the system (Service Registry, Hub Server, Engine, Memory, Agents, and Plugins).

## Purpose and scope

- Define Lyrixa as the conversational and interface layer for Aetherra OS
- Describe runtime contracts and integration points with Aetherra systems
- Document the Hub chat bridge, service registration, and safe-edit workflows
- Outline configuration flags and expected behaviors (GUI/CLI, offline, safety)

See also: Aetherra Chat System (./AETHERRA_CHAT_SYSTEM.md) for transport, streaming, and platform chat contracts used by Lyrixa and other clients.

## At‑a‑glance status

- System status: Functional foundation complete
- Chat service (identity/awareness, heuristics, safe edits): Implemented
- Hub chat bridge (POST /api/lyrixa/chat): Implemented (best‑effort, fallback)
- GUI integration (Basic/Hybrid PySide6): Partial (auto‑selection, backends wired)
- Plugin system (Lyrixa plugins; create/install/activate/execute): Implemented (local)
- Deep intelligence (Lyrixa full intelligence, router): Partial/Planned per env
- Prometheus metrics (Lyrixa‑specific): Planned (today uses Hub/Engine/Orchestrator series)

## Functional foundation completion

Lyrixa is functionally foundation complete for the current Aetherra milestone.
The completed foundation is the bounded identity, guidance, chat, safe-edit,
fallback, and status contract. It does not depend on the old GUI stack and does
not claim that Lyrixa's future Cognitive Observatory presentation is complete.

The current foundation gives Aetherra a stable human-facing guide that can
answer identity and system-awareness questions, degrade safely when optional
intelligence systems are unavailable, and expose clear readiness to Hub clients.

New Hub status surface:

- `GET /api/lyrixa/status` reports Lyrixa readiness, capabilities, degraded
  components, safe-edit posture, and authority boundaries.

### Understanding Rule

What it does:

- Provides Lyrixa identity, guidance, and awareness responses.
- Accepts chat requests through the internal `LyrixaChatService` and Hub
  `POST /api/lyrixa/chat`.
- Returns deterministic offline fallback responses when the service is not
  registered.
- Suggests conservative safe edits and only applies them through Guardian-audited
  scoped edits.
- Exposes readiness, capabilities, degraded components, and authority boundaries
  through `GET /api/lyrixa/status`.

Why it exists:

- Lyrixa is the user-facing guide for Aetherra. It helps the user understand,
  inspect, and interact with the system without turning every subsystem into its
  own conversational surface.
- Lyrixa gives the future Cognitive Observatory a voice and guide layer while
  keeping actual authority in Guardian, Security, Kernel, and subsystem owners.

Authority it owns:

- Lyrixa identity and guidance responses.
- Bounded chat-service fallback behavior.
- Safe-edit suggestion formatting.
- Service-level awareness summaries for user-facing explanation.
- Lyrixa readiness and capability reporting.

Authority it does not own:

- Guardian approval decisions.
- Security capability, sandbox, network, or signing policy.
- Kernel scheduling or lifecycle control.
- Memory persistence authority.
- Self-Incorporation execution authority.
- Runtime UI rendering.
- Legacy GUI lifecycle or future Observatory rendering.

How it fails:

- If Lyrixa is not registered, Hub chat returns a deterministic offline fallback
  and `/api/lyrixa/status` reports `offline`.
- If optional intelligence, memory, consciousness, or monitoring components are
  unavailable, Lyrixa reports degraded components and continues with safe
  deterministic behavior.
- If a chat request violates Guardian/Security policy, the request is rejected
  before the registry service is invoked.
- If safe-edit approval is denied, no file mutation occurs and the denial is
  recorded through Guardian audit.

How it interacts with other systems:

- Hub exposes Lyrixa chat and status endpoints.
- Guardian reviews chat ingress and safe-edit mutation attempts.
- Security provides capability checks for evidence and edit authority.
- Memory and consciousness integrations enrich responses when available, but are
  optional for the foundation.
- Runtime UI can consume Lyrixa status and guidance as a read-only guide layer.

## Architecture overview

Lyrixa sits at the boundary between users and the Aetherra OS core:

- Frontend/UI:
  - Basic GUI (preferred) and legacy Hybrid GUI (PySide6). The launcher picks the best available window and wires backend services via a Live Context Bridge.
  - CLI mode is available for headless use.
- Chat Service (`LyrixaChatService`):
  - Provides identity‑aware, workspace‑aware responses and optional safe code edits.
  - Optional intelligence stack: Lyrixa full intelligence and/or the Aetherra chat router when present; otherwise uses deterministic answers and heuristics.
- Service Registry:
  - Lyrixa registers a `lyrixa_chat` service for the OS. The Hub uses the registry to forward chat requests to Lyrixa (best‑effort).
- Hub Server integration:
  - Hub exposes a lightweight chat bridge at `POST /api/lyrixa/chat`. If the registry has no `lyrixa_chat` service, the Hub returns a deterministic fallback.
  - Hub `/api/stats` includes a `lyrixa_chat` registration snippet for UI display.
- Engine/Memory/Agents:
  - When available, the engine is used for reasoning; workspace awareness scans the repository (with safe excludes); the UI connects live to the Agent Orchestrator and Memory panel if present.
- Plugins:
  - The Lyrixa Plugin System manages local `lyrixa_plugins/` (create/install/activate/execute) with a JSON registry and basic policy budgets.

## Key integrations and flow

### 1) Hub chat bridge → Service Registry → Lyrixa

- Client calls Hub `POST /api/lyrixa/chat`.
- Hub looks up `lyrixa_chat` in the Service Registry and forwards the request with message and safe‑edit options.
- If the service is offline, Hub returns a deterministic fallback response so clients never break.

### 2) Lyrixa chat pipeline

- Workspace awareness: quick repo scan with excludes (git/.venv/docs/etc.).
- Identity/awareness queries: deterministic, safe responses.
- Intelligence: try Lyrixa full intelligence; fallback to chat router; if neither returns a good answer, fall back to deterministic reply.
- Safe edits (optional): when requests imply “fix/update/change,” Lyrixa suggests simple, safe edits; with `allow_edits=true` and a scoped `edit_root`, the first suggestion can be applied.

### 3) Frontend wiring

- The launcher selects a GUI (Basic preferred) or runs in CLI.
- Backend services (registry, plugin manager, engine, memory, orchestrator, hub connector) are attached to the window if present.

## Contracts and APIs

- Hub chat bridge
  - Endpoint: POST `/api/lyrixa/chat`
  - Request: `{ message | content: string, allow_edits?: bool, edit_root?: string }`
  - Response (when Lyrixa online; superset):
    - `{ text: string, suggestions: Array<object>, applied_changes: Array<object>, identity?: object, awareness?: object }`
  - Response (Hub fallback when Lyrixa offline):
    - `{ text: string, suggestions: [], applied_changes: [] }`

- Lyrixa chat service (internal async API)
  - `chat(message: str, opts?: ChatOptions) -> ChatResponse`
  - `suggest_fixes(hint: str = "", limit: int = 3) -> list`
  - `apply_fix(suggestion, edit_root?: Path) -> (ok: bool, change: dict)`
  - ChatOptions: `{ user_id: str, session_id: str, max_tokens: int, allow_edits: bool, edit_root: Path }`
  - ChatResponse: `{ text: str, suggestions: list, applied_changes: list, identity: object, awareness: object }`

- Service Registry
  - Service name: `lyrixa_chat`
  - Hub forwards via registry method `handle_message("lyrixa.chat", payload)`.

- GUI selection
  - Basic GUI (`Aetherra.lyrixa.lyrixa_basic_gui`) preferred when available; Hybrid GUI otherwise. CLI mode supported.

## Expected behaviors

- If Lyrixa is offline, Hub chat returns a friendly fallback and no suggestions/changes.
- Identity/awareness questions should respond deterministically and safely.
- Workspace scans must respect exclude lists and remain lightweight.
- Edits require both `allow_edits=true` and a valid `edit_root`; edits are conservative and scoped.
- When engine/router are unavailable, responses degrade gracefully.

## Configuration and environment

Examples (subject to change as implementation evolves):

- `AETHERRA_USE_HYBRID=1` — prefer legacy Hybrid GUI (otherwise Basic is preferred)
- `AETHERRA_BOOT_MENU=1` — show boot menu to pick GUI/CLI or Safe Mode
- `AETHERRA_SAFE_MODE=1` — reduce functionality for safer startup
- (Removed) Offline gating: Lyrixa now attempts full initialization by default and degrades gracefully.

Related Hub/Agents developer APIs (opt‑in, token‑guarded):

- `AETHERRA_AI_API_ENABLED=1` and optionally `AETHERRA_AI_API_REQUIRE_TOKEN=1`
- `AETHERRA_AGENTS_API_ENABLED=1` and optionally `AETHERRA_AGENTS_API_REQUIRE_TOKEN=1`

## Service and Endpoint Summary

- Hub
  - `GET /api/lyrixa/status` - readiness, capabilities, degraded components,
    and authority boundaries
  - `POST /api/lyrixa/chat` — chat bridge to Lyrixa (best‑effort)
  - `GET /api/stats` — includes `lyrixa_chat` registration status
- Service Registry
  - Service: `lyrixa_chat` — Lyrixa chat handler registered by the OS launcher

## Security and safety

- Safe‑edit guardrails: explicit `allow_edits`, scoped `edit_root`, and simple transforms only.
- Plugin policy budgets: max executions and optional internal flags to limit risk.
- GUI integrates with Aetherra security defaults (plugin signing at Hub; secrets and capabilities managed under OS policies).

## Observability

- Lyrixa‑specific Prometheus series are not yet exposed.
- Overall health and activity are visible through:
  - Hub `/api/stats` and `/metrics` (kernel/registry/orchestrator)
  - GUI status panes (when Hybrid present) and CLI status dumps

## Appendices

- Minimal Hub fallback response
  - `{ "text": "Lyrixa chat service is not online right now. I can still answer identity and Aetherra questions.", "suggestions": [], "applied_changes": [] }`
- Example ChatResponse (when Lyrixa online)
  - `{ "text": "…", "suggestions": [{"title": "Fix…", "file": "…", "action": "…"}], "applied_changes": [], "identity": {…}, "awareness": {…} }`

---

Status: ✅ Implemented (core chat, Hub bridge, plugin system) · 🛠 partial (GUI wiring, intelligence) · 🔭 planned (metrics)

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

