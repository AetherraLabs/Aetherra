# Aetherra Deployment Tiers

This guide clarifies maturity and hardening levels so operators can align expectations with current capabilities.

| Tier                | Intended Use                         | Characteristics                                                                                                   | Included Systems                                                                                                                         | Notes                                                                |
| ------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Dev                 | Local exploration, feature work      | Fast iteration, relaxed safety, optional mocks                                                                    | Hub (dev APIs), Lyrixa chat (mock fallback), Memory (persistent + optional QFAC), Plugin loader (non-strict)                             | HMR allowed; signing optional; network allowlist relaxed             |
| Test (Smoke / CI)   | Deterministic validation, gating     | Strict verification, bounded queues, deterministic profile, no external egress except allowlist                   | Kernel loop, Service Registry, Memory, Plugin Manager (timeouts + breaker), Script verifier (strict), Hub disabled or tokenless internal | Use env block in `SMOKE_PROFILE.md`; network strict; AI API disabled |
| Beta Hardened       | Early adopter staging / limited prod | Strict signing + require, capabilities enforced, network allowlist + tokens, circuit breakers, metrics dashboards | All core systems + metrics exporter, limited QFAC (classical mode)                                                                       | HMR off (unless strict mode enforced); Trainer still stub/pilot      |
| Production (Target) | Stable external automation           | Same as Beta Hardened + audited retention policies, sandbox enhancements, plugin provenance, provider attestation | Adds hardened Trainer persistence, container isolation, escalation review                                                                | Some items in-progress (see ROADMAP)                                 |

## Current Gaps (2025-09)

- Trainer persistence & advanced eval scoring: planned (ROADMAP) – treat as experimental.
- Full sandbox/container isolation: partial; rely on capability + signing gates until hardened.
- Federation sync: stub endpoints (501) – exclude from prod runbooks.
- Quantum advanced (hybrid/quantum) policy modes: classical recommended for production.

## Recommended Env Blocks

See `SMOKE_PROFILE.md` for canonical smoke profile. Production quick reference:

```
AETHERRA_PROFILE=prod
AETHERRA_AI_API_REQUIRE_TOKEN=1
AETHERRA_NET_STRICT=1
AETHERRA_NETWORK_ALLOWLIST=localhost,127.0.0.1,.aetherra.dev
AETHERRA_SCRIPT_VERIFY_STRICT=1
AETHERRA_SIGNING_STRICT=1
AETHERRA_REQUIRE_CAPABILITIES=1
AETHERRA_REQUIRE_STRICT=1
AETHERRA_HMR_ENABLED=0
AETHERRA_KERNEL_QSIZE_HIGH=128
AETHERRA_KERNEL_QSIZE_NORMAL=512
AETHERRA_KERNEL_QSIZE_BACKGROUND=512
AETHERRA_KERNEL_DLQ=1
AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC=20
AETHERRA_PLUGIN_CB_THRESHOLD=3
AETHERRA_PLUGIN_CB_COOLDOWN_SEC=60
AETHERRA_QFAC_MODE=classical
```

## Documentation Hooks

- Kernel heartbeat stale defaults now configurable: `AETHERRA_REGISTRY_HEARTBEAT_SEC` (default 60) and `AETHERRA_REGISTRY_STALE_SEC` (default 3x heartbeat).
- OS status file now includes `pid`, `host`, `process_uptime_sec`; stale cleanup window: `AETHERRA_OS_STATUS_GRACE_SEC` (default 300).

Update related docs when thresholds or defaults change.
