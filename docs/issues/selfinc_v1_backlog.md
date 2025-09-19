# Aetherra OS — Self-Incorporation v1 Backlog (Copy/Paste Issues)

This file contains a copy-ready set of GitHub issues for the Self-Incorporation v1
milestone. Each card includes labels and an acceptance checklist. Paste each section
as a new issue in GitHub.

Milestone: Self-Incorporation v1

---

## 1) Expose /api/selfinc/status + Prom metrics

Labels: phase:1, area:observability, type:feature

Description:
Expose an HTTP endpoint to surface Self-Incorporation status and Prometheus metrics.

Acceptance Criteria:

- GET /api/selfinc/status returns JSON with counts:
  {found, classified, planned, applied, quarantined}
- Prometheus counters/gauges for the same are exported on /metrics
- Basic error handling documented; 200 OK with payload or clear 5xx on failure
- Minimal unit tests for the endpoint and metrics registry updates

Notes:

- Wire into the existing hub/Flask app if available
- Document env flags in PROJECT_OVERVIEW.md

---

## 2) Strict mode gates (signatures + caps)

Labels: phase:1, area:security, type:feature

Description:
Enable strict mode which enforces .aether HMAC signatures, plugin ed25519 signatures,
and deny-by-default capability policy.

Acceptance Criteria:

- When `AETHERRA_SELFINC_STRICT=1`:
  - .aether HMAC signature verification must pass, else quarantine
  - Plugin artifacts must verify ed25519 signature, else quarantine
  - Deny-by-default capability policy; require explicit allowlist
- Quarantine includes remediation guidance in logs/messages
- Unit tests for positive path and quarantine path

---

## 3) Quarantine → Escalate → Release flow (UI hooks)

Labels: phase:1, area:ui, type:feature

Description:
Provide a user-visible flow to manage quarantined items with actionable remediation
and release.

Acceptance Criteria:

- UI lists quarantined items with reason and fix hints (sign/reduce caps/sandbox)
- Release action triggers integrator re-apply
- Events/Audit entries written for quarantine, escalate, release
- Minimal e2e or integration test covering flow

---

## 4) HMR swap + auto-rollback integration

Labels: phase:2, area:kernel, type:feature

Description:
Integrate hot module reload (HMR) with health-based auto-rollback and auditing.

Acceptance Criteria:

- Quiesce/swap/verify stages implemented
- On health drop, automatic rollback occurs and is audited
- Metrics for attempts, successes, rollbacks exposed
- Tests: unit for swap controller; simulated failure path triggers rollback

---

## 5) Night cycle deep checks

Labels: phase:2, area:maintenance, type:feature

Description:
Add nightly deep scans/tests during configured hours and emit artifacts.

Acceptance Criteria:

- Runs between configured hours
- Executes extended scans/tests; generates nightly summary artifact
- Ethics delta report generated and stored
- Tests for schedule window calc and report generation

---

## 6) CLI: aether selfinc {scan|plan|apply|rollback|audit}

Labels: phase:1, area:dx, type:feature

Description:
Introduce a CLI command group to manage the self-incorporation lifecycle.

Acceptance Criteria:

- Commands: scan, plan, apply, rollback, audit
- Each command has help text and examples
- Exit codes: 0 success; non-zero on failure
- Unit tests for command parsing and basic flows

---

## 7) Spec→Tests Gate in Integrator

Labels: phase:3, area:quality, type:feature

Description:
Enforce presence of tests for runtime-impacting self-incorporation changes during
integration.

Acceptance Criteria:

- Gate detects changes in integrator paths and requires tests present in PR
- Failing tests allowed during development, but gate blocks merge without tests
- Documentation for exemptions and overrides
- Unit test(s) for gate logic with sample diffs

---

## 8) Ethics & Audit Ledger (append-only)

Labels: phase:1, area:ethics, type:infra

Description:
Implement an append-only JSONL ledger for ethics/audit decisions.

Acceptance Criteria:

- 100% of quarantine/allow decisions produce a JSONL entry
- Entries link scans, signatures, capability diffs
- Provide a basic query tool (filter by date, action, component)
- Unit tests for writer and basic query

---

## 9) Hub policy alignment + tokens

Labels: phase:2, area:apis, type:feature

Description:
Ensure self-incorporation APIs align with Hub auth tokens/claims gating and propagate
policy in responses/streams.

Acceptance Criteria:

- Self-inc endpoints honor Hub’s token/claims gating
- Policy surfaced in headers/streams per chat contracts
- Tests for token gating and header propagation
- Docs updates for env flags and headers

---

## 10) Lyrixa panel: Self-Incorporation

Labels: phase:3, area:ui, type:feature

Description:
Add a Lyrixa UI panel to visualize self-incorporation status and actions.

Acceptance Criteria:

- Progress bar; risk pie; quarantine queue
- Recent HMR events; ethics profile switcher
- Live counts/metrics
- Snapshot tests or e2e smoke for the panel

---

## Release Notes (Template)

Title: Aetherra OS — Self-Incorporation v1

Summary:
A kernel-orchestrated system that sees, understands, and safely integrates 100% of its
codebase at boot and during operation. It includes a quarantine workflow, audit/ethics
ledger, strict security gates (.aether HMAC + plugin ed25519), and hot-swap/rollback
support. The result is a Self-Hosting Cognitive Organism: no dark code, continuous
evolution, safety by default.

Highlights:

- /api/selfinc/status + Prom metrics
- Strict mode gates for signatures and capabilities
- Quarantine → Escalate → Release workflow with UI hooks
- HMR swap with auto-rollback and audit
- Night cycle deep checks and ethics delta report
- New CLI: aether selfinc {scan|plan|apply|rollback|audit}
- Integrator Spec→Tests gate
- Ethics & Audit append-only ledger
- Hub policy alignment with tokens/claims
- Lyrixa Self-Incorporation panel

Upgrade Notes:

- New env flags: `AETHERRA_SELFINC_STRICT`, `AETHERRA_SELFINC_*` and
  `AETHERRA_PASSIVE_*` family
- Ensure policy bootstrap updated; re-run Bootstrap Policy Files task if needed

Compatibility:

- Backward compatible by default; strict mode is opt-in via env

Acknowledgements:

- Contributors and reviewers
