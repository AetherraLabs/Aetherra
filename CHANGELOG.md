## Changelog

### 0.1.0-alpha.1 (2025-09-05)

Initial public alpha snapshot.

Added:
- Hub trainer + eval scaffolding with in-memory jobs/evals and metrics (`aetherra_trainer_*`).
- Memory narratives endpoints (`/api/memory/narratives`, `/memory/narratives`).
- Expanded Prometheus metrics: per-principal stream gauges, quantum + observer/coherence signals, trainer series.
- Docs consistency automation and project overview inventory of env flags and endpoints.

Hardening:
- Safety redaction & policy snapshot headers.
- Differential privacy flags surfaced in policy snapshot.
- Idempotency cache for chat endpoints.

Limitations (Alpha):
- Trainer/eval state is in-memory only (not persisted).
- Upstream model providers may fallback to mock engines silently when unavailable.
- Federation endpoints partially stubbed (501 on announce/sync without optional deps).
- Evaluation scoring simulated (deterministic placeholder scores).
- Quantum hardware provider mode optional; defaults to simulator pathway.

Next:
- Persistent trainer/eval storage, cancellation, retry.
- Enhanced federation peer sync and secure signing enforcement.
- Pluggable evaluation metrics and dataset registry.
- Hardened coverage for disabled feature paths (partially added in this release).

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
