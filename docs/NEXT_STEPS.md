# Next Steps: Lyrixa Chat Production Readiness

This plan captures immediate, low-risk follow-ups after wiring Lyrixa Chat into the Service Registry and Hub endpoint.

## Priority 1 — Validation & UX

- Add hub stats field for lyrixa_chat availability (e.g., in `/api/stats`):
  - Include `lyrixa_chat: { registered: bool, healthy: bool }` if registry is available.
- Add a small health route to LyrixaChatAdapter (e.g., `lyrixa.health`) and wire through the registry for quick checks.
- Expand capability tests:
  - Ensure `/api/lyrixa/chat` returns deterministic identity response when intelligence providers are offline or unavailable.

## Priority 2 — Docs & DevEx

- Update `docs/PROJECT_OVERVIEW.md` to reference `docs/LYRIXA_CHAT_ENDPOINT.md`.
- Add examples to README/Quickstart for using the chat endpoint from curl and a tiny Python snippet.
- Trim endpoints in PROJECT_OVERVIEW that aren’t real routes to calm the docs consistency report.

## Priority 3 — Observability & Safety

- Log audit entries on applied_changes from Lyrixa (file, action, outcome) with an audit channel.
- Add `edit_root` default policy in config (e.g., repo root) with allowlist; tests for scope enforcement.
- Rate-limit hub chat endpoint to prevent spam during local testing (simple token bucket or per-IP cooldown).

## Priority 4 — Integration Polish

- Optionally surface Lyrixa service status in Hub web index page.
- Add service heartbeat metrics to the registry stats for visibility.

## Done

- LyrixaChatService registered as `lyrixa_chat` with heartbeat adapter.
- Hub server exposes `/api/lyrixa/chat` bridge with deterministic fallback.
- Capability tests pass, including new endpoint test.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
