# Alpha Readiness & Usage Guide

Version: 0.1.0-alpha.2
Date: 2025-09-06

This document captures the scope, constraints, and safe operational defaults for the Aetherra alpha release.

## Goals
- Provide early access to Hub APIs (chat, memory narratives, trainer/eval scaffolding, metrics).
- Gather feedback on observability & policy surfaces before persistence and scaling layers land.

## Safe Defaults
| Capability       | Env Flag                      | Default         | Recommendation                 |
| ---------------- | ----------------------------- | --------------- | ------------------------------ |
| Chat (sync)      | AETHERRA_AI_API_ENABLED       | 0               | Enable only with token gating  |
| Chat streaming   | AETHERRA_AI_API_STREAM        | 0               | Keep off unless testing SSE/WS |
| Require token    | AETHERRA_AI_API_REQUIRE_TOKEN | 1 (recommended) | Always set in shared envs      |
| WebSocket stream | AETHERRA_AI_API_WS            | 0               | Experimental                   |
| Trainer/Eval     | AETHERRA_TRAINER_ENABLED      | 0               | Enable per session only        |
| Federation       | AETHERRA_HUB_SKIP_OPTIONALS   | 1               | Set 0 only if deps installed   |
| Security ledger  | AETHERRA_SECURITY_LEDGER      | 1               | Disable only in hermetic CI    |

## Key Endpoints (Alpha)
| Endpoint                 | Notes                                                              |
| ------------------------ | ------------------------------------------------------------------ |
| /metrics                 | Prometheus text; includes trainer, quantum, coherence, chat series |
| /api/trainer/status      | Shows enabled + counts                                             |
| /api/trainer/jobs /evals | In-memory; simulated progression                                   |
| /api/memory/narratives   | Narrative memory stub list                                         |
| /api/ai/ask /stream      | Disabled by default unless explicitly enabled                      |

## Limitations
- Trainer/eval jobs are not persisted across process restarts.
- Quantum provider hardware integration is optional and may return simulator metadata.
- Federation peer operations return 501 unless optional modules installed.
- Evaluation scoring is deterministic placeholder (0.9) pending real metrics.
- No RBAC / multi-tenant isolation yet; treat instance as single-tenant.

## Quick Start
```powershell
$env:AETHERRA_AI_API_REQUIRE_TOKEN='1'
$env:AETHERRA_HUB_SKIP_OPTIONALS='1'
python aetherra_hub_server.py
# In another shell (enable trainer transiently)
$env:AETHERRA_TRAINER_ENABLED='1'
python - <<'PY'
import requests, time
port=3001
r=requests.post(f'http://localhost:{port}/api/trainer/jobs', json={'task':'sft'})
print(r.json())
time.sleep(1)
print(requests.get(f'http://localhost:{port}/api/trainer/jobs').json())
print(requests.get(f'http://localhost:{port}/metrics').text.splitlines()[:15])
PY
```

## Feedback
Open issues with label `alpha-feedback` describing: scenario, expected vs actual, logs/metrics snippet.

## Road to Beta
- Persisted trainer/eval store + cancellation
- Secure federation handshake & signing enforcement
- Expanded evaluation metric registry & dataset catalog
- Memory narratives enrichment & query parameters
- Policy-driven tool execution sandboxing

---
© 2025 Aetherra & Lyrixa Contributors

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
