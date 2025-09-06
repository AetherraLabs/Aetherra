<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
# Beta Milestone Planning (Draft)

## Objective

Consolidate remaining higher-assurance controls and feature depth to transition from experimental alpha to reliable beta platform.

## Thematic Buckets

| Theme         | Beta Goals                                                                         |
| ------------- | ---------------------------------------------------------------------------------- |
| Supply Chain  | Multi-sig release, provenance attestation, deny list enforcement                   |
| Isolation     | Plugin sandbox (subprocess or WASM), resource limits, timeout metrics              |
| Memory & Data | Encrypted at rest selectable stores, narrative enrichment pipeline                 |
| Evaluation    | Persistent eval store, dataset registry, differential coverage on PRs              |
| Governance    | Automated override prune merge suggestions, SPDX deny gate, risk review automation |
| Observability | Alerting hooks, structured audit log, sandbox metric series                        |

## Candidate Tasks

- Implement provenance attestation signer producing statement referencing integrity manifest.
- Add SPDX deny list env (`LICENSE_DENY`) enforced with failing gate.
- Introduce plugin execution sandbox with least-privilege file/network policy.
- Differential coverage report generation for modified lines.
- Encrypted memory backend (pluggable key provider abstraction).
- Multi-sig tag creation workflow (steward + build attestor signatures aggregated).
- Transparency log (append-only) for release manifests (Merkle root anchoring).
- Metrics: `plugin_timeout_total`, `sandbox_violations_total`, `license_deny_fail_total`.
- Risk automation: PR template auto-includes risk acceptance delta section.

## Success Criteria

- All Beta goals with status >= Implemented or In Review.
- Zero critical (P1) open security issues.
- Reproducibility verification documented and passes in CI.
- License deny list gate protecting against disallowed additions.

## Out of Scope (Beta)

- Full multi-tenant isolation (target GA).
- Advanced hardware offload for quantum memory accelerators.

---
Living draft; update as design discussions converge.
