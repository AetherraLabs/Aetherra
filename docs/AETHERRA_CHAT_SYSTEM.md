# Aetherra Chat System

## Release notes (2025-08-31)

- Lyrixa bridge schema hardening:
  - Persona is always included and defaults to `{ name: "Lyrixa" }` when upstream omits identity.
  - edit_plan is synthesized to mirror `suggestions[]` one-to-one (action/title/file pass-through).
  - confidence defaults to `0.5` if upstream does not provide it, bounded to [0.0, 1.0].
- SSE v2 resilience:
  - Last-Event-ID resume guarantees strictly monotonic event ids; resuming from stale ids starts at next id.
  - Added tests for mid-stream resume with gaps and for very stale resumes.

These changes are backward compatible and covered by new capability tests and validators.

Updated: 2025-08-31

This document describes the Aetherra Chat System: a platform-level conversational service that provides message transport, streaming, safety middleware, and observability for multiple clients (Lyrixa UI/CLI, tools, and future apps).

## Purpose and scope

- Define chat as a reusable platform service, separate from Lyrixa’s UI/identity concerns
- Document core contracts: request/response schema and SSE stream
- Describe routing, safety middleware, backpressure, and fallback behavior
- Specify observability (Prometheus), configuration flags, and extension points

## At‑a‑glance status

- Hub developer APIs: `POST /api/ai/ask`, `POST /api/ai/stream` (primary), `GET /api/ai/stream` (alias) — Implemented
- Hub Lyrixa bridge: `POST /api/lyrixa/chat` — Implemented (always-on advanced path with graceful fallback)
- Safety filters, RAG hooks, scratchpad, confidence calibration — Implemented/Partial
- Backpressure/queue limits/retries/DLQ — Implemented at Hub/Orchestrator
- Prometheus chat series — Implemented

## Architecture overview

Chat is composed of three cooperating parts:

Hub endpoints (transport/control)

- `POST /api/ai/ask` — synchronous JSON ask
- `POST /api/ai/stream` — SSE stream (JSON body)
- `GET /api/ai/stream?...` — SSE alias (query params) for simple clients

### WebSocket transport (optional)

- Capability advertise: `GET /api/ai/stream_ws` → 200 when WS available, 501 when disabled.
- Stream route: `ws://<host>/ws/ai/stream`
  - Client sends one JSON payload to start: `{ message, context?, client_message_id?, last_event_id? }`
  - Server sends frames identical in shape to SSEEnvelopeV2: `{ id, trace_id, ts, type, data, client_message_id? }`
  - Resume: if `last_event_id` is provided in the initial payload, the server starts envelopes at `last_event_id + 1`.
  - Idempotency: duplicates on `client_message_id` yield an immediate error JSON with `{ ok:false, code:"duplicate", client_message_id }` and the socket closes.
- `POST /api/lyrixa/chat` — Lyrixa bridge via Service Registry, deterministic fallback when offline

Middleware pipeline (safety/intelligence)

- Safety filters: prompt/response guards, redaction hooks, network allowlist checks
- Retrieval hooks (RAG) and scratchpad for reasoning traces
- Confidence calibration and degradations (deterministic fallbacks)

Backpressure and reliability

- Queue limits, priority aging, retries, DLQ (shared with Agent Orchestrator)
- TTL/deadline and priority parity with Kernel (drop/aging rules honored)
- Circuit breakers and rate limiting for upstream model calls

## Message and stream contracts

### Request (ask)

- Endpoint: `POST /api/ai/ask`
- Headers:
  - `X-Aetherra-Trace-Id` (optional): client-supplied trace id; if omitted, Hub generates one and returns it in headers and body.
  - `X-Aetherra-Chat-Version: 2` (response): indicates SSE v2/envelope contracts are in effect.
  - `X-Aetherra-Policy` (response): JSON snapshot of effective policy.
- Body (example):
  - Minimal: `{ "message": "hello", "context": {"workspace": true} }`
  - Optional backpressure fields:
    - `priority`: `"high" | "normal" | "background"` (default: `normal`)
    - `ttl_sec`: integer seconds-to-live; translated to a deadline if `deadline_ts` is absent
    - `deadline_ts`: UNIX epoch seconds; if in the past, request is rejected with DLQ record

### Response (ask)

Unified response contract returned under `result`:

- `response`: string — the answer text
- `session_id`: string — chat/session correlation id (generated if absent)
- `timestamp`: ISO string — when the hub emitted the response
- `reasoning` or `reasoning_ref`: optional — pass-through if provided by engine
- `memory_id`: optional — memory linkage id when available
- `relevant_memories_count`: number — count of linked memories if provided
- `confidence`: number — conservative float (kept for legacy clients)
- `confidence_breakdown`: object — `{ model?, grounding?, coherence?, safety? }`
- Additional safe passthrough fields when present: `provider`, `model`, `latency_ms`, `usage`, `id`
- `evidence`: optional array — normalized citations/evidence derived from RAG or engine fields. Each item:
  - `kind`: `"memory"|"doc"` (default `memory` if not provided)
  - `id?`: identifier for memory/doc (accepts `id|memory_id|uid` from upstream)
  - `uri?`: canonical URI or URL if available
  - `title?`: short human title if available
  - `score?`: number — relevance/score (best-effort normalization across `score|relevance|confidence`)
  - `snippet?`: string — supporting excerpt, trimmed to 1,024 chars
  - `tags?`: string[] — arbitrary tags when provided
- `scratchpad_policy`: optional — `"ephemeral"|"persisted"|"redacted"`; propagates user preference and engine behavior
- Traceability: response includes `trace_id` and sets headers `X-Aetherra-Trace-Id`, `X-Aetherra-Chat-Version`, and `X-Aetherra-Policy`.

### Stream (SSE)

- Primary: `POST /api/ai/stream`
  - Body: `{ "message"|"content": string, "context"?: object, "trace_id"?: string, "priority"?: string, "ttl_sec"?: int, "deadline_ts"?: number, "scratchpad_policy"?: "ephemeral|persisted|redacted" }`
  - Headers (response): `X-Aetherra-Trace-Id`, `X-Aetherra-Chat-Version`, `X-Aetherra-Policy`
  - Emits events (SSE Event Taxonomy v2; envelope format):
    - Envelope: every SSE line carries `data` as `{ id, trace_id, ts, type, data }` and includes `id:` header for Last-Event-ID clients.
    - Events:
      - `status` — stream start signal
      - `auth` — token/claims confirmation `{ required, ok }` (replaces `token`)
      - `policy` — effective policy snapshot
        - Base: `{ ai_enabled, stream_enabled, require_token, safety_mode, max_tokens, temperature }`
        - Safety extras: `{ dp: { enabled, epsilon? }, capabilities: string[], network_policy: { allowlist: string[], block_unknown: bool } }`
      - `usage` — usage counters `{ tokens_in, tokens_out, chars_in, chars_out }`
      - `heartbeat` — reserved for long streams (not emitted by default)
    - `final` — terminal with `{ ok, result }` (result uses the unified contract, including `evidence[]` and optional `scratchpad_policy`)
      - `error` — emitted prior to `final` when failures occur `{ message }`
  - Reconnects: Clients may send `Last-Event-ID` to resume sequencing; server does not replay past data yet but continues with monotonic ids.
  - Expiry/backpressure: if `deadline_ts` is in the past (or `ttl_sec` resolves to a past deadline), the stream emits `error` then `final` and the request is written to DLQ.
- Alias: `GET /api/ai/stream?message=...&token=...`
  - Accepts `message` (or `content`) as a query param. When `AETHERRA_AI_API_REQUIRE_TOKEN=1`, token may be supplied via header `X-Aetherra-Token` or `?token=`.
  - Emits the same SSE v2 events and envelope as the POST variant.
  - Supports optional query params: `trace_id`, `priority`, `ttl_sec`, `deadline_ts`, `scratchpad_policy`, and `last_event_id`.

### Lyrixa chat bridge

- Endpoint: `POST /api/lyrixa/chat`
- Request: `{ content: string, allow_edits?: bool, edit_root?: string }`
- Response (Lyrixa online): `{ text, suggestions, applied_changes, identity?, awareness? }` plus advanced fields when available:
  - `awareness.confidence_breakdown` — provided by the adaptive orchestrator
  - `awareness.evidence` — normalized citations from persistent memory via MultidimensionalMemory
  - `awareness.consciousness` — small coherence snapshot when the bridge is available
- Response (fallback): `{ text, suggestions: [], applied_changes: [] }`

## Security and safety

- Token/claims gating for developer APIs (`/api/ai/*`) via env flags
- Safety filters applied on both prompt and response; redaction of sensitive data; strict network allowlist in strict mode
- Rate limits and circuit breakers around model calls and streaming sources
- Security ledger: high‑risk intercepts are appended to `security_ledger.jsonl` (path configurable) with trace id and reasons

### Safety modes (auditable)

- `AETHERRA_CHAT_SAFETY_MODE=strict|standard`
  - strict: short‑circuit on detected high‑risk prompts; enforce network allowlist for outbound URLs in the prompt; capability grants are conservative (`tools:allowlist`, `write:none`, limited FS)
  - standard: redact secrets; allow unknown hosts by default; capability grants allow limited write

Effective policy is surfaced to clients via:

- Response header `X-Aetherra-Policy`: JSON of the snapshot
- SSE `policy` event: includes `dp`, `capabilities`, and `network_policy`

Preflight behavior:

- On deny, non‑stream endpoints return 403 with `{ error: { code: "policy_violation", message, details: { reasons: [...] } } }`
- Streaming emits `error` then `final` with the same standardized error shape.
  The prompt text is redacted before any downstream processing.

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
- `AETHERRA_NETWORK_ALLOWLIST` — comma‑separated hosts/wildcards (e.g. `localhost,127.0.0.1,*.aetherra.dev`); strict mode defaults to a localhost/aetherra.dev allowlist
- `AETHERRA_DP_ENABLED=0|1` and `AETHERRA_DP_EPSILON` — differential privacy flags surfaced in policy snapshot
- `AETHERRA_SECURITY_LEDGER=1` and `AETHERRA_SECURITY_LEDGER_PATH` — enable and path for `security_ledger.jsonl`
Kernel/Hub parity:
- `AETHERRA_KERNEL_TASK_DEFAULT_TTL_SEC` — default TTL applied by Kernel if no deadline is provided
- `AETHERRA_KERNEL_DLQ=1` — enable Kernel DLQ; Hub will prefer Kernel DLQ for chat expiry records when available (fallback to `hub_chat_dlq.jsonl`)
- `AETHERRA_KERNEL_QSIZE_*` and queue limit controls exposed via Hub control APIs

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
  - `POST /api/ai/stream` — SSE streaming (JSON body)
  - `GET /api/ai/stream` — SSE alias (query params)
  - `POST /api/lyrixa/chat` — bridge to Lyrixa (best‑effort)

## Quick LLM Setup Verification

Use the helper script to validate environment and basic provider wiring:

```bash
python tools/verify_llm_setup.py
```

It checks:

- Required feature flags (`AETHERRA_AI_API_*`), with clear warnings
- Presence of provider keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
- Optional: a minimal provider round‑trip if libraries are installed

Exit code is 0 when configuration is consistent; it returns 1 if `AETHERRA_AI_API_REQUIRE_TOKEN=1` is set but no token is configured (`AETHERRA_AI_API_TOKEN` or `AETHERRA_HUB_CONTROL_TOKEN`).

## Environment Variables Index

- `AETHERRA_AI_API_ENABLED`
- `AETHERRA_AI_API_REQUIRE_TOKEN`
- `AETHERRA_AI_API_STREAM`
- `AETHERRA_CHAT_MAX_TOKENS`
- `AETHERRA_CHAT_TEMPERATURE`
- `AETHERRA_CHAT_RATE_LIMIT`
- `AETHERRA_CHAT_SAFETY_MODE`
- `AETHERRA_NETWORK_ALLOWLIST`
- `AETHERRA_DP_ENABLED`
- `AETHERRA_DP_EPSILON`
- `AETHERRA_SECURITY_LEDGER`
- `AETHERRA_SECURITY_LEDGER_PATH`
- `AETHERRA_KERNEL_TASK_DEFAULT_TTL_SEC`
- `AETHERRA_KERNEL_DLQ`

---

Status: ✅ implemented (core endpoints, middleware, reliability) · 🚧 partial (full safety/RAG breadth) · 🔮 planned (chat‑specific metrics)

## RAG and citations contract

Final payloads include an optional `evidence[]` array and a `scratchpad_policy` knob to control reasoning artifact handling.

- Evidence normalization: the hub coerces common upstream shapes like `relevant_memories[]`, `sources[]`, or `documents[]` into a stable array with fields shown below. Unknown extra fields are dropped. Snippets are trimmed to 1,024 chars.
- Scratchpad policy: set via request (`POST` body or `GET` query) to one of `ephemeral|persisted|redacted`. The engine may honor/override based on policy. The effective value is echoed in the final result when set.

Example final result (ask or stream `final.data.result`):

```json
{
  "response": "Here are key points...",
  "session_id": "8b7e9f7c-1f1e-4b0a-9f3d-3a3a3e5e0b47",
  "timestamp": "2025-08-31T17:22:45.601Z",
  "confidence": 0.62,
  "confidence_breakdown": { "model": 0.74, "grounding": 0.62, "coherence": 0.66, "safety": 0.93 },
  "relevant_memories_count": 2,
  "scratchpad_policy": "ephemeral",
  "evidence": [
    {
      "kind": "memory",
      "id": "mem:abc123",
      "title": "User preference: dark theme",
      "score": 0.81,
      "snippet": "... prefers dark mode across apps ...",
      "tags": ["profile", "prefs"]
    },
    {
      "kind": "doc",
      "uri": "https://docs.aetherra.dev/chat/contracts#sse-v2",
      "title": "SSE v2 Envelope",
      "score": 0.77,
      "snippet": "Every SSE line carries data as { id, trace_id, ts, type, data } ..."
    }
  ]
}
```

SSE `final` example (envelope abridged):

```json
{
  "id": "42",
  "trace_id": "d2e2f1...",
  "ts": "2025-08-31T17:22:45.602Z",
  "type": "final",
  "data": {
    "ok": true,
    "result": { "response": "...", "evidence": [/* as above */], "scratchpad_policy": "ephemeral" }
  }
}
```

## Client guide: reconnect-safe SSE v2 and evidence handling

This short guide shows how to consume the SSE v2 stream with resume support and how to read the normalized `evidence[]` and `scratchpad_policy` from the final payload.

Key points:

- Every SSE message uses the envelope `{ id, trace_id, ts, type, data }` and sets the SSE `id:` field. Persist the latest `id` you received to support resume.
- To resume after a disconnect, send the `Last-Event-ID` header (preferred) or `?last_event_id=` query on the next connection. The server won’t replay past chunks but continues with a strictly greater `id`.
- The final message has `type: "final"` and `data: { ok, result }`. Read `result.scratchpad_policy` and iterate `result.evidence[]`.

### Minimal GET client (browser/EventSource)

```js
// Example only; adjust URL and params to your deployment
const params = new URLSearchParams({
  message: "Summarize project state",
  scratchpad_policy: "redacted",
});

let lastId = localStorage.getItem("aetherra:lastEventId") || undefined;
const headers = lastId ? { "Last-Event-ID": lastId } : {};

const es = new EventSource(`/api/ai/stream?${params.toString()}`, { withCredentials: false });

es.onmessage = (evt) => {
  // evt.lastEventId contains the SSE id header
  if (evt.lastEventId) localStorage.setItem("aetherra:lastEventId", evt.lastEventId);
  const env = JSON.parse(evt.data); // { id, trace_id, ts, type, data }
  switch (env.type) {
    case "status":
    case "policy":
    case "usage":
    case "chunk":
      // handle as needed
      break;
    case "final": {
      const { ok, result } = env.data;
      // Read scratchpad policy echo
      console.log("scratchpad_policy:", result.scratchpad_policy);
      // Iterate normalized evidence[]
      (result.evidence || []).forEach((e) => {
        // e.kind, e.id|uri, e.title, e.score, e.snippet, e.tags
      });
      es.close();
      break;
    }
    case "error":
      console.warn("stream error:", env.data);
      break;
  }
};

es.onerror = () => {
  es.close();
  // On next connect, browser EventSource automatically sends Last-Event-ID
};
```

### Minimal POST client (Node/Fetch + SSE parser)

```js
// Pseudocode; use an SSE parser like eventsource-parser
import fetch from "node-fetch";
import { createParser } from "eventsource-parser";

let lastId; // persist between runs to resume
const res = await fetch("http://localhost:3012/api/ai/stream", {
  method: "POST",
  headers: {
    "content-type": "application/json",
    ...(lastId ? { "Last-Event-ID": String(lastId) } : {}),
  },
  body: JSON.stringify({
    message: "Outline risks and mitigations",
    scratchpad_policy: "ephemeral",
  }),
});

const parser = createParser((event) => {
  if (event.type === "event") {
    if (event.id) lastId = event.id;
    const env = JSON.parse(event.data);
    if (env.type === "final") {
      const { result } = env.data;
      console.log(result.scratchpad_policy);
      console.log(result.evidence || []);
    }
  }
});

for await (const chunk of res.body) parser.feed(chunk.toString());
```

Notes:

- Both POST and GET support `scratchpad_policy` in the request and echo it in the final result, including error paths.
- If `AETHERRA_AI_API_REQUIRE_TOKEN=1`, provide your token via `X-Aetherra-Token` (header) or `?token=`.
- The server exposes `X-Aetherra-Trace-Id` and `X-Aetherra-Policy` headers for correlation and policy visibility.

## Appendix: Patch‑ready spec inserts (v2 examples)

The following drop-in text provides concrete examples and clarifications to reduce ambiguity and align with Engine, Kernel, Agents, and Security systems. Where behavior is marked “planned,” the Hub will evolve to match (current behavior is compatible unless noted).

### A) Request/Response (Ask v2)

POST /api/ai/ask

```json
{
  "messages": [{"role": "user", "content": "..." }],
  "context": {
    "session_id": "opt",
    "workspace": true,
    "policy": {"budget": {"tokens": 2000, "sec": 30}},
    "deadline_ts": 1725062400,
    "priority": "normal",
    "ttl_sec": 60,
    "client_message_id": "opt"
  },
  "max_tokens": 512,
  "temperature": 0.2
}
```

200 OK

```json
{
  "id": "run_123",
  "text": "...",
  "session_id": "sess_abc",
  "tokens": {"input": 123, "output": 456},
  "confidence": 0.71,
  "confidence_breakdown": {"model": 0.74, "grounding": 0.68, "coherence": 0.73, "safety": 0.90},
  "memory_id": "mem_987",
  "relevant_memories_count": 3,
  "evidence": [{"kind":"memory","id":"mem_987","score":0.81}],
  "timestamp": "2025-08-31T12:34:56Z",
  "trace_id": "trc_..."
}
```

Aligns with Engine’s conversational payload and planned confidence calibration.

Note: The Hub normalizes responses under `result` with stable fields (e.g., `response`, `evidence[]`, `scratchpad_policy`). This example shows an engine-aligned flat shape; mapping is preserved in normalization.

### B) SSE Stream (Events v2)

POST /api/ai/stream

Headers:

```text
X-Aetherra-Trace-Id: trc_...
X-Aetherra-Chat-Version: 2
```

Example transcript:

```text
event: status
data: {"id":"1","trace_id":"trc_...","ts":"...","data":{"ready":true}}

event: auth
data: {"id":"2","trace_id":"trc_...","data":{"token_required":true,"principal":"user|svc"}}

event: policy
data: {"id":"3","trace_id":"trc_...","data":{"safety_mode":"strict","caps":["memory.read"],"dp":false}}

event: thought
data: {"id":"4","trace_id":"trc_...","data":{"summary":"Planning RAG retrieval..."}}

event: chunk
data: {"id":"5","trace_id":"trc_...","data":{"delta":"Hello", "index":0}}

event: usage
data: {"id":"6","trace_id":"trc_...","data":{"input":100,"output":10}}

event: heartbeat
data: {"id":"7","trace_id":"trc_...","data":{"ms":15000}}

event: final
data: {"id":"8","trace_id":"trc_...","data":{
  "text":"Hello world",
  "session_id":"sess_abc",
  "confidence":0.71,
  "confidence_breakdown":{"model":0.74,"grounding":0.68,"coherence":0.73,"safety":0.90},
  "evidence":[{"kind":"memory","id":"mem_987","score":0.81}],
  "timestamp":"2025-08-31T12:34:56Z"
}}
```

Removes ambiguity between auth vs token counts; adds reconnect safety via event id.

Note: Today, `auth` is emitted and `token` may also be emitted when tokens are required; future revisions may prefer `auth` only. The server already supports Last-Event-ID resume with strictly increasing ids.

### C) Standard errors & rate‑limit

```text
HTTP/1.1 429 Too Many Requests
Retry-After: 30
{
  "error": { "code":"rate_limited","message":"Rate limit exceeded","details":{"retry_after_sec":30}, "trace_id":"trc_..." }
}
```

Backs the existing backpressure narrative with actionable semantics.

### D) Security & policy hooks

Safety profiles map to: prompt‑defense scanner (jailbreak detection), capability enforcement, network policy allowlist/denylist, and DP telemetry toggles; policy events expose what’s active for this stream.

`/api/ai/*` remains token‑guarded per env (`AETHERRA_AI_API_ENABLED`, `AETHERRA_AI_API_REQUIRE_TOKEN`).

### E) Observability additions

Prometheus (hub):

- `aetherra_chat_ttft_ms` (histogram)
- `aetherra_chat_chunks_total`
- `aetherra_chat_fallback_total{path}`
- `aetherra_chat_breaker_open_total`
- `aetherra_chat_streams_current{principal}`

Coordinate with Kernel `/metrics` to correlate per‑target inflight and HMR states.

### F) Handoff to Agents

When work escalates to a long task:

```text
event: handoff
data: {"task_id":"t_123","status_url":"/api/tasks/t_123"}
```

Client then attaches to `/api/tasks/{id}/stream`.

### Small fixes & clarifications

- Rename SSE `token` → `auth`; add `usage` for token/char counts to avoid confusion.
- Document keep‑alive cadence and proxy guidance (disable buffering for SSE).
- State the idempotency window for `client_message_id` and expected semantics on duplicates.
- Spell out default caps for the Lyrixa bridge (what it may edit/apply) and how failures degrade to fallback text.

### Why this matches the rest of Aetherra

- Engine alignment: shared response fields and confidence schema remove glue code between chat and reasoning/memory.
- Kernel alignment: deadlines/TTL/priorities + `trace_id` bring chat into the OS scheduling model.
- Agents alignment: explicit `handoff` event makes chat a first‑class ingress for multi‑agent work.
- Security alignment: safety profiles, network policy, and capability gates are visible and testable from the stream.
- Memory alignment: evidence/citations and scratchpad policy reflect the memory system’s typed recall and health discipline.
- Project flags: uses the same enable/require‑token env switches documented at the Hub/Overview layer.

### Implementation checklist (for PRs)

- Add trace_id propagation + headers; honor `deadline_ts`, `ttl_sec`, `priority`.
- Update SSE emitter to v2 taxonomy and add `id` per event; implement heartbeat.
- Expand final payload to include Engine fields + `confidence_breakdown`.
- Implement `client_message_id` dedup window; define duplicate semantics and surface id in response.
- Add `policy` event (caps, DP, safety mode, net policy).
- Add `handoff` → Agents stream and document `/api/tasks/{id}/stream`.
- Extend Prometheus series (TTFT, chunk rate, fallbacks, breaker).
- Document optional WebSocket transport with identical frames.

