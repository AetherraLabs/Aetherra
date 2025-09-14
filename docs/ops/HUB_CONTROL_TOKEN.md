# Hub Control Token

When remote control APIs are enabled, the Hub requires a token for privileged control plane operations.

## Environment

- `AETHERRA_HUB_CONTROL_TOKEN` — shared secret used for Hub control plane APIs
- `AETHERRA_AI_API_TOKEN` — primary AI API token; Hub will also accept `AETHERRA_HUB_CONTROL_TOKEN` where noted

## Scope

- Control plane endpoints under `/api/kernel/control/*` (pause, resume, drain, queue limits)
- Peer management endpoints under `/api/peers*` (announce/sync) when enabled
- Some admin reads may also require a token in hardened mode

## Client behavior

- Send the token via header: `X-Aetherra-Token: <token>`
- If `AETHERRA_AI_API_REQUIRE_TOKEN=1`, the Hub enforces token on AI endpoints; control plane enforces token when configured regardless
- Tests demonstrate precedence fallbacks: if `AETHERRA_AI_API_TOKEN` is unset, `AETHERRA_HUB_CONTROL_TOKEN` is used

## Security notes

- Prefer a distinct token for control plane; rotate regularly
- Do not expose control endpoints publicly; restrict by network policy and reverse proxy
- Audit access via Hub logs and (if enabled) the security ledger

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

