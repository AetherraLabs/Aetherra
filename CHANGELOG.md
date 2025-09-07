# Changelog

## [Unreleased]

### Planned

* Documentation expansion for new observability endpoints (`/api/health`, memory/kernel metrics breakdown)
* Persistent trainer/eval storage backend (post‑beta)
* Federation secure peer handshake & signing enforcement
* Enhanced evaluation metrics & dataset registry
* Extended sandbox policy surfaces (syscall / resource limits) and deterministic replay signage

---

## 0.5.0-beta.0 (2025-09-07)

Stabilization & Observability Beta. Focus: security tooling integration, fragmentation resilience, health & metrics surfaces.

### Highlights

* New `/api/health` aggregate endpoint (kernel, registry, orchestrator, memory, chat) for probes & dashboards.
* Enhanced Prometheus exporter now includes memory coherence & branch metrics, orchestrator histograms, per-agent gauges, sandbox counters.
* Static security scanner + memory fragmentation heuristic integrated into `quality_gates.py` (configurable env thresholds).
* Snapshot & replay harness enables deterministic service + memory state verification.
* Password placeholder false-positive downgrade in static scan reduces noise in pipelines.
* Quantum / memory coherence status & audit endpoints hardened with fallback ephemeral engine.
* CHANGELOG normalization and README version / badges updated to Beta lineage.

### Hardening & Resilience

* Memory fragmentation metric stabilized (warmup + retries, protected against zero‑trace baselines on Windows).
* Crash recovery tests extended to cover service rehydration & dependency resolution.
* Sandbox safe_eval allow‑list refined; deterministic profile harness for QRNG simulation outputs.

### Tooling

* `tools/static_security_scan.py` produces JSON/Markdown, gating on critical findings.
* `tools/memory_fragmentation_metrics.py` exposes fragmentation heuristic consumed by quality gates.
* `tools/snapshot_replay_harness.py` supports state snapshotting & replay integrity tests.

### Metrics Additions

* Memory: coherence score, branches, fragments, entanglement nodes, per‑branch node/edge gauges (cardinality‑capped).
* Orchestrator: latency histogram (fallback rolling), task status/priority breakdown, coherence policy gauges.
* Kernel: histogram fallback with rolling accumulation when live histogram absent.
* Chat: latency + TTFT histograms, per‑principal stream gauges.

### Breaking / Behavioral Notes

* Trainer & federation advanced paths remain stub/incomplete (501 responses) – preserved intentionally for staged hardening.
* Health endpoint `ok` flag currently keyed primarily off kernel running state (memory absence is soft). Future versions may broaden criteria.

### Upgrade Guide

1. Run `pip install -e .[dev]` to refresh local editable install (version bump to 0.5.0-beta.0).
2. Optional: enable gates `STATIC_SECURITY_SCAN=1` and `FRAGMENTATION_CHECK=1` before invoking `python tools/quality_gates.py`.
3. Probe new health and metrics surfaces:
	* `curl http://localhost:3001/api/health`
	* `curl http://localhost:3001/metrics | grep aetherra_memory`

---

### Stability & Safety Additions

* Reflection memory stability capability test (bounded buffers + heap growth heuristic)
* Crash recovery simulation for `LyrixaMemorySystem` persistence
* Extended crash recovery & service rehydration test (memory + registry restart + dependency resolution + broadcast sanity)
* Security sandbox placeholder test (safe_eval restrictions, timeout, memory budget hook) with refined builtin allow‑list
* Deterministic profile harness validating QRNG deterministic outputs under test / simulator modes
* Snapshot & replay harness (`tools/snapshot_replay_harness.py`) capturing service registry + memory stats with replay integrity test
* Static security scan tool (`tools/static_security_scan.py`) producing JSON/Markdown reports; capability test ensures no critical findings
* Memory fragmentation heuristic metrics (`tools/memory_fragmentation_metrics.py`) with retry‑hardened baseline capture to reduce flakiness

### Runtime & API Adjustments

* Added `close()`, context manager support, and GC finalizer to `LyrixaMemorySystem` (Windows SQLite handle cleanup)
* `safe_eval` now permits whitelisted builtin calls (`abs`, `min`, `max`, `sum`, `len`, `range`)
* Normalized `MemoryCore.store` return shape when legacy engine pathway returns `bool`
* Hardened memory fragmentation measurement (warmup + retries) eliminating intermittent zero‑trace baseline on Windows CI

### Internal Tooling

* Extended capability suite now covering recovery + determinism safety claims
* New capability tests: snapshot replay round‑trip, static security scan baseline, memory fragmentation heuristic
* Quality gates groundwork: planned integration of static security scan & fragmentation heuristic (no critical secrets; bounded delta)
* Static security scanner password placeholder downgrade logic (avoids false positives for obvious placeholders/redactions)

### Planned Next (Not Yet Implemented)

* Integrate static security scan + fragmentation thresholds directly into `quality_gates.py` (fail on new critical secrets or pathological fragmentation delta)
* Documentation updates describing new resilience & security tooling (snapshot harness, scanner, fragmentation heuristic)
* CHANGELOG normalization pass (deduplicate legacy trailing sections fully) once gates integration merged
* Optional cryptographic signing of runtime snapshots for tamper detection

## 0.2.0-beta.0 (2025-09-07)

Highlights (First Public Beta):

* Full capability test suite expanded to 32 passing tests (chat, hub metrics, memory, ownership, plugin lifecycle, quantum optional path, self‑maintenance services).
* Added automated plugin reload lifecycle test ensuring clean unregister → re-register with state isolation.
* Advanced diagnostics enhancements: adaptive PASS logic when external OS / Hub provides services; capability reinforcement hook `_ensure_full_capabilities()` integrated.
* Plugin System Documentation (`docs/AETHERRA_PLUGIN_SYSTEM.md`) detailing architecture, lifecycle, and future registry model.
* Memory & Intelligence hardening: persistent memory initialization stability, rate-limited provider & memory error logging, capability flags auto-reinforced at runtime.
* Model alias normalization and multi-provider orchestration resilience (graceful OpenAI/Anthropic fallback + local stub provider).
* Beta Readiness Report (`BETA_READINESS_REPORT.md`) added summarizing health evidence and risks.
* Signed workflow support validated across sample demos; groundwork for future marketplace / registry.

Breaking / Behavioral Notes:

* Some alpha trainer & federation endpoints remain partially stubbed (returning 501) – preserved intentionally; stabilization deferred to post‑beta minor releases.
* Chat upstream provider quota/billing failures surface as logged warnings/errors but do not abort fallback responses.

<!-- Cleaned duplicate legacy sections above; canonical changelog retained below. -->

### Governance & Compliance

* Extended overrides YAML normalized (tabs removed) to ensure parser reliability in gates.

### Internal

* Feature branch `feat/federation-signing-telemetry` merged and deleted after integration.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

## 0.1.0-alpha.1 (2025-09-05)

Initial public alpha snapshot.

### Added

* Hub trainer + eval scaffolding with in-memory jobs/evals and metrics (`aetherra_trainer_*`).
* Memory narratives endpoints (`/api/memory/narratives`, `/memory/narratives`).
* Expanded Prometheus metrics: per-principal stream gauges, quantum + observer/coherence signals, trainer series.
* Docs consistency automation and project overview inventory of env flags and endpoints.

### Hardening

* Safety redaction & policy snapshot headers.
* Differential privacy flags surfaced in policy snapshot.
* Idempotency cache for chat endpoints.

### Limitations (Alpha)

* Trainer/eval state is in-memory only (not persisted).
* Upstream model providers may fallback to mock engines silently when unavailable.
* Federation endpoints partially stubbed (501 on announce/sync without optional deps).
* Evaluation scoring simulated (deterministic placeholder scores).
* Quantum hardware provider mode optional; defaults to simulator pathway.

### Next

* Persistent trainer/eval storage, cancellation, retry.
* Enhanced federation peer sync and secure signing enforcement.
* Pluggable evaluation metrics and dataset registry.
* Hardened coverage for disabled feature paths (partially added in this release).

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
* Memory narratives endpoints (`/api/memory/narratives`, `/memory/narratives`).
* Expanded Prometheus metrics: per-principal stream gauges, quantum + observer/coherence signals, trainer series.
* Docs consistency automation and project overview inventory of env flags and endpoints.

Hardening:

* Safety redaction & policy snapshot headers.
* Differential privacy flags surfaced in policy snapshot.
* Idempotency cache for chat endpoints.

Limitations (Alpha):

* Trainer/eval state is in-memory only (not persisted).
* Upstream model providers may fallback to mock engines silently when unavailable.
* Federation endpoints partially stubbed (501 on announce/sync without optional deps).
* Evaluation scoring simulated (deterministic placeholder scores).
* Quantum hardware provider mode optional; defaults to simulator pathway.

Next:

* Persistent trainer/eval storage, cancellation, retry.
* Enhanced federation peer sync and secure signing enforcement.
* Pluggable evaluation metrics and dataset registry.
* Hardened coverage for disabled feature paths (partially added in this release).

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
