<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

# Project Governance

The Aetherra project is stewarded by **Aetherra Labs**. Community contributors are welcome; stewardship ensures strategic coherence, legal compliance, and safety alignment.

## Roles

| Role                     | Responsibilities                                              | Appointment                          | Removal                                        |
| ------------------------ | ------------------------------------------------------------- | ------------------------------------ | ---------------------------------------------- |
| Stewards (Aetherra Labs) | Vision, roadmap arbitration, escalation decisions             | Designated by Labs                   | Labs decision                                  |
| Maintainers              | Merge PRs, review architecture changes, enforce quality gates | Steward nomination + 2 maintainer +1 | Majority of maintainers + steward ratification |
| Security Team            | Vulnerability intake, embargo handling, CVE coordination      | Steward delegation                   | Steward decision                               |
| Contributors             | Submit issues/PRs, improve docs, tests                        | Open participation                   | n/a                                            |

## Decision Model

1. Open discussion in Issues/Discussions/RFC.
2. Seek lazy consensus (silence ≥48h after summary = accept).
3. If contested → maintainers vote (simple majority).
4. If deadlock or cross-cutting risk → steward tie‑break; rationale documented.
5. Security / legal matters may proceed under private review; post-mortem summary published when safe.

## Technical Change Classes

| Class       | Examples                                  | Required Signals                 |
| ----------- | ----------------------------------------- | -------------------------------- |
| Patch       | Docs typo, non-behavioral refactor        | 1 maintainer review              |
| Minor       | New endpoint (non-breaking), new metrics  | 2 maintainer reviews             |
| Major       | Public API change, workflow grammar delta | 2 maintainers + steward sign-off |
| Exceptional | Cryptography, licensing, security posture | Steward explicit approval        |

## Release Process

1. All capability + quality gate tests green.
2. CHANGELOG entry authored & reviewed.
3. SPDX headers validated (tools/ check scripts).
4. Tag signed (GPG/SSH) by steward key.
5. Post-release: metrics baseline snapshot and upgrade notes published.

### Release Ownership & Signing Authority

The official release pipeline (tags, packaged artifacts, published wheels / containers, signed workflow bundles) is exclusively controlled by **Aetherra Labs**. Community automation (e.g. CI from forks) cannot publish or attach official artifacts.

| Aspect                        | Policy                                                                                                                                                                                                                                 |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Official Tags                 | Must be created & signed (GPG / SSH) by an Aetherra Labs steward key.                                                                                                                                                                  |
| Workflow (.aether) Signatures | In strict verification modes only signatures produced by registered Aetherra Labs signing keys are treated as "official"; community / third‑party signatures are accepted for execution only when explicitly allowed via policy flags. |
| Plugin / Script Admission     | New plugins or scripts must carry SPDX headers and (when marked official) a valid steward signature. Unsigned community code is sandboxed until reviewed.                                                                              |
| Key Management                | Steward keys are rotated on a minimum 12‑month cadence or immediately upon suspected compromise; retired keys are placed on a deny list.                                                                                               |
| Audit Logging                 | All release signing operations emit immutable audit log entries retained ≥ 24 months.                                                                                                                                                  |
| Reproducibility               | A release bill-of-materials (BOM) + hash manifest is generated and referenced in the CHANGELOG.                                                                                                                                        |

### Strict Mode Behavior

When strict modes are enabled (environment flag or policy configuration):

1. Only Aetherra Labs signing keys are accepted for: core workflow bundles, privileged plugin definitions, kernel / orchestrator extension modules.
2. Community-contributed artifacts must be explicitly whitelisted (hash + signature) post-review before activation.
3. Any unsigned or improperly attributed file touching execution surfaces (plugins, workflow specs, kernel hooks) triggers a policy violation and is quarantined.
4. Policy violations are surfaced as metrics and can fail CI gates.

### Community Contributions & Steward Sign-off

Contributions are welcomed under the following guardrails:

- All PRs require at least one maintainer review; "official" feature / component elevation additionally requires steward sign-off recorded in the PR discussion.
- Contributors may sign their commits; steward merge squash or rebase re-sign does not remove authorship attribution.
- Submitted plugins / scripts intended for distribution must include: SPDX headers, short security rationale (threat / misuse notes), and test coverage for any new capability exposure.
- Stewards reserve the right to reject, defer, or sandbox contributions that introduce unvalidated execution paths, network reach, or cryptographic primitives.

### Security System & Policy Enforcement

The security subsystem provides:

| Control                 | Description                                                                                          |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| Script & Plugin Signing | Validates cryptographic signature + timestamp + key trust tier.                                      |
| Policy Engine           | Enforces capability budgets, network / filesystem access rules, and signature requirements per mode. |
| Audit Trail             | Append-only log of load, activation, error, and escalation events (hash chained where supported).    |
| Quarantine              | Holds unreviewed or policy-violating artifacts; requires maintainer action to release.               |
| Metrics & Alerts        | Prometheus metrics + optional alert hooks for signature failures, policy denials, and key anomalies. |

Escalation path for security-signing incidents: Security Team triage → Maintainers notification → Steward decision (key revoke / emergency patch) → Post-mortem within 72h (public once safe).

## Stewardship Principles

1. Security & Safety First
2. Transparent Metrics Over Claims
3. Reproducibility Before Optimization
4. Public APIs Require Tests & Docs in Same PR
5. No Dark Features (all gated & documented)

## Changes to Governance

Proposed via PR to this file; requires steward approval after a 72h comment window (unless urgent for legal/security reasons).

---
For stewardship queries contact: [governance@aetherra.dev](mailto:governance@aetherra.dev)
