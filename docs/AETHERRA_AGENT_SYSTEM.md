# Aetherra Agent System

Updated: 2025-08-27

This document describes the Aetherra Agent System: the orchestrator and agent components responsible for coordinating specialized AI agents to execute tasks. It mirrors the structure of other system docs and reflects the current codebase.

## Purpose and scope

- Provide a multi-agent orchestration layer for planning and executing complex tasks
- Model tasks, capabilities, and policies; schedule work across agents with priorities
- Integrate with the AI Engine, Memory System, Kernel, and Hub for a cohesive OS experience

## At‑a‑glance status

- Orchestrator core: Implemented (AgentOrchestrator with graceful fallbacks)
- Agent registry: In-memory in orchestrator; integrates with broader Service Registry for discovery where available
- Task model: Basic task submission, priority, and status; sequential/parallel patterns available in stubs
- Policies and capabilities: Basic capability checks; Kernel capability enforcement recommended for critical ops
- Retries/timeout: Simple retry/timebox hooks; expand with Kernel backpressure for production
- Telemetry: Basic counters and status; expand via Hub/Prometheus exposure
- Engine integration: Implemented — `AetherraEngine.execute_task()` delegates to the orchestrator

### 1) Core components

Primary files:

- `Aetherra/aetherra_core/agents/agent_orchestrator.py` — production orchestrator module
- `Aetherra/aetherra_core/orchestration/agent_orchestrator.py` — alternate/bridge module (legacy)
- `Aetherra/aetherra_core/engine/aetherra_engine.py` — houses engine-facing hooks to the orchestrator
- `Aetherra/plugins/agent_components/agent_orchestrator.py` — plugin/agent components and examples

Responsibilities (AgentOrchestrator):

- Maintain a catalog of agents (id, description, capabilities, policies)
- Accept task submissions and plan execution across one or more agents
- Enforce basic capability/policy checks before routing tasks
- Track task status, results, and errors; surface telemetry

Key methods (representative):

- `register_agent(agent: AgentSpec) -> bool`
- `submit_task(task: dict, priority: str = "normal") -> str` (returns task_id)
- `get_task_status(task_id: str) -> dict`
- `execute(task: dict) -> dict` (internal plan/dispatch)

### 2) Agent interface

Agents implement a simple contract so the orchestrator can route work deterministically:

- `id: str` — stable identifier
- `capabilities: list[str]` — verbs/skills (e.g., "search", "write", "summarize")
- `handle_task(task: dict) -> Awaitable[dict]` — core async/sync entrypoint
- Optional: `estimate_cost(task) -> dict`, `plan_subtasks(task) -> list[dict]`

Basic policy context accompanies each call (budget/timebox/scope), and the Kernel’s capability gate should be consulted for risky operations.

### 3) Task lifecycle

1. Submit: Engine or user submits a task via `execute_task()` or directly to the orchestrator
2. Validate: Orchestrator checks shape, capability, and policy requirements
3. Plan: Select agent(s) and pattern (single, parallel, sequential)
4. Execute: Dispatch to agents, timebox and retry where configured
5. Collect: Aggregate outputs, store relevant artifacts/memories
6. Report: Update status and return final result to caller

Priorities: `"high" | "normal" | "background"` — align with Kernel queues when integrated.

Planner enhancements (planned):

- Hierarchical planning: automatically decompose large tasks into subtasks
- Dynamic agent selection: choose agents using context (memory, past success rate, specialization)
- Fallback routing: if agent A fails, route to agent B with equivalent capabilities

### 4) Coordination patterns

- Single-agent direct execution (default)
- Sequential multi-agent (pipeline)
- Parallel fan-out with aggregation (map/reduce-like)
- Debate/critique strategies (agents challenge each other’s outputs)
- Consensus mechanisms (weighted voting by confidence or track record)
- Role-based teams (planner → executor → verifier loop)
- Reflection/self-improvement loops (night cycle)

### 5) Small contract summary

- Task submission (input):
  - `{ task_name: str, task_data: dict, priority?: "high"|"normal"|"background", policy?: dict }`
- Task submission (output):
  - `{ task_id: str }`
- Task status (output):
  - `{ task_id: str, status: "pending"|"running"|"failed"|"completed", progress?: number, result?: dict, error?: string, updated_at: iso8601 }`
- Agent registration (input):
  - `{ id: str, capabilities: string[], description?: string, policy?: dict }`
- Agent execution (result):
  - `{ ok: boolean, output?: any, artifacts?: list, metrics?: dict }`

Error modes:

- No matching capability → reject with `error: capability_unavailable`
- Agent failure/timeout → retry (bounded), then mark failed
- Policy violation → reject with `error: forbidden`

### 6) Configuration and environment

The Agent System reuses repo-wide flags and Kernel controls; it does not add new env flags by default.

Relevant flags:

- `AETHERRA_QUIET=1` — reduce logs during smoke/tests
- `AETHERRA_PROFILE=test` — prefer deterministic behavior in mocks
- Kernel queue/backpressure flags for integration (see Kernel System doc)

### 7) Observability and metrics

- Orchestrator status: registered agents, in-flight tasks, completed/failed counts
- Per-agent telemetry: success rate, average latency, last error (where available)
- Engine hooks: `execute_task()` updates engine/session metrics
- Hub exposure: aggregate via Hub `/api/stats` or Kernel-promoted `/metrics` where integrated

Planned metrics:

- Per-priority queue depth; retries and timeouts; policy gate denials
- Task-level traces (agent sequence, durations, errors) with trace IDs

Enhanced telemetry (planned):

- Per-task end-to-end traces with IDs spanning planner and agents
- Confidence/quality scores per agent output
- Explainability hooks: why a particular agent/path was chosen; alternatives considered

### 8) Health and fault tolerance

- Timeboxing and bounded retries for agent calls
- Circuit breaker for repeatedly failing agents
- Graceful degradation: fallback agent or mock implementation when real agent unavailable
- DLQ/expiration when integrated with Kernel queueing

Resource management and quotas (planned):

- Per-agent budgets for CPU, memory, and network
- Adaptive throttling when agents misbehave or exceed error thresholds
- Tight Kernel backpressure integration so orchestrator queues can’t flood the system

### 9) Safety and policy

- Capability gates checked before executing tools or external actions
- Policy contexts include budgets (time/compute/network) and scopes (files, endpoints)
- Leverage Kernel security and rate-limits for network/file/process operations

Security extensions (planned):

- Per-agent capability sandboxing (fine-grained allow/deny for file/net/process)
- Policy plugins: externalized rules that operators can author and hot-reload

### 10) Extension points

- Add new agents by registering components that implement the agent interface
- Configure planners to choose agents/patterns based on task traits and policies
- Integrate Memory System to persist task context, artifacts, and reflections
- Connect to external tools via Plugins/Toolchains under capability enforcement

Agent memory integration (planned):

- Agent-specific episodic memory: each agent builds a profile of outputs, successes, and preferences
- Specialization over time: agents adapt to user style and task domains via their own memory

### 11) Known limitations and roadmap

- Planner is basic; add goal/plan reasoning and dependency graphs
- Limited telemetry; add structured traces and Prometheus metrics
- No first-class quotas; integrate budget-aware scheduling and Kernel backpressure fully

Roadmap phases:

1. Capability-aware planning with dependency graphs and retries
2. Rich telemetry and `/metrics` exposure of orchestrator stats
3. Quota/budget-aware scheduling, with Kernel integration and per-agent limits
4. Advanced multi-agent strategies (debate, critique, tool-use routing)
5. Evaluation harness for agent performance and nightly regression

### 12) Night cycle tie‑in

The orchestrator participates in the Kernel’s night cycle to run evaluations, refresh capabilities, and generate reflections. Typical jobs:

- Evaluate agent success rates and error clusters; auto-tune retries/timeouts
- Refresh memory indexes for agent-relevant domains
- Generate reflection memories from task outcomes

### 13) Agent evaluation

Establish a concrete evaluation harness to drive continuous improvement:

- Nightly benchmark suite with standard tasks per capability area
- Error clustering to identify recurring failures and propose fixes
- Meta-agent role that evaluates agents and recommends retraining/fine-tuning
- Regression tracking with thresholds; flag performance drops for investigation

### 14) Interfaces (implemented, opt-in)

The Agents API is implemented in the Hub and disabled by default. Enable via env flags and token guards.

Endpoints:

- `GET /api/agents` — orchestrator summary
- `GET /api/agents/metrics` — orchestrator metrics snapshot
- `POST /api/tasks` — submit task
- `GET /api/tasks/{id}` — task status/results
- `POST /api/tasks/{id}/stream` — SSE stream of task progress
- `POST /api/agents/evaluate` — run a lightweight evaluation harness
- `GET /api/agents/evaluation` — fetch last evaluation report

Environment flags:

- `AETHERRA_AGENTS_API_ENABLED=1`
- `AETHERRA_AGENTS_API_REQUIRE_TOKEN=1` and `AETHERRA_AGENTS_API_TOKEN=<token>` (recommended)
- `AETHERRA_AGENTS_API_STREAM=1` to enable SSE for task updates
- `AETHERRA_AGENTS_STREAM_POLL_MS=200` (optional poll interval)

Prometheus:

- `/metrics` now includes orchestrator gauges:
  - `aetherra_orchestrator_agents_total`
  - `aetherra_orchestrator_tasks_pending_total`
  - `aetherra_orchestrator_tasks_active`
  - `aetherra_orchestrator_tasks_pending{priority="<prio>"}`
  - `aetherra_orchestrator_tasks_total{status="<status>"}`
  - `aetherra_orchestrator_timeouts_total`, `aetherra_orchestrator_policy_denied_total`

API usage (quick examples):

1) List orchestrator summary

```http
GET /api/agents
Headers: X-Aetherra-Token: <token>
-> { ok: true, data: { orchestrator: { total_agents, pending_tasks, ... } } }
```

1) Submit a task, check status, and stream updates

```http
POST /api/tasks
Headers: X-Aetherra-Token: <token>
Body: { "name": "demo.task", "data": {"x":1}, "priority": "high" }
-> { ok: true, task_id: "t_123" }

GET /api/tasks/t_123
Headers: X-Aetherra-Token: <token>
-> { ok: true, status: { state, progress, ... } }

POST /api/tasks/t_123/stream
Headers: X-Aetherra-Token: <token>
-> text/event-stream: events "status", "token", zero-or-more "update", and final "final"
```

1) Evaluation harness

```http
POST /api/agents/evaluate
Headers: X-Aetherra-Token: <token>
Body: { "cases": [{"name": "eval.quick.status", "data": {}}], "timeout_sec": 3 }
-> { ok: true, report: { cases: [...], summary: { total, success, failed, avg_duration_sec, errors, wall_time_sec } } }

GET /api/agents/evaluation
Headers: X-Aetherra-Token: <token>
-> { ok: true, report: { ... } }
```

### References (code and docs)

- Orchestrator: `Aetherra/aetherra_core/agents/agent_orchestrator.py`
- Engine integration: `Aetherra/aetherra_core/engine/aetherra_engine.py`
- Plugin agent components: `Aetherra/plugins/agent_components/agent_orchestrator.py`
- Kernel System doc: `docs/AETHERRA_KERNEL_SYSTEM.md`
- AI System doc: `docs/AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md`

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

