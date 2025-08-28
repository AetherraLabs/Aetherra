# Aetherra Chat System

Updated: 2025-08-27

This document describes the Aetherra Chat System: a platform-level conversational service that provides message transport, streaming, safety middleware, and observability for multiple clients (Lyrixa UI/CLI, tools, and future apps).

## Purpose and scope

- Define chat as a reusable platform service, separate from Lyrixa’s UI/identity concerns
- Document core contracts: request/response schema and SSE stream
- Describe routing, safety middleware, backpressure, and fallback behavior
- Specify observability (Prometheus), configuration flags, and extension points

## At‑a‑glance status

- Hub developer APIs: `POST /api/ai/ask`, `GET /api/ai/stream` — Implemented
- Hub Lyrixa bridge: `POST /api/lyrixa/chat` — Implemented (best‑effort, fallback)
- Safety filters, RAG hooks, scratchpad, confidence calibration — Implemented/Partial
- Backpressure/queue limits/retries/DLQ — Implemented at Hub/Orchestrator
- Prometheus chat series — Planned (names reserved below)

## Architecture overview

Chat is composed of three cooperating parts:

1) Hub endpoints (transport/control)
   - `POST /api/ai/ask` — synchronous JSON ask
   - `GET /api/ai/stream?...` — SSE stream of tokens/events
   - `POST /api/lyrixa/chat` — Lyrixa bridge via Service Registry, deterministic fallback when offline

2) Middleware pipeline (safety/intelligence)
   - Safety filters: prompt/response guards, redaction hooks
   - Retrieval hooks (RAG) and scratchpad for reasoning traces
   - Confidence calibration and degradations (deterministic fallbacks)

3) Backpressure and reliability
   - Queue limits, priority aging, retries, DLQ (shared with Agent Orchestrator)
   - Circuit breakers and rate limiting for upstream model calls

## Message and stream contracts

### Request (ask)

- Endpoint: `POST /api/ai/ask`
- Body (example):
  - `{ "messages": [{"role":"user","content":"..."}], "max_tokens": 512, "temperature": 0.2, "context": {"workspace": true} }`

### Response (ask)

- `{ "id": "...", "text": "...", "tokens": {"input": n, "output": m}, "confidence": 0.0..1.0, "scratchpad": optional }`

### Stream (SSE)

- Endpoint: `GET /api/ai/stream?session=...&token=...` (token optional per env)
- Events (format: event: TYPE, data: JSON):
  - `token` — incremental text tokens
  - `thought` — optional chain‑of‑thought summary/chunk (redacted by default)
  - `tool_call` — tool invocation intent
  - `safety_flag` — safety event with rule identifier
  - `done` — terminal event with usage and summary

### Lyrixa chat bridge

- Endpoint: `POST /api/lyrixa/chat`
- Request: `{ content: string, allow_edits?: bool, edit_root?: string }`
- Response (Lyrixa online): `{ text, suggestions, applied_changes, identity?, awareness? }`
- Response (fallback): `{ text, suggestions: [], applied_changes: [] }`

## Security and safety

- Token/claims gating for developer APIs (`/api/ai/*`) via env flags
- Safety filters applied on both prompt and response; redaction of sensitive data
- Rate limits and circuit breakers around model calls and streaming sources

## Observability


Chat API exposes hub-level Prometheus series:

- aetherra_chat_requests_total
- aetherra_chat_streams_current
- aetherra_chat_latency_ms_sum and aetherra_chat_latency_count (derive avg/percentiles in PromQL)
- aetherra_chat_chars_in_total and aetherra_chat_chars_out_total

Memory (quantum) observability via Hub:

- GET /api/memory/status returns coherence_id, branch, branches, entanglement_nodes, coherence (when available; otherwise ephemeral fallback marked enabled: false)
- /metrics exports aetherra_memory_* series: coherence_score, branches_total, fragments_total, entanglement_nodes_total, and a branch_info gauge
Related existing series:

- Kernel/registry/orchestrator metrics are already exposed and tested.

## Configuration and environment

Examples (opt‑in and guarded by deployment):

- `AETHERRA_AI_API_ENABLED=1` — enable `/api/ai/*`
- `AETHERRA_AI_API_REQUIRE_TOKEN=1` — require bearer for `/api/ai/*`
- `AETHERRA_CHAT_MAX_TOKENS=512` — default cap for outputs
- `AETHERRA_CHAT_TEMPERATURE=0.2` — default sampling temperature
- `AETHERRA_CHAT_RATE_LIMIT=30/m` — nominal rate limit per principal
- `AETHERRA_CHAT_SAFETY_MODE=strict|standard` — safety policy preset

## Extensibility

- Middleware insertion points: pre‑prompt, post‑tool, pre‑emit
- Tooling/agents interop: defer to Agent Orchestrator for long‑running tasks
- Transport: SSE today; gRPC/WebSocket can be added as alternate transports

## Testing

- Unit tests for:
  - `/api/ai/ask` shape and error modes
  - SSE stream basic sequence (`token` → `done`)
  - Safety intercepts and redactions
  - Backpressure/circuit‑breaker toggles (happy path + tripped)
  - Prometheus series presence with labels (when implemented)

## Integration map

- Lyrixa UI/CLI — uses chat bridge and/or developer APIs
- Engine — model orchestration, scratchpad, and confidence calibration
- Agent Orchestrator — complex tasks; status/metrics surfaced via Hub

## Service and Endpoint Summary

- Hub
  - `POST /api/ai/ask` — synchronous ask
  - `GET /api/ai/stream` — SSE streaming responses
  - `POST /api/lyrixa/chat` — bridge to Lyrixa (best‑effort)

## Environment Variables Index

- `AETHERRA_AI_API_ENABLED`
- `AETHERRA_AI_API_REQUIRE_TOKEN`
- `AETHERRA_CHAT_MAX_TOKENS`
- `AETHERRA_CHAT_TEMPERATURE`
- `AETHERRA_CHAT_RATE_LIMIT`
- `AETHERRA_CHAT_SAFETY_MODE`

---

Status: ✅ implemented (core endpoints, middleware, reliability) · 🚧 partial (full safety/RAG breadth) · 🔮 planned (chat‑specific metrics)
