# Aetherra 0.5.0-beta.0 Release Notes

Date: 2025-09-07
Tag: v0.5.0-beta.0
Status: Public Beta

## Highlights

* /api/health aggregate endpoint (kernel, registry, orchestrator, memory, chat)
* Expanded Prometheus metrics (coherence, orchestrator latency histogram, sandbox counters, per-agent gauges)
* Static security scan + memory fragmentation heuristic in quality gates
* Snapshot & replay harness (deterministic state verification)
* Stabilized fragmentation metric (warmup + retries)
* Quantum/memory fallback via ephemeral engine

## Install (Dev)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .[dev]
```

## Quickstart

```bash
export AETHERRA_AI_API_ENABLED=1
export AETHERRA_AI_API_STREAM=1
python aetherra_hub_server.py &
curl -X POST -H 'Content-Type: application/json' \
   http://localhost:3001/api/lyrixa/chat \
   -d '{"message":"hello beta"}'
curl http://localhost:3001/api/health
```

## Key Metrics (sample)

`aetherra_kernel_cycle_time_ms_bucket` · `aetherra_orchestrator_task_latency_ms_bucket` · `aetherra_memory_coherence_score` · `aetherra_chat_latency_ms_bucket` · `aetherra_agent_requests_total`

## Hardening

* Crash recovery & rehydration tests
* Placeholder password downgrade (static scan)
* Rolling histogram fallbacks (kernel/orchestrator)

## Breaking / Notes

* Trainer & federation advanced paths partial (some 501)
* Health ok keyed mainly on kernel running (memory absence soft)

## Upgrade

```bash
git pull origin main
pip install -e .[dev]
python tools/quality_gates.py
```

## Contribute Focus Areas

Persistent trainer storage · Federation signing handshake · Eval dataset registry · Narrative enrichment · Sandbox policy expansion

## Security

Report privately: [security@aetherralabs.org](mailto:security@aetherralabs.org) (see SECURITY.md)

## License

GPL-3.0-or-later — see LICENSE, NOTICE, LICENSE_POLICY.md

---
SPDX-License-Identifier: GPL-3.0-or-later
SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
