# Strict mode gates (signatures + caps)

Labels: phase:1, area:security, type:feature
Milestone: Self-Incorporation v1

## Description

Enable strict mode which enforces .aether HMAC signatures, plugin ed25519 signatures,
and deny-by-default capability policy.

## Acceptance Criteria

- When `AETHERRA_SELFINC_STRICT=1`:
  - .aether HMAC signature verification must pass, else quarantine
  - Plugin artifacts must verify ed25519 signature, else quarantine
  - Deny-by-default capability policy; require explicit allowlist
- Quarantine includes remediation guidance in logs/messages
- Unit tests for positive path and quarantine path
