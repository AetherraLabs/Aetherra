# Aetherra Self-Incorporation System – Production Readiness Guide

    Date: 2025-09-16
    Status: Hardened (Phase 1 complete)
    Owner: Self-Incorporation / Platform Engineering

    ---
    ## 1. Snapshot

    This document is generated from structured metadata (`metadata/selfinc_readiness.json`). Edit the JSON to update.

    ---
    ## 2. Validation Dimensions

| Dimension                | Outcome          | Notes                                       |
| ------------------------ | ---------------- | ------------------------------------------- |
| Cold Boot                | PASS             | Registers real instance; artifacts created  |
| API Availability         | PASS             | Status endpoint healthy                     |
| Security Strict Mode     | PASS             | Env guard enforces strict posture           |
| Capability Denial        | PASS             | Unauthorized ops denied                     |
| HMR Rollback Resilience  | PASS (code-path) | Rollback path & metrics verified            |
| Spec → Tests Enforcement | PASS             | Kernel loop + hub + registry + script tests |

    ---
    ## 3. Environment Variables

| Variable                                           | Required        | Purpose                       | Auto-Remediation            |
| -------------------------------------------------- | --------------- | ----------------------------- | --------------------------- |
| AETHERRA_PROFILE                                   | prod/production | Activates hardening guard     | N/A                         |
| AETHERRA_REQUIRE_CAPABILITIES                      | 1               | Capability policy enforcement | Abort if unset              |
| AETHERRA_SCRIPT_VERIFY_STRICT                      | 1               | Script signature strictness   | Abort if unset              |
| AETHERRA_SIGNING_STRICT                            | 1               | Plugin signing strict mode    | Abort if unset              |
| AETHERRA_NET_STRICT                                | 1               | Restrict outbound network     | Auto-enable + allowlist     |
| AETHERRA_NETWORK_ALLOWLIST                         | Value list      | Hosts allowlist               | Defaults if missing         |
| AETHERRA_AI_API_ENABLED                            | 1 (if AI API)   | Enable AI endpoints           | Warn if insecure            |
| AETHERRA_AI_API_REQUIRE_TOKEN                      | 1 (if AI API)   | Require auth token            | Failure recorded if missing |
| AETHERRA_AI_API_TOKEN / AETHERRA_HUB_CONTROL_TOKEN | Yes             | Authentication secret         | Required if require_token=1 |
| AETHERRA_SELFINC_ENABLED                           | 1 (optional)    | Auto startup task             | Idle if missing             |

    ---
    ## 4. HTTP API (Subset)

| Endpoint              | Method | Auth | Shape                   |
| --------------------- | ------ | ---- | ----------------------- |
| /api/selfinc/status   | GET    | None | {status,running,...}    |
| /api/selfinc/scan     | POST   | None | {queued|started|...}    |
| /api/selfinc/apply    | POST   | None | {ok,applied,rb_token?}  |
| /api/selfinc/rollback | POST   | None | {ok}|error              |
| /api/selfinc/audit    | GET    | None | {audit_summary,filters} |

    ---
    ## 5. Risk Register

| Risk                             | Likelihood | Impact | Mitigation                                                                               |
| -------------------------------- | ---------- | ------ | ---------------------------------------------------------------------------------------- |
| Ethics endpoints instrumentation | Medium     | Low    | Ledger-backed metrics, audit, and scoring now implemented; further hardening in Phase 2. |
| Apply/rollback race              | Low        | Medium | Add lock + idempotency                                                                   |

    ---
    ## 6. Phase 2 Items
    - Token + capability scoped auth
- Ethics decision provenance
- Streaming scan progress
- Deterministic synthetic delta fixtures
- Cryptographic signing of plans
- Expanded metrics (latency, ethics counts)

    ---
    Generated: 2025-09-16T22:48:01.809046Z
