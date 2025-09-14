# Aetherra Labs — Living Roadmap
_Last updated: 2025-08-11 23:01 UTC_

This roadmap consolidates current plans across the OS, Lyrixa, memory/cognition, plugins, and developer experience. It’s designed to be **edited in PRs** and reflected on the website. Keep language clear and concrete (avoid hype such as “world’s first”).

---

## How to use this document
- Treat each **Epic** as a tracked initiative with a clear **Outcome**, **Milestones**, **Owner**, **Due**, and **Status**.
- Update **Status** weekly: `Planned → Active → Blocked → Done`.
- Attach issue/PR links next to milestones. Add measurements to the **Scorecard** as they roll in.
- Keep the **Changelog** at the bottom updated in every PR that changes scope or dates.

> **Legend**: 🟢 Active · 🟡 Planned · 🔴 Blocked · ✅ Done

---

## Release train snapshot
- **Current window:** Aug–Oct 2025
- **Next window:** Nov 2025–Jan 2026
- **Cadence:** Monthly minor releases; quarterly feature rollups

---

## Workstream A — Memory & Cognition (Product‑critical)

### Epic A1 — Narrative & Reflective Memory in UI 🟡 Planned
**Outcome**: Users can view daily/weekly stories with causal chains and quality scoring; integrates with Lyrixa.
- [ ] UI: Memory Story panel + timeline view
- [ ] Causality markers (cause→effect edges) visible
- [ ] Story quality/coherence scoring surfaced
- **Owner**: _TBD_ · **Due**: 2025‑09‑30 · **Status**: Planned
- **Metric targets**: Narrative quality scoring enabled in UI; >70% user rating on clarity

### Epic A2 — Performance & Scaling 🟢 Active
**Outcome**: <200ms average recall under representative load; safe migrations + recovery.
- [ ] FAISS or equivalent index for vector search
- [ ] Lazy loading & background enrichment
- [ ] Backups + recovery runbook
- [ ] Bench harness in CI (p50/p95)
- **Owner**: _TBD_ · **Due**: 2025‑09‑15 · **Status**: Active
- **Metric targets**: Recall p50 < 120ms · p95 < 250ms

### Epic A3 — Curiosity + Conflict (Night Cycle) 🟡 Planned
**Outcome**: Contradiction detection, gap‑driven questions, and safe shadow‑state exploration during night cycles.
- [ ] Contradiction detector integrated with concept graph
- [ ] Question generator + prioritization
- [ ] Shadow‑state forks; validation gates; rollback
- **Owner**: _TBD_ · **Due**: 2025‑10‑15 · **Status**: Planned
- **Metric targets**: >80% conflict resolution in tests

---

## Workstream B — Assistant Core & Autonomy

### Epic B1 — Self‑Correction Engine 🟢 Active
**Outcome**: Plugin errors are diagnosed, fix candidates proposed, and applied with confirmation; learns from patterns.
- [ ] Real‑time error monitor
- [ ] LLM‑guided diagnosis + patch generation
- [ ] “Apply fix” flow with diff preview
- [ ] Pattern memory to reduce recurrence
- **Owner**: _TBD_ · **Due**: 2025‑09‑30 · **Status**: Active
- **Metric targets**: ≥95% plugin execution success

### Epic B2 — Background Agents & Coordinator 🟡 Planned
**Outcome**: Planner, MemoryAnalyzer, BugHunter, Performance agents run concurrently with task scheduler.
- [ ] Agent lifecycle + IPC protocol
- [ ] Task scheduler with priorities
- [ ] Coordination + conflict resolution
- **Owner**: _TBD_ · **Due**: 2025‑11‑15 · **Status**: Planned
- **Metric targets**: ≥3 agents active; ≥70% automated task completion

### Epic B3 — Permissions & Audit 🟡 Planned
**Outcome**: Granular permissions; confirmations for sensitive ops; audit trail.
- [ ] Permission schema + prompts
- [ ] Sandbox for untrusted code
- [ ] Structured audit logs
- **Owner**: _TBD_ · **Due**: 2025‑10‑31 · **Status**: Planned
- **Metric targets**: Zero critical vulns in quarterly review

---

## Workstream C — Plugin Ecosystem & Registry

### Epic C1 — Registry MVP (API + Web) 🟢 Active
**Outcome**: Submit, validate, search, and rate plugins; security levels; scanning.
- [ ] REST API + auth
- [ ] Submission + validation pipeline
- [ ] Search & discovery UI
- [ ] Security scanner + trust tiers
- **Owner**: _TBD_ · **Due**: 2025‑09‑30 · **Status**: Active
- **Metric targets**: API p50 < 200ms; 100% scan coverage

### Epic C2 — DX & Official Plugins 🟡 Planned
**Outcome**: Scaffolds, tests, docs generator; 20+ official plugins.
- [ ] `create-aetherra-plugin` scaffold
- [ ] Test harness + CI template
- [ ] Docs generator from manifests
- [ ] 20 official plugins published
- **Owner**: _TBD_ · **Due**: 2025‑10‑31 · **Status**: Planned
- **Metric targets**: 4.5★ average rating; >100 community downloads

### Epic C3 — Community Programs 🟡 Planned
**Outcome**: Bounties, mentorship, recognition.
- [ ] Bounty board + starter issues
- [ ] Mentorship signups
- [ ] Monthly demo day
- **Owner**: _TBD_ · **Due**: 2025‑11‑30 · **Status**: Planned
- **Metric targets**: 50+ active plugin devs

---

## Workstream D — UX & Docs

### Epic D1 — Memory Timeline & Layout 🟡 Planned
**Outcome**: Interactive timeline, saved layouts, status indicators.
- [ ] Cluster view + click‑to‑recall
- [ ] Panel layout presets
- [ ] Live status strip
- **Owner**: _TBD_ · **Due**: 2025‑09‑30 · **Status**: Planned
- **Metric targets**: >60% timeline engagement

### Epic D2 — Task “Recipes” & Tutorials 🟡 Planned
**Outcome**: Docs tied to console/playground with runnable examples.
- [ ] 12 task recipes
- [ ] Playground deep links
- [ ] Success telemetry
- **Owner**: _TBD_ · **Due**: 2025‑10‑15 · **Status**: Planned
- **Metric targets**: Reduced time‑to‑first‑success

---

## Medium‑term (Nov 2025 → Jun 2026)

### Epic E1 — IDE Integrations (VS Code, JetBrains) 🟡 Planned
- [ ] Context‑aware chat & inline actions
- [ ] Project‑wide analysis & refactors
- **Owner**: _TBD_ · **Due**: 2026‑03‑31 · **Metric**: 10k installs

### Epic E2 — Universal Language Bridge 🟡 Planned
- [ ] Python/JS/Rust/Go interop flows
- [ ] Cross‑stack performance advisor
- **Owner**: _TBD_ · **Due**: 2026‑06‑30 · **Metric**: End‑to‑end demo apps

### Epic E3 — Marketplace v2 🟡 Planned
- [ ] In‑app installer; ratings/reviews
- [ ] Verification + version mgmt
- **Owner**: _TBD_ · **Due**: 2026‑04‑30

---

## Long‑term (H2 2026 → 2027)

### Epic F1 — Autonomous Maintenance 🟡 Planned
- Diagnose → simulate → test → gated deploy; confidence thresholds; rollback.
- **Metric**: MTTR ↓; successful auto‑remediations tracked

### Epic F2 — Self‑Tuning & Shared Learning 🟡 Planned
- Behavior optimization from usage patterns; optional shared best‑practice propagation.
- **Metric**: measurable productivity/latency gains

---

## Dependencies & sequencing
1. **A2 Performance** precedes **A1 Narrative UI** and **B2 Agents**.
2. **C1 Registry** precedes **C2 Official plugins** and **E3 Marketplace v2**.
3. **B3 Permissions** precedes autonomous features in **F1**.

---

## Scorecard (update monthly)
- Memory recall p50: _TBD_ ms · p95: _TBD_ ms
- Narrative quality score (human eval): _TBD_
- Plugin execution success: _TBD_%
- Agents concurrently active: _TBD_
- Registry uptime: _TBD_% · API p50: _TBD_ ms
- Timeline engagement: _TBD_%
- Security: Critical vulns this quarter: _0/TBD_

---

## Risk register (rolling)
- **Scaling of memory graph** — Mitigate with sharding/lazy edges.
- **Integration complexity** — Stage rollouts; feature flags; fallbacks.
- **API costs** — Prefer local models + caching.
- **Security** — Sandbox untrusted plugins; strict permissions; audits.

---

## Links
- Product site & docs: _link_
- Bench harness dashboard: _link_
- Plugin registry: _link_
- Community/Contributing: _link_

---

## Changelog
- 2025-08-11 — Initial living roadmap created; merged near‑term and medium/long‑term tracks; added scorecard & risk register.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

