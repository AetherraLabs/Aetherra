# Security Policy

We take security and privacy seriously. Please follow these guidelines to report vulnerabilities and keep users safe.

## Supported Versions

We aim to support the latest stable main branch. Security fixes are backported on a best-effort basis.

## Reporting a Vulnerability

- Do not open public issues for security vulnerabilities.
- Email security reports to <mailto:security@aetherralabs.org> with details and a proof of concept when possible.
- Please allow up to 72 hours for initial response.

## Scope

All code in this repository, published Docker images, and hosted demo infrastructure are in scope unless explicitly marked otherwise.

## Coordinated Disclosure

- We follow responsible disclosure. We will work with you on a timeline.
- We will credit reporters in release notes unless you prefer to remain anonymous.

## Hardening Checklist (Internal)

- Secret scanning and push protection enabled
- CodeQL security analysis enabled
- Dependabot security updates enabled
- CI uses least-privilege tokens and avoids printing secrets
- Dependencies pinned and lockfiles committed

## Production-Safe Defaults (Hub Developer AI API)

When running the Hub’s developer AI endpoints, production builds enforce safer defaults:

- AETHERRA_PROFILE=prod enables stricter behavior by default.
- AI API tokens required by default in production: set either `AETHERRA_AI_API_TOKEN` or `AETHERRA_HUB_CONTROL_TOKEN` and provide it via `X-Aetherra-Token`.
- Inbound network allowlist is enforced for AI endpoints via `AETHERRA_NETWORK_ALLOWLIST`.
	- If unset in production, access defaults to localhost only (`localhost,127.0.0.1,::1`).
	- You can add domains or wildcards (e.g., `*.corp.example.com`).
- Startup guard prevents enabling AI API without a token in production.

See `docs/PROJECT_OVERVIEW.md` and `.env.example` for full variable descriptions and examples.

## HMR (Hot Module Reload) Safety in Production

HMR is powerful and risky if misconfigured. In production profile (AETHERRA_PROFILE=prod):

- HMR requires strict mode: set `AETHERRA_HMR_STRICT=1`.
- HMR requires non-empty allowed sources: set `AETHERRA_HMR_ALLOWED_SOURCES` to a comma-separated list of approved modules or path prefixes (e.g., `engine_v2,adapters/memory/*`).
- If these requirements are not met, the launcher refuses to enable HMR.
- Audit rotation defaults are enforced when unset: `AETHERRA_HMR_AUDIT_MAX_BYTES=5242880` (5 MiB) and `AETHERRA_HMR_AUDIT_MAX_BACKUPS=3`.
- The Hub surfaces HMR config via Prometheus (`aetherra_hmr_*` gauges) and `/api/kernel/metrics` under `hmr`.

Review these settings in `.env.example` and `docs/PROJECT_OVERVIEW.md` before enabling HMR in sensitive environments.

## Policy Bootstrap Quickstart

Generate safe starter policy files under your user policy directory (`~/.aetherra/policy`) using the built-in CLI:

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

- In production profile, capabilities are deny-by-default and network policy is strict by default.
- Default outbound allowlist (when no policy file exists): `localhost, 127.0.0.1, .aetherra.dev`.
- You can override the policy home for CI/tests with `AETHERRA_POLICY_HOME`.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
