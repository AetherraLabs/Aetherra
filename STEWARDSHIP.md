<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

# Aetherra Stewardship Statement

This document clarifies that **Aetherra Labs** is the official steward of the Aetherra project, its language artifacts, and release process.

## Scope of Stewardship

| Area                          | Steward Responsibilities                      | Community Role             |
| ----------------------------- | --------------------------------------------- | -------------------------- |
| Roadmap & Vision              | Long-term direction, phase criteria           | Feedback / RFCs            |
| Releases                      | Versioning, signing, CHANGELOG integrity      | Validation & testing       |
| Security & Compliance         | Vulnerability intake, embargo handling        | Responsible disclosure     |
| Licensing & Policy            | SPDX integrity, license compatibility reviews | Raise incompatibilities    |
| Workflow Language (`.aether`) | Grammar evolution, signing format             | Proposal & experimentation |
| Metrics Stability             | Backward compatibility windows                | Early adoption feedback    |

## Attribution Standard

All new source files must include:

```text
SPDX-License-Identifier: GPL-3.0-or-later
SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
```

## Release Signing

Releases are considered official only if:

1. Tag is cryptographically signed with an Aetherra Labs steward key.
2. CHANGELOG entry matches repository state (hash check by tooling upcoming).
3. Quality gates (capabilities + metrics assertions) pass at tag time.

## Escalation Channels

| Topic                      | Contact                                                   |
| -------------------------- | --------------------------------------------------------- |
| Governance                 | [governance@aetherra.dev](mailto:governance@aetherra.dev) |
| Security / Vulnerabilities | [security@aetherra.dev](mailto:security@aetherra.dev)     |
| Licensing                  | [legal@aetherra.dev](mailto:legal@aetherra.dev)           |
| General Steward Queries    | [steward@aetherra.dev](mailto:steward@aetherra.dev)       |

## Trademark & Branding

"Aetherra" and related marks are stewarded by Aetherra Labs. Use is permitted in descriptive, nominative contexts. Do not misrepresent forks as official distributions.

## Change Control

Stewardship modifications require: PR + 72h public comment + steward approval.

---
For clarifications open a discussion with the `stewardship` label.
