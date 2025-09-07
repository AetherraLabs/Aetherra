<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

# Aetherra 0.5.0 Beta Roadmap & Community Focus

This document mirrors the pinned GitHub Discussion ("0.5.0 Beta Roadmap & Community Focus"). Comment in the Discussion for alignment before starting substantial work.

## 🎯 Core Goals (Beta)

| Pillar                    | Objective                                  | Success Signal                                       |
| ------------------------- | ------------------------------------------ | ---------------------------------------------------- |
| Stability & Quality Gates | Reduce flaky / non-deterministic behaviors | All gates green 3 consecutive runs                   |
| Observability / Metrics   | Close metric blind spots                   | No UNKNOWN in /api/health; doc patch coverage        |
| Security & Trust          | Harden signature & scan surfaces           | False-positive rate < 5%; add failing-signature test |
| Developer Experience      | Faster first contribution                  | Median setup <15m from clone                         |
| Plugins & Ecosystem       | Primitives for safe extension              | 1–2 exemplar minimal plugins documented              |
| Memory & Learning         | Introspectible memory graph health         | Graph consistency tests stable                       |
| Federation (Prep)         | Clarify trust & handshake model            | Published threat model draft                         |
| Docs & Guides             | Micro-guides for high-friction tasks       | 5 new task guides merged                             |

## 🧭 Suggested Low-Lift Contributions

| Area          | Starter Ideas                                       |
| ------------- | --------------------------------------------------- |
| stability     | Add snapshot replay regression test for X edge case |
| observability | Add metric for plugin activation count              |
| security      | Extend static scan ignore heuristics (document!)    |
| dx            | Script: validate environment & API keys in one step |
| plugins       | Example: memory inspector (read-only)               |
| memory        | Test verifying branch node count monotonicity       |
| docs          | "Add a metric in 60s" micro-guide                   |

## 🔍 Coordination Flow

1. Identify idea (issue or new)
2. Comment in Discussion thread with: scope, impact, test plan
3. Wait for lightweight ack (✅) from maintainer or two contributors
4. Open Draft PR early (label: `wip`)
5. Keep changes minimal & atomic

## 🧪 Definition of Done (Feature / Fix)

| Requirement                  | Notes                               |
| ---------------------------- | ----------------------------------- |
| Linked issue or roadmap item | Provide context & intent            |
| Tests updated/added          | Unless doc-only                     |
| Quality gates pass locally   | Run `python tools/quality_gates.py` |
| Documentation / comments     | Explain non-obvious logic           |
| No unrelated reformatting    | Keep diffs focused                  |

## 🛡 Security Coordination

- Security issues: NEVER open a public issue—use the security contact link.
- Pre-disclosure discussion (non-vuln hardening ideas) welcome in Discussions.

## 🗓 Indicative Timeline

- Week 0–1: Community alignment & low-hanging test/docs contributions
- Week 2–3: Plugin/example + metric coverage expansion
- Week 4: Federation threat model draft + polish / stabilization

## 📌 Tracking Table (Copy into Discussion Comment)

```markdown
### Proposal Summary
Area: (stability / observability / security / dx / plugins / memory / federation-prep / docs)
Title: <short>
Problem: <one-line>
Proposed Change: <1–3 lines>
Impact: <qualitative + any numbers>
Test Plan: <how will we know it works?>
Owner(s): @you
Status: idea | drafting | wip-pr | review | merged
```

## 🤝 Recognition

Meaningful roadmap-aligned contributions will be called out in release notes and future Hall of Fame.

---
Contribute intentionally. Small, well-tested improvements compound fast. 🚀
