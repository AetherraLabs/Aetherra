# Aetherra OS • Architecture Map (v1.0)

> A professional, end‑to‑end map of Aetherra/Lyrixa as an AI‑native operating system: concepts → components → contracts → flows. Use this as the living source of truth for design reviews, onboarding, and roadmap planning.

---

## 0) Guiding Principles
- **Intelligence‑first OS**: thoughts/goals/memory as first‑class OS objects (not just files/processes).
- **Deterministic by default**: test profile, auditability, strict/verifiable artifacts.
- **Graceful degradation**: every subsystem fails safe; mocks and fallbacks preserve core flows.
- **Policy & safety baked in**: capability gates, signing, redaction, telemetry opt‑in.
- **Composable autonomy**: agents, plugins, and .aether orchestrate complex work under guardrails.

---

## 1) System at a Glance

```
+-----------------------------------------------------------------------+
|                                HUB                                    |
|  REST & SSE APIs: chat, agents, kernel, memory, trainer, metrics      |
+-------------------------+----------------------+----------------------+
                          |                      |
                    [Lyrixa UI/CLI]        [External Clients]
                          |
+-------------------------v---------------------------------------------+
|                              KERNEL                                   |
|  Priority queues • Heartbeats • Maintenance • Night cycle • HMR       |
|  Service Registry • Event Bus (KEB) • Module Manager (KLM)            |
+-------------------------+----------------------+----------------------+
           |               |                      |
           |               |                      |
   +-------v------+  +-----v------+        +------v------+
   |   ENGINE     |  |  PLUGINS   |        |  SECURITY   |
   | (Reason/RAG  |  | & TOOLCHAINS        |  (Policy,   |
   |  Conv/Tasks) |  |  (capabilities)     |  Signing)   |
   +-------+------+  +-----+------+        +------+------+
           |               |                       |
           |               |                       |
   +-------v---------------v-----------------------v-----+
   |                        MEMORY                        |
   |  Core (SQLite) • Advanced (fractal/concept/episodic) |
   |  Narratives/Reflections • QFAC & Quantum Bridge      |
   +------------------------------------------------------+
```

---

## 2) Core Layers & Responsibilities

### 2.1 Kernel System (OS Runtime)
- **Role**: Schedules and supervises all work; provides heartbeats, health, maintenance, and night cycle.
- **Queues**: `high`, `normal`, `background` with optional backpressure, TTL, DLQ.
- **Tasks**: `memory_query`, `plugin_invoke`, `aetherra_thought`, `hmr_*`.
- **Hot Module Reload (HMR)**: Prepare → Verify → Quiesce → Swap → Resume → (Rollback on failure).
- **Module Manager (KLM)** & **Event Bus (KEB)**: module lifecycle & pub/sub; metrics exposed via Hub.
- **Interfaces**: `start_kernel_loop()`, `add_task(...)`, `get_status()`.

**Outputs**: Kernel metrics snapshot, health broadcasts (`kernel.health`), persisted metrics file.

### 2.2 Aetherra Engine (AI Execution)
- **Role**: Coordinates conversation, reasoning, memory, plugin chains, and multi‑agent orchestration.
- **Conversation loop**: persist → recall → reason → synthesize → persist → metrics.
- **Task API**: `execute_task(name, data, priority)` delegates to Agent Orchestrator.
- **RAG**: planned first‑class retrieval pipeline; ephemeral scratchpad for protected reasoning traces.
- **Status**: Health/introspection surface for dashboards.

**Outputs**: Response payload `{ response, confidence, session_id, ... }`, task ids, system status.

### 2.3 Agent System (Multi‑Agent Orchestration)
- **Role**: Plans and executes tasks via registered agents under policy and capability checks.
- **Agent contract**: `id`, `capabilities[]`, `handle_task(task) -> result` (+ optional estimate/plan).
- **Patterns**: single, sequential pipeline, parallel fan‑out, debate/consensus, planner→executor→verifier.
- **Task lifecycle**: submit → validate → plan → execute → collect → report.
- **APIs** (Hub, opt‑in): list agents, submit task, status, SSE stream, evaluation harness.

**Outputs**: `{ task_id }`, status & metrics, artifacts, evaluation reports.

### 2.4 Memory System (Core + Advanced + Quantum)
- **Core (SQLite)**: async store/recall; conversation/project/preference/learning types; stats.
- **Advanced Orchestrator**: fractal fragments, concept clusters, episodic timelines, narratives, reflections, pulse/health.
- **QFAC & Quantum Bridge**: adaptive compression nodes, hybrid/quantum modes with deterministic shadow logs.
- **Privacy Classes**: `public|internal|sensitive`; anonymized previews and policy guards.
- **Determinism**: seeded embeddings and fixed timestamps in test profile.

**Outputs**: `MemoryRecallResult` (typed items + scores + metadata) and narrative/health summaries.

### 2.5 Chat System (Transport & Middleware)
- **Endpoints**: `/api/ai/ask`, `/api/ai/stream` (SSE), `/api/lyrixa/chat` bridge.
- **Pipeline**: safety filters → retrieval hooks (RAG) → scratchpad → confidence calibration.
- **Reliability**: queue limits, retries, circuit breakers, DLQ.

**Outputs**: `{ id, text, tokens, confidence, scratchpad? }`, streaming events (`token`, `thought`, `tool_call`, `safety_flag`, `done`).

### 2.6 Security System (Policy, Signing, Defense)
- **Secrets**: file+env store, optional encryption, rotation & leak checks.
- **Signing**: `.aether` HMAC signatures; plugin manifests with Ed25519 (strict mode optional).
- **Sandbox & Capabilities**: AST‑gated `safe_eval`, deny‑by‑default capability policy, network allow/deny with safe HTTP wrappers.
- **Prompt Defense**: heuristic scanner; high‑risk short‑circuits with alert.
- **Telemetry Privacy**: explicit opt‑in, redactions, optional DP noise; audit ledger for runs.

**Outputs**: alerts JSONL, audit logs, static risk reports, policy denials with reasons.

### 2.7 Coding System (Lyrixa Code Studio)
- **IDE‑grade**: planning, generation, diffs, refactors, lint/test/build, security checks.
- **Autonomy modes**: Assist → Co‑drive → Autopilot.
- **Spec→Tests Gate**: tests must be written before patches are applied.
- **Plugin authoring**: scaffolds, signing, permissions, live reload.

**Outputs**: minimal diffs, build/test/security reports, signed artifacts, PR/commit metadata.

### 2.8 Aether Script Language (`.aether` v1.1)
- **Nature**: declarative‑intent language orchestrating cognition, plugins, memory.
- **Core blocks**: `meta`, `policy`, `require`, `on_error`, `workflow`, `parallel/await`, `transaction`.
- **Built‑ins**: `reflect`, `summarize`, `store`, `detect_anomalies`, `run_plugin`, `metrics`, `trace`.
- **Contracts**: `plugin_contract` with version & schema verification; signatures at file header.
- **Determinism**: seeded behavior; strict verification via env flags or CLI.

**Outputs**: execution payload with `trace`, `transactions`, `policy`, `requires`.

---

## 3) Runtime Contracts (Canonical Shapes)

### 3.1 Conversation (Engine)
- **Input**: `{ message: string, context?: object }`
- **Output**: `{ response: string, session_id: string, confidence: number, reasoning?: string, memory_id: string, relevant_memories_count: number, timestamp: iso8601 }`

### 3.2 Task (Agent Orchestrator)
- **Submit**: `{ task_name: string, task_data: object, priority?: "high|normal|background", policy?: object } → { task_id }`
- **Status**: `{ task_id, status: "pending|running|failed|completed", progress?: number, result?: object, error?: string, updated_at: iso8601 }`

### 3.3 Memory Recall (Advanced)
- **Result**: `{ items: typed[], source: "core|conceptual|episodic|hybrid|qfac", scores: number[], metadata: object }`

### 3.4 Chat Stream (SSE)
- **Events**: `token`, `thought`, `tool_call`, `safety_flag`, `done` (JSON in `data:`).

---

## 4) Operational Flows

### 4.1 Boot (OS Launcher)
1. Initialize Service Registry
2. Load core systems (memory, plugins, engine, script service, scheduler, hub, self‑maintenance, Lyrixa chat, GUI hooks)
3. Start Kernel Loop (inject systems; register kernel)
4. Activate services (mark **HEALTHY**)
5. Validate health (heartbeat & metrics)
6. Announce **OS ONLINE** (write status; enqueue first thought)
7. Main loop (periodic checks; snapshots; metrics flush)

### 4.2 Night Cycle (Maintenance Window)
- Memory consolidation; narratives & reflections; plugin optimization.
- Engine regression/evaluation; cache warm‑starts; retries with backoff.
- Agent evaluation harness; tune retries/timeouts; refresh indexes.

### 4.3 HMR Lifecycle (Safe Reloads)
- Prepare shadow instance → Probe → Quiesce target (drain in‑flight) → Swap atomically → Resume → Rollback on error.

---

## 5) Observability & Telemetry
- **Metrics**: Kernel/Registry/Orchestrator/Chat/Memory/HMR counters & gauges via `/metrics`.
- **Status**: `/api/kernel/status`, `/api/kernel/metrics`, `/api/agents(/**)`, `/api/memory/status`, `/api/site_status`.
- **Logs**: audit ledger (`.jsonl`), security alerts, kernel metrics snapshot on shutdown.
- **Dashboards**: Hub exposes Prometheus‑friendly series; narrative/health summaries from Memory.

---

## 6) Configuration & Profiles (Essentials)
- **Deterministic test**: `AETHERRA_PROFILE=test`, `AETHERRA_DETERMINISTIC=1`, fixed timestamps/embeddings.
- **Strictness toggles**: `AETHERRA_SCRIPT_VERIFY_STRICT`, `AETHERRA_SIGNING_STRICT`, `AETHERRA_REQUIRE_CAPABILITIES`, `AETHERRA_NET_STRICT`.
- **Kernel**: queue sizes, rate limits, plugin timeouts, CB thresholds, retries, night window.
- **APIs**: `AETHERRA_AI_API_ENABLED`, `AETHERRA_AGENTS_API_ENABLED`, `*_REQUIRE_TOKEN`.
- **Memory**: `AETHERRA_QFAC_MODE=classical|hybrid|quantum`.

---

## 7) Security Posture (At a Glance)
- **Verify**: signed `.aether` + signed plugin manifests; static risk checks.
- **Isolate**: AST‑safe eval; capability gates; network policy.
- **Protect**: secrets vault; redaction; DP telemetry; audit trails.
- **Defend**: prompt‑injection scanner; high‑risk short‑circuit; alerts feed.

---

## 8) Roadmap Snapshot
- **Engine**: production LLM reasoning + tool‑use; integrated RAG with citations.
- **Chat**: richer streaming events; WebSocket transport; chat‑specific metrics.
- **Agents**: dependency graphs; quotas/budgets; advanced debate/consensus.
- **Trainer**: datasets → SFT/LoRA → eval harness → preference optimization → cloud/HF backends.
- **Security**: stronger isolation (containers/VMs/policy engine) for untrusted plugins.

---

## 9) Appendix — Quick Reference

### Key Endpoints
- Kernel: `/api/kernel/status`, `/api/kernel/metrics`
- Agents: `/api/agents`, `/api/tasks`, `/api/tasks/{id}/stream`
- Chat: `/api/ai/ask`, `/api/ai/stream`, `/api/lyrixa/chat`
- Memory: `/api/memory/status`, narratives/health via Hub
- Site status: `/api/site_status`, `/metrics`

### High‑Impact Env Vars
- `AETHERRA_HMR_ENABLED`, `AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC`, `AETHERRA_PLUGIN_MAX_CONCURRENCY`
- `AETHERRA_KERNEL_QSIZE_*`, `AETHERRA_KERNEL_DLQ`, `AETHERRA_KERNEL_RATE_LIMIT_PER_MIN`
- `AETHERRA_QFAC_MODE`, `AETHERRA_SCRIPT_VERIFY_STRICT`, `AETHERRA_SIGNING_STRICT`

---

### Usage
- Treat this map as the top‑level index. Each section mirrors the corresponding spec/doc and repository modules. Update alongside changes to contracts or behavior.


# 🌌 Aetherra OS Architecture Map (v1.1)

## 🔑 Core Principles

* **AI‑Native OS**: Manages thoughts, goals, memory, and agents — not just files and processes.
* **Quantum‑Enhanced Memory**: Observer‑aware, fractal compression, reproducible shadow logs.
* **Open & Extensible**: `.aether` workflows, plugin ecosystem, and transparent APIs.
* **Self‑Evolving**: Night cycle reflection, safe self‑repair, autonomous improvement.

---

## 🧩 Core Components

### 1. **Kernel Runtime**【79†source】

* **AetherraKernelLoop** — priority queues, heartbeats, retries, backpressure.
* **Night Cycle** — 02:00–04:00 deep reflection, cleanup, agent evaluation.
* **Hot Module Reload (HMR)** — safe swap, rollback, and audit logging.
* **KLM (Module Manager)** — module loads, rollbacks, and metrics.
* **KEB (Event Bus)** — pub/sub event flow with backlog metrics.
* **APIs** — `/api/kernel/status`, `/api/kernel/metrics`.

### 2. **AI Engine**【75†source】

* **AetherraEngine** — coordinates memory, reasoning, plugins, and agents.
* **Flows**: `process_message`, `execute_task`, `get_system_status`.
* **Reasoning**: RAG pipeline with provenance and evidence weighting.
* **Self‑Improvement**: Hooks for night cycle evaluation.
* **Developer APIs**: `/api/ai/ask`, `/api/ai/stream`.

### 3. **Agent System**【76†source】【80†source】

* **AgentOrchestrator** — registers agents, routes tasks, enforces capabilities.
* **Patterns**: single, sequential, parallel, debate, consensus.
* **Lifecycle**: submit → validate → plan → execute → report.
* **APIs**: `/api/agents`, `/api/tasks`, `/api/agents/evaluate`.
* **Telemetry**: per‑agent success rate, retries, failure clustering.

### 4. **Memory System**【78†source】

* **LyrixaMemorySystem (SQLite)** — conversations, projects, learning, preferences.
* **AetherraMemoryEngineAdvanced** — orchestrates fractal fragments, concept clusters, episodic timelines.
* **QFAC (Quantum Fractal Adaptive Compression)** — classical, hybrid, or quantum mode with quantum shadow logs.
* **Narratives**: daily/weekly/thematic summaries.
* **Pulse/Health**: coherence score, contradictions, drift, compression ratio.

### 5. **Chat System**【81†source】

* **Endpoints**: `/api/ai/ask`, `/api/ai/stream`, `/api/lyrixa/chat`.
* **Contracts**: `token`, `thought`, `tool_call`, `safety_flag`, `done`.
* **Safety**: filters, redactions, confidence calibration.
* **Backpressure**: queue limits, retries, DLQ.
* **Observability**: Prometheus metrics (`aetherra_chat_requests_total`, `latency_ms`).

### 6. **Security System**【83†source】

* **Script Signing**: `.aether` HMAC-SHA256.
* **Plugin Signing**: Ed25519 with revocation and transparency logs.
* **Secrets Management**: encrypted API key store with rotation.
* **Sandbox**: AST‑restricted eval + quotas.
* **Network Policy**: allow/deny lists + safe HTTP wrappers.
* **Prompt Defense**: heuristic injection scanner.
* **Audit**: static risk reports, security alerts feed.

### 7. **Coding System (Lyrixa Code Studio)**【84†source】

* **Autonomy Modes**: Assist → Co‑drive → Autopilot.
* **Spec→Tests Gate**: tests required before any patch.
* **Plugin Scaffold**: manifest, code, tests, signing.
* **Safety Gates**: lint/test/coverage/security enforced.
* **Audit Trail**: decisions, patches, metrics persisted.
* **Integration**: Git, test runners, security scanners.

### 8. **Trainer System**【82†source】

* **Planned**: trainer orchestrator, dataset manager, evaluation harness, model registry.
* **Techniques**: SFT, LoRA, DPO, alignment with safety filters.
* **Contracts**: `{ job_id, task, dataset, params }`.
* **APIs (planned)**: `/api/trainer/jobs`, `/api/trainer/evals`, `/metrics`.

### 9. **.aether Language v1.1**【77†source】

* **Core Blocks**: `goal`, `workflow`, `policy`, `require`, `on_error`, `plugin_contract`.
* **Semantics**: parallel/await, transactions, determinism profiles.
* **Observability**: `trace`, `metrics`, `narrate`.
* **Security**: signed scripts, capability gating.
* **Execution**: memory‑driven, agent‑aware orchestration.

---

## 📊 Role‑Based Ownership Matrix

| Role / Team              | Primary Ownership                                          | Supporting Systems |
| ------------------------ | ---------------------------------------------------------- | ------------------ |
| **Core Kernel Team**     | Kernel loop, Service Registry, HMR, KLM, KEB【79†source】  | Metrics, Hub       |
| **AI Engine Team**       | AetherraEngine, reasoning, RAG【75†source】                | Memory, Agents     |
| **Agent Orchestration**  | AgentOrchestrator, task lifecycle【76†source】             | Kernel, Engine     |
| **Memory Team**          | LyrixaMemorySystem, QFAC, Narratives【78†source】          | Security, Trainer  |
| **Chat & Interface**     | Chat System APIs, Lyrixa Bridge【81†source】               | Kernel, Security   |
| **Security Team**        | Script/plugin signing, sandbox, net policy【83†source】    | Kernel, Coding     |
| **Code Studio Team**     | Lyrixa Code Orchestrator, plugin scaffolding【84†source】  | Security, Agents   |
| **Trainer Team**         | Training orchestrator, datasets, eval harness【82†source】 | Memory, Security   |
| **Language Maintainers** | `.aether` grammar, compiler, verification【77†source】     | Engine, Coding     |
| **Ops & Reliability**    | Restart utils, config mgmt, observability【74†source】     | All subsystems     |

---

## 📚 Quick Reference

* **Endpoints**: `/api/ai/*`, `/api/agents/*`, `/api/memory/*`, `/api/kernel/*`, `/api/lyrixa/chat`, `/metrics`【85†source】
* **Env Flags**: `AETHERRA_PROFILE`, `AETHERRA_QFAC_MODE`, `AETHERRA_REQUIRE_CAPABILITIES`, `AETHERRA_HMR_ENABLED`, `AETHERRA_SCRIPT_VERIFY_STRICT`【85†source】
* **Night Cycle**: regression tests, memory reflection, agent evaluation【79†source】
* **Auditability**: security logs, audit ledger, quantum shadow logs【78†source】【83†source】

---

> ✅ This architecture map + ownership matrix provides a professional blueprint for engineering and ops teams to navigate Aetherra OS.

