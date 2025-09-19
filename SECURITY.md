# Security Policy

## Supported Versions

We support the latest main branch. Please open issues and PRs against main.

## Reporting a Vulnerability

If you discover a security vulnerability, please do not open a public issue.

Instead, email <security@aetherra.dev> with:

- A detailed description of the issue and its impact
- Steps to reproduce or a proof-of-concept
- Affected components/files (paths)

We aim to acknowledge reports within 3 business days and provide updates on
assessment and remediation timelines.

## Scope

- Runtime enforcement (capabilities, signatures, tokens)
- Aether scripts and signature verification
- Hub APIs and authentication/authorization

## Responsible Disclosure

Please give us a reasonable time to remediate before public disclosure.

## Production-Safe Defaults (Hub Developer AI API)

When running the Hub’s developer AI endpoints, production builds enforce safer defaults:

- AETHERRA_PROFILE=prod enables stricter behavior by default.
- AI API tokens are required by default in production: set either
  `AETHERRA_AI_API_TOKEN` or `AETHERRA_HUB_CONTROL_TOKEN` and provide it via
  the `X-Aetherra-Token` header.
- Inbound network allowlist is enforced for AI endpoints via
  `AETHERRA_NETWORK_ALLOWLIST`.
  - If unset in production, access defaults to localhost only
    (`localhost,127.0.0.1,::1`).
  - You can add domains or wildcards (for example, `*.corp.example.com`).
- Startup guard prevents enabling AI API without a token in production.

Additional recent hardening:

- Night schedule timezone guard: kernel exports
  `aetherra_kernel_night_schedule_guard_pass` (0=failing) until either
  `AETHERRA_NIGHT_TZ` is set to an IANA timezone or `AETHERRA_NIGHT_UTC=1` is
  provided in prod/staging. This prevents ambiguous local‑time scheduling.
- QFAC policy gating metrics: `aetherra_qfac_policy_mode_current`,
  `aetherra_qfac_policy_allowed`, and `aetherra_qfac_policy_info{key=reason|policy}`
  expose quantum/hybrid downgrade reasons for audit (shadow vs. enforce).
- Scratchpad redaction default: absent an explicit, permitted `scratchpad_policy`,
  Hub forces `redacted` and masks reasoning/evidence fields. `persisted` requires
  `evidence.view` capability; `ephemeral` remains allowed.
- Key encryption status: `aetherra_keys_encrypted` and
  `aetherra_master_key_present` provide an at‑a‑glance encryption posture signal.

See `docs/PROJECT_OVERVIEW.md` and `.env.example` for full variable
descriptions and examples.

## HMR (Hot Module Reload) Safety in Production

HMR is powerful and risky if misconfigured. In production profile
(`AETHERRA_PROFILE=prod`):

- HMR requires strict mode: set `AETHERRA_HMR_STRICT=1`.
- HMR requires non-empty allowed sources: set `AETHERRA_HMR_ALLOWED_SOURCES` to
  a comma-separated list of approved modules or path prefixes (for example,
  `engine_v2,adapters/memory/*`).
- If these requirements are not met, the launcher refuses to enable HMR.
- Audit rotation defaults are enforced when unset:
  `AETHERRA_HMR_AUDIT_MAX_BYTES=5242880` (5 MiB) and
  `AETHERRA_HMR_AUDIT_MAX_BACKUPS=3`.
- The Hub surfaces HMR config via Prometheus (`aetherra_hmr_*` gauges) and
  `/api/kernel/metrics` under `hmr`.

Review these settings in `.env.example` and `docs/PROJECT_OVERVIEW.md` before
enabling HMR in sensitive environments.

## Policy Bootstrap Quickstart

Generate safe starter policy files under your user policy directory
(`~/.aetherra/policy`) using the built-in CLI.

PowerShell (Windows):

```powershell
# Create capabilities.json and net_policy.json with safe defaults
python -m Aetherra.cli.policy_bootstrap --all

# Add extra allowed domains to network policy
python -m Aetherra.cli.policy_bootstrap --network --allow api.example.com .corp.example

# Overwrite existing files if needed
python -m Aetherra.cli.policy_bootstrap --all --force
```

Notes:

- In production profile, capabilities are deny-by-default and network policy is
  strict by default.
- Default outbound allowlist (when no policy file exists):
  `localhost, 127.0.0.1, .aetherra.dev`.
- You can override the policy home for CI/tests with `AETHERRA_POLICY_HOME`.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
