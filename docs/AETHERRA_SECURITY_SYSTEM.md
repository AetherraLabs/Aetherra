# Aetherra Security System (Aetherra OS + Lyrixa)

Updated: 2025-08-27

This document describes the security measures implemented in Aetherra OS and Lyrixa today, how to configure them, and what’s planned next. It is grounded in the current codebase and tests to avoid over‑claiming.

## Principles

- Least privilege and safe-by-default
- Verify what runs: signatures, static checks, auditability
- Opt-in telemetry and privacy first
- Defense in depth with graceful fallbacks in dev

## At‑a‑glance status

- Script signing (.aether): Done (HMAC-SHA256, strict mode available)
- Plugin manifest signing (ed25519): Partial (strict toggle; PyNaCl optional)
- Secrets (API keys): Improved (file store + env override; rotation and leak checks; encrypt-at-rest optional via master key)
- Sandbox for eval: Partial (best-effort Python AST/eval restrictions; containers/policy engine planned)
- Security scans (keys/memory/files/network): Done (periodic, alerting + auto-cleanup hooks)
- Prompt injection defenses: New (heuristic scanner with high‑risk short‑circuit)
- Capability enforcement: New (deny-by-default option with policy file)
- Network policy: New (domain allow/deny with strict mode + safe HTTP wrappers)
- Telemetry privacy: Partial (opt-in enforced by tests; minimal counters)
- Audit and static risk for .aether: Done (report + thresholds; strict signature verify optional)

## Components and controls

### 1) Identities and secret management

- API key store: `Aetherra/security/api_keys.py`
  - Stores keys in user config dir: `~/.aetherra/keys.json` (Windows-friendly path), with an in-memory cache.
  - Env override: any key can be provided via `AETHERRA_<NAME>` environment variable; env wins over file.
  - Operations: `get_key(name)`, `set_key(name, value)`, `delete_key(name)`, `get_key_scoped(name, requester)`.
  - Encrypt-at-rest (optional): set a Fernet master key via env `AETHERRA_KEYS_MASTER` or file `~/.aetherra/keys_master.key`.
    - When a master key is present, keys are stored encrypted with structure `{ "__encrypted__": true, name: {"cipher": "..."} }`.
    - Utility: `ensure_master_key()` will generate and persist a master key file and auto-upgrade existing plaintext entries.
  - Scoped access: deny-by-default when a `requester` is specified unless allowed by `~/.aetherra/policy/keys_policy.json`.

- Rotation and leak checks: `Aetherra/aetherra_core/system/security_system.py`
  - Rotation advisory based on age (configurable `api_key_rotation_days`, default 30 days).
  - Leak checks scan environment variables and common files for “api_key”/“secret” strings.
  - File permission checks on sensitive paths (e.g., `.aetherra/secure`, `.aetherra/keys`).

### 2) Code and artifact signing

- .aether script signing: `Aetherra/security/script_signing.py`
  - HMAC-SHA256 over the script body; signature embedded in first line as `# @signature: <hex>`.
  - Secret source: API key store (`aether_script_signing_secret`) or dev fallback.
  - Strict verification gate: set `AETHERRA_SCRIPT_VERIFY_STRICT=1` or pass `--strict` to the verifier.
  - Tooling: `tools/verify_aether_scripts.py` generates `aether_static_report.md`, enforces thresholds, and validates signatures when strict.

- Plugin manifest signing: `Aetherra/security/plugin_signing.py`
  - Ed25519 signatures via PyNaCl when available; permissive fallback otherwise.
  - Strict mode: `AETHERRA_SIGNING_STRICT=1` makes unsigned/invalid manifests fail.
  - Revocation: checks `~/.aetherra/revocations.json` for revoked pubkeys/key_ids.
  - Transparency log: appends JSONL entries to `~/.aetherra/signing_log.jsonl` on sign.
  - Optional integrity: when `code_hash` and `code_files` are present in the manifest, verify SHA256 over the file list.

### 3) Execution isolation and permissions

- Sandbox (best-effort): `Aetherra/security/sandbox.py`
  - `safe_eval` uses AST checks to disallow dangerous nodes; tight builtin whitelist.
  - Intended for small arithmetic/logic expressions only; not a general-purpose sandbox.
  - Strong isolation (containers/VMs/policy engine) is recommended for untrusted plugins (planned).
  - Quotas available: `run_with_timeout` (wall-clock) and `ensure_memory_budget` (RSS best-effort); exceptions `TimeBudgetExceeded` and `MemoryBudgetExceeded` raised on violations.

- Capability/permissions model (policy):
  - Coding System spec establishes deny-by-default capabilities for plugins and policy‑mediated file/network/process access.
  - Implementation: `Aetherra/security/capabilities.py` with optional strict mode via `AETHERRA_REQUIRE_CAPABILITIES=1` and policy file `~/.aetherra/policy/capabilities.json`:
    {
      "allow": { "core:webhook_manager": ["network:outbound", "network:webhook"] }
    }
  - Wired example: `Aetherra/core/webhook_manager.py` checks capability `network:webhook` before firing.

### 4) System scanning and hardening

- Security System Orchestrator: `Aetherra/aetherra_core/system/security_system.py`
  - Periodic scans (threaded): API keys, memory, files, network → alerts and auto‑cleanup hooks.
  - UI alerts feed: JSONL appended at `.aetherra/security/alerts.jsonl` for recent alerts display.
  - Memory protection: integrates with the core `MemoryManager` for usage stats; high-usage log notice.
  - File system scanning: flags suspicious extensions/patterns and permissive permissions.
  - Network: placeholder open‑port checks (extend per deployment).
  - Logging: security/audit files under `.aetherra/security/`.

### 6) Prompt injection defenses

- Module: `Aetherra/security/prompt_defense.py`
  - Heuristic pattern-based scanner detects jailbreak/injection phrases and scores risk.
  - Integrated into `Aetherra/core/chat_router.py`: high-risk (>= 0.6) short-circuits with a guarded response and emits a security alert if the orchestrator is available.

### 7) Network policy and safe HTTP wrappers

- Module: `Aetherra/security/net_policy.py`
  - Policy file `~/.aetherra/policy/net_policy.json` with `allow_domains`/`deny_domains`.
  - Strict mode via `AETHERRA_NET_STRICT=1` denies non-allowlisted domains.
  - Safe wrappers `http_get/http_post` enforce policy and timeouts; used by `Aetherra/core/webhook_manager.py`.

### 5) Telemetry and privacy

- Opt-in telemetry (tests): `tests/unit/test_telemetry_optin.py`
  - Telemetry ingestion/stats exist in the Hub; opt‑in is enforced by environment/config (module: `Aetherra.telemetry.optin`).
  - Defaults are conservative; tests verify explicit opt‑in is respected.
  - Differential Privacy: runtime‑toggleable via Lyrixa Settings (Enable DP + epsilon). Backend applies via `Telemetry.set_dp(enabled, epsilon)` and persists DP flags to `~/.aetherra/telemetry.json`.
  - Redactions and noise: filters out `content`, `prompt`, `message`; redacts common IDs; applies Laplace noise to numeric fields when DP is enabled.

- Audit ledger for .aether runs
  - When enabled, execution emits anonymized traces and audit records (see Coding System spec). Redaction hooks prevent sensitive content leakage in logs.

## Configuration (env flags and tasks)

- Strict signing for plugins: set `AETHERRA_SIGNING_STRICT='1'`.
- Strict signature verification for .aether: set `AETHERRA_SCRIPT_VERIFY_STRICT='1'`.
- Strict require semantics in generated .aether: `AETHERRA_REQUIRE_STRICT='1'`.
- Capabilities strict mode: `AETHERRA_REQUIRE_CAPABILITIES='1'` (deny-by-default without explicit grants). In production profile (`AETHERRA_PROFILE=prod|production`), this is enforced by default.
- Network strict mode: `AETHERRA_NET_STRICT='1'` (deny-by-default for non-allowlisted domains). In production profile, strict mode is enabled by default; when no policy file exists, a safe allowlist is assumed: `localhost`, `127.0.0.1`, `.aetherra.dev`.
- Deterministic/test profiles: see Coding/Memory specs (e.g., `AETHERRA_PROFILE=test`).

VS Code Tasks (Terminal → Run Task):

- “Aether Verify (Quick, Test Profile)” → static .aether checks and signature validation (test profile).
- “Aether Verify (Strict Signatures)” → strict signature checks across `.aether` files.

PowerShell examples:

```powershell
$env:AETHERRA_SCRIPT_VERIFY_STRICT='1'; python tools/verify_aether_scripts.py --strict --output aether_static_report.md
$env:AETHERRA_SIGNING_STRICT='1'; pytest -q tests/test_hub_signing.py tests/test_discovery_signing.py
# Bootstrap policy files (capabilities and network) with safe defaults
python -m Aetherra.cli.policy_bootstrap --all
python -m Aetherra.cli.policy_bootstrap --network --allow api.example.com .corp.example
```

## Observability and reports

- .aether static risk report: `aether_static_report.md` (generated by `tools/verify_aether_scripts.py`).
- Security logs: `.aetherra/security/security.log` and `.aetherra/security/alerts.log`.
- Docs verification: “Verify Docs Consistency” task checks env and endpoint references across docs.
Lyrixa UI: Security Alerts panel displays `.aetherra/security/alerts.jsonl` in real time via the web bridge.

Alerts CLI (view recent and follow live):

- Module: `Aetherra/cli/alerts.py`
- Show last N alerts (PowerShell):

```powershell
python -m Aetherra.cli.alerts --recent 30
```

- Follow the live feed (Ctrl+C to stop):

```powershell
python -m Aetherra.cli.alerts --follow
```

- Custom path (defaults to `./.aetherra/security/alerts.jsonl`):

```powershell
python -m Aetherra.cli.alerts --path C:\path\to\alerts.jsonl --recent 50
```

## Known limitations and roadmap

- API key storage is plaintext today. Recommended mitigations: provide keys via environment variables or integrate an OS keychain/secret manager. A built‑in encrypt‑at‑rest option (e.g., keyring/cryptography) is planned.
- The Python sandbox is intentionally narrow and not a substitute for containerization/VMs; stronger isolation and a central policy engine are planned.
  - Recommended deployment tier for untrusted plugins: containerized plugin runner (per-plugin process/container boundary with network/FS policies). This is the suggested production posture until the integrated isolation layer ships.
- Network/TLS hardening depends on deployment; add reverse proxy/TLS termination and CORS policies per environment.
- Capability enforcement is partly policy/docs‑level; wire stricter checks into plugin execution and hub operations over time.

## References (code and tests)

- API keys: `Aetherra/security/api_keys.py`
- Script signing (.aether): `Aetherra/security/script_signing.py`, `tools/verify_aether_scripts.py`, tests in `tests/unit/`
- Plugin signing (ed25519): `Aetherra/security/plugin_signing.py`, hub/discovery tests `tests/test_hub_signing.py`, `tests/test_discovery_signing.py`
- Security orchestration: `Aetherra/aetherra_core/system/security_system.py`
- Sandbox: `Aetherra/security/sandbox.py`
- Prompt injection: `Aetherra/security/prompt_defense.py`, integration in `Aetherra/core/chat_router.py`
- Capabilities: `Aetherra/security/capabilities.py`, usage in `Aetherra/core/webhook_manager.py`
- Network policy: `Aetherra/security/net_policy.py`, usage in `Aetherra/core/webhook_manager.py`
- Telemetry (opt-in): `Aetherra/telemetry/optin.py` (referenced by tests), `tests/unit/test_telemetry_optin.py`
- Policy/guardrails overview: `docs/AETHERRA_CODING_SYSTEM.md`

See also:

- Aetherra Coding System: `docs/AETHERRA_CODING_SYSTEM.md`
- Aetherra Memory System: `docs/AETHERRA_MEMORY_SYSTEM.md`
- Security policy for reporting: `SECURITY.md`

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

