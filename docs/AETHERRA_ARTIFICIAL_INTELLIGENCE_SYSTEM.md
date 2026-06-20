# Aetherra Artificial Intelligence System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2026-06-20

This document describes the Aetherra Artificial Intelligence System: the core AI engine, its subsystems, contracts, observability, and extension points. It mirrors the structure of other system docs and is grounded in the current codebase.

## Purpose and scope

- Provide the main AI execution engine that coordinates reasoning, memory, improvement, plugins/tooling, and agent orchestration
- Offer a simple conversational interface and task execution entrypoints
- Expose health/status for dashboards and integrate with the OS Kernel and Hub

## At‑a‑glance status

- System status: Functional foundation complete
- Engine core: Implemented (AetherraEngine)
- Memory integration: Implemented (async core memory APIs with graceful mock fallback)
- Reasoning: Basic mock; placeholder for production LLM/tool-augmented reasoning
- Self‑improvement: Basic mock cycle and metrics hooks
- Plugin/tool chains: Basic mock executor wiring
- Agent orchestration: Basic mock orchestration with task submit/status
- Introspection/health: Implemented with graceful fallback
- Conversational loop: Implemented (store/recall + response synthesis)
- Developer AI HTTP APIs: Implemented (opt-in) — /api/ai/ask (JSON), /api/ai/stream (SSE)

## Functional foundation completion

The Artificial Intelligence System is functionally foundation complete for the
current Aetherra milestone. The completed foundation is not "full autonomous
intelligence" or final LLM-backed reasoning. It is a bounded AI engine contract
with message processing, memory handoff, basic reasoning, task submission,
Guardian-protected task execution, graceful component degradation, metrics, and
read-only readiness reporting.

This foundation is safe for alpha preparation because risky execution authority
remains outside the AI engine. The AI engine can process messages and submit
tasks through guarded paths, but Guardian, Security, Kernel, Memory,
Self-Improvement, Self-Incorporation, and Maintenance retain their own
authority.

New Hub status surface:

- `GET /api/ai/status` reports AI engine readiness, component state, safety
  signals, session metrics, and authority boundaries.

### Understanding Rule

What it does:

- Provides the core AI engine entrypoint for message processing and task
  submission.
- Builds reasoning context from conversation state and memory recall.
- Produces bounded response payloads with confidence and session metrics.
- Submits AI tasks to the agent orchestrator through Guardian-audited controls.
- Exposes `GET /api/ai/status` for read-only readiness and authority reporting.

Why it exists:

- Aetherra needs one central AI processing layer that coordinates reasoning,
  memory, agents, tools, and improvement signals without giving any one feature
  unchecked authority.
- The AI system gives Hub, Lyrixa, agents, and future clients a stable engine
  contract while the deeper model/tool/RAG layers continue to evolve.

Authority it owns:

- AI message processing.
- Reasoning context construction.
- Conversation memory handoff.
- AI task submission to agent orchestration.
- AI subsystem status and readiness reporting.

Authority it does not own:

- Guardian approval decisions.
- Security capability, sandbox, signing, or network policy.
- Kernel scheduling or lifecycle control.
- Memory persistence policy and storage authority.
- Self-Improvement proposal approval.
- Self-Incorporation execution.
- Chat transport policy and client-facing routing.

How it fails:

- If the engine is not registered or unavailable, `/api/ai/status` reports
  `offline` and Hub AI request routes return bounded offline/disabled responses.
- If required status fields or required components are unavailable, readiness
  reports `blocked`.
- If components are present but degraded or inactive, readiness reports
  `degraded` and clients should avoid treating AI output as fully reliable.
- If Guardian denies a task submission, the task is not submitted and no active
  task record is created.
- If memory or reasoning operations fail during message processing, the engine
  falls back to conservative error handling rather than granting new authority.

How it interacts with other systems:

- Hub exposes opt-in AI request/stream routes and the read-only AI status route.
- Guardian reviews AI task execution intents before agent orchestration.
- Security supplies capability and policy enforcement expectations.
- Memory supplies recall and persistence when available.
- Agent System receives approved AI task submissions.
- Kernel and Hub surface AI status and metrics for operators.

### 1) AetherraEngine

File: `Aetherra/aetherra_core/engine/aetherra_engine.py`

Responsibilities:

- Coordinate subsystems: memory, reasoning, self‑improvement, plugin chain executor, agent orchestrator, introspection
- Provide high‑level flows: initialize/shutdown, start conversation, process message, execute task, report status

Key methods (selected):

- `initialize()` / `shutdown()`
- `start_conversation(user_id="default") -> str`
- `process_message(message: str, context: Optional[dict]) -> dict`
- `execute_task(task_name: str, task_data: dict, priority: str = "normal") -> str`
- `get_system_status() -> dict`
- `get_conversation_summary() -> dict`

Subsystems (with graceful mock fallbacks when modules are absent):

- Memory: `AetherraMemorySystem` (async store/recall, stats, learning)
- Reasoning: `ReasoningEngine` (async `reason(context)`)
- Self‑improvement: `SelfImprovementEngine` (cycle control, metrics)
- Plugin Chains: `PluginChainExecutor` (tool sequencing)
- Agent Orchestration: `AgentOrchestrator` (submit tasks, status, orchestrate)
- Introspection: `IntrospectionController` (component health monitoring)

### 2) Conversational flow

1. Ensure session (auto‑starts if missing)
2. Persist user message to memory (conversation type, tags)
3. Recall recent/conversational memories
4. Build a reasoning context and call `ReasoningEngine.reason()`
5. Synthesize an assistant response (placeholder text generation)
6. Persist assistant response
7. Record improvement metric and return response payload

### 3) Task orchestration

- `execute_task()` constructs a task record and submits it to `AgentOrchestrator`
- `get_task_status(task_id)` fetches orchestrator status for a task

## Memory integration and RAG

Planned upgrade: Retrieval‑Augmented Reasoning (RAG) is a first‑class flow that leverages the Memory System’s strengths.

RAG pipeline (design):

- Query construction: build retrieval queries from the message, session context, and goals
- Retrieval: fetch typed memories (core/conceptual/episodic) with scores and metadata
- Evidence selection: apply confidence/recency/privacy filters; prefer high‑confidence, recent, policy‑safe items
- Reasoning context: construct a compact context window with citations and provenance
- Answer synthesis: reasoning engine uses the evidence to produce grounded responses

Contracts:

- `MemoryRecallResult` items include a `kind` discriminator and `scores`; the engine will weigh items by confidence, recency, and relevance
- Ephemeral scratchpad: short‑lived, session‑scoped context that is never persisted; used to hold chain‑of‑thought/tool traces (privacy‑aware)

Example (conceptual):

```python
# 1) Retrieve
hits = await engine.memory_system.recall_memories(query_text=message, limit=8, memory_type="conversation")
# 2) Select high-confidence evidence
evidence = [m for m in hits if getattr(m, "importance", 0.0) >= 0.6][:5]
# 3) Build reasoning context with citations
ctx = {
  "query": message,
  "evidence": [{"id": getattr(m, "id", None), "content": getattr(m, "content", None)} for m in evidence],
  "session": engine.conversation_context,
}
res = await engine.reasoning_engine.reason(ctx)
```

## Small contract summary

- Conversational request (input):
  - `{ message: str, context?: dict }`
- Conversational response (output):
  - `{ response: str, session_id: str, reasoning: str, confidence: float, memory_id: str, relevant_memories_count: int, timestamp: iso8601 }`
- Task execution (input):
  - `{ task_name: str, task_data: dict, priority?: "high"|"normal"|"background" }`
- Task submission (output):
  - `{ task_id: str }`
- System status (output):
  - `{ engine_status: "active"|"inactive", session_active: bool, memory_system: dict, improvement_system: dict, agent_orchestrator: dict, health_monitoring: dict, uptime_minutes: number, timestamp: iso8601 }`

Error modes:

- Subsystem unavailable → graceful mock behavior with conservative defaults
- Memory/IO error during process → user‑facing error payload with apology and `error` field

Confidence calibration (planned):

- Expand single `confidence` float into a structured object:
  - `{ model: float, grounding: float, coherence: float, safety: float }`
  - Keep `confidence` as the conservative minimum for backward compatibility

## Configuration and environment

The AI system honors repo‑wide flags and profiles; it does not define new env flags itself. Relevant existing flags:

- `AETHERRA_QUIET=1` to reduce logs in smoke runs
- `AETHERRA_PROFILE=test` to prefer deterministic behavior where supported
- Logging level: `AETHERRA_LOG_LEVEL=INFO|WARNING|ERROR`

Note: Advanced scheduler/backpressure and control flags live in the Kernel. See `docs/AETHERRA_KERNEL_SYSTEM.md`.

## Observability and metrics

- Introspection health: component monitor may register checks for memory, reasoning, and orchestrator
- Memory stats: total memories and simple retrieval metrics via memory system
- Improvement metrics: record simple counters (e.g., `user_satisfaction`, `response_generation_time`)
- Engine status: `get_system_status()` aggregates subsystem summaries for dashboards
- Hub exposure: surfaced indirectly via Kernel/Hub status endpoints and dashboards (see Project Overview)

Per‑session metrics (planned):

- Reasoning latency histogram; model/tool usage counters
- Fallback counts (mock → real; RAG hit/miss; safety filter triggers)
- Conversation coherence score (topic drift, repetition)
- Streaming timing (time to first token/chunk)

Auditability:

- Structured logs linked to session and trace IDs; integrate with the audit ledger
- Redact sensitive content; log hashes/identifiers instead of raw data when required

## Health and fault tolerance

- Initialization/shutdown: wraps subsystem start/stop with try/except and logs errors
- Graceful fallbacks: if a subsystem import fails, a mock class provides minimal behavior
- Conversation resilience: message processing tries to persist both user and assistant messages; on failure, returns an error payload

## AI safety

Input hardening:

- Sanitize user and plugin inputs; strip prompt‑injection patterns and disallowed instructions
- Canonicalize and validate tool arguments before invocation

Output filtering:

- Apply policy checks before returning responses (security, privacy, and content policy)
- Gate calls to risky tools by capability checks (enforced by the Kernel/Security systems)

Grounding:

- Prefer RAG‑grounded responses; cite evidence where appropriate
- Track a safety score in confidence calibration

## Extension points

- Reasoning:
  - Replace placeholder with production LLM + tool‑use (function‑calling/agents)
  - Add safety and policy checks on prompts/results
- Plugins/Tools:
  - Implement `PluginChainExecutor.execute_chain()` to support multi‑tool workflows
  - Integrate with Kernel capability checks and rate‑limits
- Memory:
  - Leverage advanced memory orchestrator for narratives, reflection, and health (see Memory System doc)
- Orchestration:
  - Extend `AgentOrchestrator` with richer dependency graphs, retries, and progress telemetry
- Introspection:
  - Register component checks and thresholds for dashboards and alerts

Reasoning plugins:

- Register custom reasoning modules behind a common `reason(context)` contract
- Enable policy‑aware routing (map tasks to reasoning backends by capabilities/policies)

Personality modules:

- Inject tone/behavior profiles (e.g., Lyrixa persona) as part of the reasoning context
- Ensure profiles are policy‑aware and can be swapped per session/app

Policy‑aware orchestration:

- Integrate capability enforcement in agent orchestration; avoid tool use outside granted scopes

## Known limitations and roadmap

- Reasoning uses a placeholder; upgrade to LLM‑backed reasoning with tools and retrieval‑augmented generation
- No direct HTTP API from the engine; interactions occur via Kernel/Hub or scripts
- Improvement metrics are minimal; expand with structured feedback loops and evaluation harnesses
- Orchestrator is basic; evolve into policy‑aware, resource‑bounded scheduling

 Roadmap phases:

 1. LLM reasoning with tool‑use and safety filters; RAG integration with citations
 2. Streaming responses (WebSocket support, richer events) and live status events
 3. Multi‑agent orchestration (dependency graphs, parallelism, quotas)
 4. Evaluation harness and nightly regression suite; link to Kernel night cycle
 5. Per‑session telemetry and audit‑friendly structured logs
 6. Pluggable personalities and policy‑aware routing

## Night cycle tie‑in

The engine’s self‑improvement and evaluation harness can run during the Kernel’s nightly window. Typical jobs:

- Regression runs for conversation/task prompts; compare metrics to baselines
- Plugin/tool performance evaluation; error analysis and retries with backoff
- Narrative and reflection generation via the Memory System
- Model/tool warm‑starts and cache refreshes for the next day

Scheduling is triggered by Kernel maintenance; the engine exposes idempotent entrypoints to run these jobs safely.

## Optional developer APIs and streaming (status)

Developer ergonomics (implemented):

- Optional HTTP interface for local testing without the full OS boot
  - GET `/api/ai/status` - read-only AI engine readiness and authority contract
  - POST `/api/ai/ask` — conversational request, returns response JSON
  - POST `/api/ai/stream` — Server-Sent Events (SSE) stream
- Environment flags (all opt-in, default off):
  - `AETHERRA_AI_API_ENABLED=1` — enable AI developer APIs
  - `AETHERRA_AI_API_REQUIRE_TOKEN=1` — require token header for access
  - `AETHERRA_AI_API_TOKEN=<value>` — token used when required (falls back to `AETHERRA_HUB_CONTROL_TOKEN` if unset)
  - `AETHERRA_AI_API_STREAM=1` — enable streaming endpoint
- Streaming contract (SSE):
  - Events emitted in order: `status` -> `token` -> `final` (with reserved `trace` for future tool steps)
  - Each event payload is JSON in the `data:` field
  - `final` contains `{ ok: boolean, result?: object, error?: string }`

Security: only enable locally or behind Kernel/HUB auth; apply capability checks and rate limits.

## References (code and docs)

- Engine core: `Aetherra/aetherra_core/engine/aetherra_engine.py`
- Memory System doc: `docs/AETHERRA_MEMORY_SYSTEM.md`
- Kernel System doc: `docs/AETHERRA_KERNEL_SYSTEM.md`
- Lyrixa Chat endpoint: `docs/LYRIXA_CHAT_ENDPOINT.md`

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

