# Aetherra Hub API Reference

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This document provides a comprehensive reference for all REST API endpoints exposed by the Aetherra Hub server. The Hub acts as the primary integration point between the Aetherra OS core, frontend clients, and external services.

## Purpose and scope

- Document all HTTP endpoints with request/response schemas
- Provide authentication and authorization requirements
- Include practical examples (curl, Python, JavaScript)
- Define error codes and status conventions
- Explain rate limiting and performance considerations

## At-a-glance status

- **Base URL**: `http://localhost:3001` (default, configurable via `--port`)
- **Protocol**: HTTP/1.1, WebSocket, Server-Sent Events (SSE)
- **Authentication**: Token-based (optional, configurable)
- **Content-Type**: `application/json` (primary), `text/event-stream` (SSE)
- **API Version**: v1 (implicit, no version prefix)

## General conventions

### HTTP status codes

- **200 OK**: Request succeeded
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource or endpoint not found
- **500 Internal Server Error**: Server-side error
- **501 Not Implemented**: Feature not yet available
- **503 Service Unavailable**: Service temporarily unavailable

### Authentication

Optional token-based authentication controlled by environment variables:

```bash
# Enable authentication
export AETHERRA_AI_API_REQUIRE_TOKEN=1
export AETHERRA_AI_API_TOKEN=your_secret_token_here

# Or for agents API
export AETHERRA_AGENTS_API_REQUIRE_TOKEN=1
export AETHERRA_AGENTS_API_TOKEN=your_secret_token_here
```

**Header format**:
```
Authorization: Bearer <token>
```

### Error response format

All error responses follow this structure:

```json
{
  "error": "Brief error description",
  "details": "Detailed error context (optional)",
  "code": "ERROR_CODE (optional)"
}
```

---

## API Endpoints by Category

### 🤖 AI & Chat APIs

#### POST /api/ai/ask

Ask a question to the AI system (non-streaming).

**Authentication**: Optional (if `AETHERRA_AI_API_REQUIRE_TOKEN=1`)

**Request**:
```json
{
  "message": "What is Aetherra OS?",
  "session_id": "optional-session-id",
  "context": {
    "user_id": "optional-user-id"
  }
}
```

**Response (200 OK)**:
```json
{
  "response": "Aetherra OS is an autonomous AI operating system...",
  "session_id": "session-123",
  "metadata": {
    "model": "engine-v1",
    "tokens": 150
  }
}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:3001/api/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, Aetherra!"}'
```

**Example (Python)**:
```python
import requests

response = requests.post(
    "http://localhost:3001/api/ai/ask",
    json={"message": "What can you do?"}
)
print(response.json())
```

---

#### POST /api/ai/stream

Request AI response as Server-Sent Events (SSE) stream.

**Authentication**: Optional (if `AETHERRA_AI_API_REQUIRE_TOKEN=1`)

**Request**:
```json
{
  "message": "Explain quantum computing",
  "stream": true
}
```

**Response (200 OK)**: `text/event-stream`

Stream format:
```
data: {"type":"start","session_id":"session-123"}

data: {"type":"token","content":"Quantum"}

data: {"type":"token","content":" computing"}

data: {"type":"done","metadata":{"tokens":150}}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:3001/api/ai/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "Hello", "stream": true}'
```

**Example (JavaScript/fetch)**:
```javascript
const response = await fetch('http://localhost:3001/api/ai/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello', stream: true })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  console.log(chunk);
}
```

---

#### GET /api/ai/stream

Alternative GET endpoint for SSE streaming (query parameters).

**Request**: Query parameters in URL

**Example**:
```bash
curl "http://localhost:3001/api/ai/stream?message=Hello&stream=true" \
  -H "Accept: text/event-stream"
```

---

#### WebSocket /api/ai/stream_ws

WebSocket endpoint for bidirectional AI streaming.

**Connection**: `ws://localhost:3001/api/ai/stream_ws`

**Message format (send)**:
```json
{
  "message": "Your question here",
  "session_id": "optional-session-id"
}
```

**Message format (receive)**:
```json
{
  "type": "token|done|error",
  "content": "Response content",
  "metadata": {}
}
```

**Example (JavaScript)**:
```javascript
const ws = new WebSocket('ws://localhost:3001/api/ai/stream_ws');

ws.onopen = () => {
  ws.send(JSON.stringify({ message: 'Hello!' }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.content);
};
```

---

#### POST /api/lyrixa/chat

Chat with Lyrixa through the Hub bridge.

**Request**:
```json
{
  "message": "Help me understand memory system",
  "allow_edits": false,
  "edit_root": "/optional/path"
}
```

**Response (200 OK)**:
```json
{
  "text": "The memory system consists of...",
  "suggestions": [
    {
      "title": "Fix memory leak",
      "file": "memory_core.py",
      "action": "replace_line"
    }
  ],
  "applied_changes": [],
  "identity": {
    "name": "Lyrixa",
    "version": "1.0"
  }
}
```

**Response (fallback when Lyrixa offline)**:
```json
{
  "text": "Lyrixa chat service is not online right now.",
  "suggestions": [],
  "applied_changes": []
}
```

---

### 🔧 Agent Orchestration APIs

#### GET /api/agents

List available agents in the system.

**Response (200 OK)**:
```json
{
  "agents": [
    {
      "name": "planner",
      "capabilities": ["planning", "task_decomposition"],
      "status": "available"
    },
    {
      "name": "executor",
      "capabilities": ["execution", "tool_usage"],
      "status": "available"
    }
  ],
  "count": 2
}
```

---

#### POST /api/tasks

Create a new task for agent execution.

**Authentication**: Optional (if `AETHERRA_AGENTS_API_REQUIRE_TOKEN=1`)

**Request**:
```json
{
  "description": "Analyze memory usage patterns",
  "agent": "analyzer",
  "priority": "normal",
  "context": {
    "time_range": "last_24h"
  }
}
```

**Response (201 Created)**:
```json
{
  "task_id": "task-abc-123",
  "status": "pending",
  "created_at": "2025-11-01T10:30:00Z"
}
```

---

#### GET /api/tasks

List recent tasks with optional filtering.

**Query Parameters**:
- `limit`: Number of tasks to return (default: 10)
- `status`: Filter by status (pending/running/completed/failed)
- `agent`: Filter by agent name

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "task_id": "task-abc-123",
      "description": "Analyze memory usage",
      "status": "completed",
      "agent": "analyzer",
      "created_at": "2025-11-01T10:30:00Z",
      "completed_at": "2025-11-01T10:31:45Z"
    }
  ],
  "count": 1
}
```

---

#### GET /api/tasks/:task_id

Get detailed status of a specific task.

**Response (200 OK)**:
```json
{
  "task_id": "task-abc-123",
  "status": "completed",
  "result": {
    "summary": "Memory usage is within normal bounds",
    "details": {}
  },
  "performed_at": "2025-11-01T10:30:00Z",
  "duration_secs": 105,
  "agent": "analyzer"
}
```

---

### 🧠 Memory System APIs

#### GET /api/memory/status

Get memory system status and health.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "stats": {
    "total_memories": 1523,
    "recent_queries": 45,
    "avg_recall_latency_ms": 23
  },
  "storm": {
    "enabled": true,
    "status": "active",
    "ot_backend": "POT"
  }
}
```

---

#### GET /api/memory/graph

Get memory graph visualization data.

**Response (200 OK)**:
```json
{
  "nodes": [
    {
      "id": "mem-123",
      "content": "...",
      "connections": 5
    }
  ],
  "edges": [
    {
      "source": "mem-123",
      "target": "mem-456",
      "weight": 0.8
    }
  ]
}
```

---

#### GET /api/memory/audit

Get memory system audit log.

**Response (200 OK)**:
```json
{
  "events": [
    {
      "timestamp": "2025-11-01T10:30:00Z",
      "event_type": "store",
      "memory_id": "mem-123",
      "user": "system"
    }
  ]
}
```

---

### 🏥 Homeostasis & Maintenance APIs

#### GET /api/homeostasis/status

Get comprehensive Homeostasis system status.

**Response (200 OK)**:
```json
{
  "status": "active",
  "health_score": 0.95,
  "phases": {
    "metrics_collection": "running",
    "controller": "running",
    "actuators": "running",
    "supervisor": "running",
    "feedback": "running",
    "validation": "running",
    "error_correction": "running",
    "metrics_bridge": "running"
  },
  "recent_actions": 12,
  "last_check": "2025-11-01T10:29:00Z"
}
```

---

#### GET /api/homeostasis/metrics

Get current stability metrics snapshot.

**Response (200 OK)**:
```json
{
  "timestamp": "2025-11-01T10:30:00Z",
  "metrics": {
    "task_latency_p95_ms": 95,
    "memory_rtt_ms": 45,
    "plugin_load_success_rate": 0.98,
    "exception_suppression_count": 2,
    "queue_depth": 3
  }
}
```

---

#### GET /api/maintenance/status

Get unified maintenance system status (Homeostasis + Self-Improvement + Self-Incorporation).

**Response (200 OK)**:
```json
{
  "timestamp": "2025-11-01T10:30:00Z",
  "healthy": true,
  "subsystems": {
    "homeostasis": {
      "running": true,
      "status": "active"
    },
    "self_improvement_engine": {
      "enabled": true,
      "status": "idle"
    },
    "self_incorporation": {
      "running": true,
      "status": "active"
    }
  },
  "kpis": {
    "system_health_score": 0.92,
    "actions_executed": 45,
    "proposals_generated": 12,
    "proposals_executed": 10,
    "proposals_accepted": 7,
    "files_integrated": 23,
    "files_quarantined": 2,
    "last_rollback_token": "hmr-2025-11-01-001"
  }
}
```

See [AETHERRA_SELF_IMPROVEMENT_API.md](./AETHERRA_SELF_IMPROVEMENT_API.md) for Self-Improvement proposal endpoints.

---

### 🔐 Self-Incorporation APIs

#### GET /api/selfinc/status

Get Self-Incorporation service status.

**Response (200 OK)**:
```json
{
  "running": true,
  "enabled": true,
  "metrics": {
    "files_discovered": 150,
    "files_classified": 145,
    "files_integrated": 80,
    "files_quarantined": 5,
    "discovery_rate": 12.5,
    "integration_success_rate": 0.96
  },
  "last_rollback_token": "rollback-2025-11-01-001"
}
```

---

#### GET /api/selfinc/discovered

List discovered files with optional filtering.

**Query Parameters**:
- `path`: Filter by path pattern

**Response (200 OK)**:
```json
{
  "files": [
    {
      "path": "plugins/new_plugin.py",
      "discovered_at": "2025-11-01T09:00:00Z",
      "status": "classified",
      "classification": "plugin"
    }
  ],
  "count": 1
}
```

---

#### GET /api/selfinc/classified

List classified files.

**Query Parameters**:
- `classification`: Filter by type (plugin/script/config/etc)
- `intent`: Filter by intent

**Response (200 OK)**:
```json
{
  "files": [
    {
      "path": "plugins/analyzer.py",
      "classification": "plugin",
      "intent": "system_optimization",
      "confidence": 0.95,
      "trust_score": 0.88
    }
  ],
  "count": 1
}
```

---

#### GET /api/selfinc/audit

Get Self-Incorporation audit records.

**Query Parameters**:
- `action`: Filter by action type
- `limit`: Number of records (default: 100)

**Response (200 OK)**:
```json
{
  "records": [
    {
      "timestamp": "2025-11-01T10:00:00Z",
      "action": "integrate",
      "path": "plugins/new_feature.py",
      "result": "success",
      "rollback_token": "rollback-001"
    }
  ],
  "total": 1
}
```

---

#### GET /api/selfinc/metrics

Get Self-Incorporation Prometheus metrics.

**Response (200 OK)**:
```
# HELP aetherra_selfinc_files_discovered Total files discovered
# TYPE aetherra_selfinc_files_discovered counter
aetherra_selfinc_files_discovered 150

# HELP aetherra_selfinc_files_integrated Total files integrated
# TYPE aetherra_selfinc_files_integrated counter
aetherra_selfinc_files_integrated 80
```

---

#### GET /api/selfinc/ethics/dashboard

Get ethics evaluation dashboard.

**Response (200 OK)**:
```json
{
  "summary": {
    "total_evaluations": 145,
    "approved": 80,
    "rejected": 10,
    "pending": 55
  },
  "recent_concerns": [],
  "policy_compliance": 0.98
}
```

---

### ⚙️ Kernel & System APIs

#### GET /api/kernel/status

Get kernel loop status.

**Response (200 OK)**:
```json
{
  "running": true,
  "uptime": 86400.5,
  "cycle_count": 144000,
  "metrics": {
    "tasks_processed": 5234,
    "avg_task_latency_ms": 12
  },
  "queue_sizes": {
    "high_priority": 0,
    "normal_priority": 3,
    "background": 15
  },
  "hmr": {
    "enabled": true,
    "attempts": 5,
    "success": 5,
    "rollback": 0
  }
}
```

---

#### GET /api/kernel/metrics

Get detailed kernel metrics (JSON format).

**Response (200 OK)**:
```json
{
  "hub_ts": "2025-11-01T10:30:00Z",
  "kernel": {
    "running": true,
    "uptime": 86400.5,
    "metrics": {}
  }
}
```

---

#### GET /api/klm/status

Get Module Manager (KLM) status.

**Response (200 OK)**:
```json
{
  "active": true,
  "modules_loaded": 15,
  "modules_active": 14,
  "recent_reloads": 2
}
```

---

#### GET /api/keb/status

Get Event Bus (KEB) status.

**Response (200 OK)**:
```json
{
  "active": true,
  "topics": 8,
  "subscribers": 12,
  "events_published": 5234,
  "events_delivered": 5230
}
```

---

### 🔌 Plugin APIs

#### GET /api/plugins

List all registered plugins.

**Response (200 OK)**:
```json
{
  "plugins": [
    {
      "name": "memory_optimizer",
      "version": "1.0.0",
      "category": "system",
      "status": "active"
    }
  ],
  "count": 1
}
```

---

#### POST /api/plugins/register

Register a new plugin.

**Request**:
```json
{
  "name": "my_plugin",
  "manifest": {
    "version": "1.0.0",
    "entry_point": "plugin.py:Plugin"
  }
}
```

**Response (201 Created)**:
```json
{
  "status": "registered",
  "plugin_id": "plugin-123"
}
```

---

#### GET /api/plugins/metrics

Get plugin system metrics.

**Response (200 OK)**:
```
# HELP aetherra_plugins_loaded Total plugins loaded
# TYPE aetherra_plugins_loaded gauge
aetherra_plugins_loaded 15
```

---

### 📜 Aether Script APIs

#### POST /api/run

Execute an Aether script.

**Request**:
```json
{
  "script": "workflows/demo.aether",
  "args": {},
  "async": true
}
```

**Response (201 Created)**:
```json
{
  "job_id": "job-abc-123",
  "status": "running",
  "started_at": "2025-11-01T10:30:00Z"
}
```

---

#### POST /api/cancel/:job_id

Cancel a running script job.

**Response (200 OK)**:
```json
{
  "ok": true,
  "message": "Job cancelled"
}
```

---

### 🔒 Security & Policy APIs

#### GET /api/security/policy

Get current security policy snapshot.

**Response (200 OK)**:
```json
{
  "capabilities": {
    "allow": {
      "core:*": ["*"]
    },
    "deny": {}
  },
  "network": {
    "allowlist": ["localhost", "127.0.0.1"],
    "denylist": []
  },
  "strict_mode": false
}
```

---

#### GET /api/policy/disclosure

Get policy disclosure information.

**Response (200 OK)**:
```json
{
  "telemetry_opt_in": false,
  "data_retention_days": 90,
  "disclosure_url": "https://aetherra.ai/privacy"
}
```

---

### 🧪 Testing & Development APIs

#### GET /api/trainer/status

Get AI trainer status.

**Response (200 OK)**:
```json
{
  "enabled": false,
  "jobs_active": 0,
  "evals_run": 0
}
```

---

#### POST /api/trainer/jobs

Create a new training job.

**Request**:
```json
{
  "task": "sft",
  "dataset": "conversations"
}
```

**Response (201 Created)**:
```json
{
  "job_id": "train-123",
  "status": "pending"
}
```

---

#### GET /api/quantum/status

Get quantum subsystem status.

**Response (200 OK)**:
```json
{
  "available": false,
  "mode": "classical",
  "backend": null
}
```

---

#### GET /api/qfac/admin/show

Get QFAC compression system status (admin).

**Response (200 OK)**:
```json
{
  "mode": "classical",
  "nodes_compressed": 0,
  "compression_ratio": 1.0
}
```

---

#### POST /api/qfac/admin/reset

Reset QFAC system state (admin).

**Response (200 OK)**:
```json
{
  "ok": true,
  "message": "QFAC system reset"
}
```

---

### 🎨 Consciousness APIs

#### GET /api/consciousness/state

Get current consciousness state snapshot.

**Response (200 OK)**:
```json
{
  "tick_id": 12345,
  "mode": "active",
  "focus": "system_monitoring",
  "emotional_valence": 0.7,
  "confidence": 0.85,
  "recent_thoughts": [
    "System health is good",
    "No anomalies detected"
  ]
}
```

---

### 📊 Observability APIs

#### GET /api/stats

Get general Hub statistics.

**Response (200 OK)**:
```json
{
  "uptime": 86400.5,
  "requests_handled": 15234,
  "telemetry_received": 523,
  "services_registered": 8,
  "lyrixa_chat": {
    "registered": true,
    "status": "healthy"
  }
}
```

---

#### GET /metrics

Get Prometheus-format metrics for all subsystems.

**Response (200 OK)**: `text/plain; version=0.0.4`

```
# HELP aetherra_kernel_cycle_count Kernel loop cycles
# TYPE aetherra_kernel_cycle_count counter
aetherra_kernel_cycle_count 144000

# HELP aetherra_memory_queries_total Total memory queries
# TYPE aetherra_memory_queries_total counter
aetherra_memory_queries_total 5234

# ... (hundreds of metrics)
```

---

#### GET /api/site_status

Get site/system status page information.

**Response (200 OK)**:
```json
{
  "status": "operational",
  "version": "0.5.0",
  "components": {
    "kernel": "healthy",
    "memory": "healthy",
    "hub": "healthy"
  }
}
```

---

#### POST /api/telemetry

Submit telemetry event (opt-in only).

**Request**:
```json
{
  "event_type": "usage",
  "data": {
    "feature": "memory_query",
    "duration_ms": 45
  }
}
```

**Response (202 Accepted)**:
```json
{
  "received": true
}
```

---

### 🌐 Federation APIs

#### POST /api/peers/announce

Announce this Hub to peer network (federation).

**Response (501 Not Implemented)**:
```json
{
  "error": "Federation not yet implemented"
}
```

---

#### POST /api/peers/sync

Sync data with peer Hubs.

**Response (501 Not Implemented)**:
```json
{
  "error": "Federation not yet implemented"
}
```

---

### 📖 Documentation APIs

#### GET /api/openapi.json

Get OpenAPI 3.0 specification for all Hub APIs.

**Response (200 OK)**: Full OpenAPI schema document

---

#### GET /

Serve frontend application (when frontend enabled).

**Response (200 OK)**: HTML page

---

## Rate Limiting

Currently, rate limiting is **not enforced** at the Hub level. Future versions may implement:

- Per-IP rate limits
- Per-token rate limits (when authentication enabled)
- Endpoint-specific limits

**Recommended client behavior**:
- Implement exponential backoff for retries
- Cache responses when appropriate
- Use streaming endpoints for long-running operations

---

## Performance Considerations

### Best Practices

1. **Use streaming endpoints** for long-running AI queries
2. **Batch operations** when possible (e.g., batch self-improvement proposals)
3. **Poll status endpoints** at reasonable intervals (5-10 seconds minimum)
4. **Cache static data** (plugin lists, agent capabilities)
5. **Use WebSocket** for real-time bidirectional communication

### Timeouts

Recommended client timeouts:

- **Short operations** (status checks): 5 seconds
- **Medium operations** (AI queries): 30 seconds
- **Long operations** (script execution): 300 seconds
- **Streaming**: No timeout (keep-alive)

---

## Security Considerations

### CORS

CORS headers are configured based on Hub settings. Local development typically allows `http://localhost:*`.

### HTTPS/TLS

For production deployments:
- Use reverse proxy (nginx, Caddy) for TLS termination
- Enable `AETHERRA_NET_STRICT=1` for network allowlist enforcement
- Set `AETHERRA_NETWORK_ALLOWLIST` appropriately

### Token Security

When authentication is enabled:
- Tokens should be treated as secrets
- Use environment variables, never hardcode
- Rotate tokens regularly
- Use HTTPS in production

---

## Related Documentation

- [AETHERRA_SELF_IMPROVEMENT_API.md](./AETHERRA_SELF_IMPROVEMENT_API.md) - Detailed Self-Improvement endpoints
- [AETHERRA_WEBSOCKET_API.md](./AETHERRA_WEBSOCKET_API.md) - WebSocket and SSE protocols (coming soon)
- [AETHERRA_AGENT_SYSTEM.md](./AETHERRA_AGENT_SYSTEM.md) - Agent orchestration system
- [AETHERRA_MAINTENANCE_SYSTEM.md](./AETHERRA_MAINTENANCE_SYSTEM.md) - Maintenance subsystems
- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - API troubleshooting (coming soon)

---

## Appendix: Quick Reference

### Environment Variables

| Variable                        | Default             | Description                        |
| ------------------------------- | ------------------- | ---------------------------------- |
| `AETHERRA_HUB_PORT`             | 3001                | Hub server port                    |
| `AETHERRA_AI_API_ENABLED`       | 0                   | Enable AI API endpoints            |
| `AETHERRA_AI_API_REQUIRE_TOKEN` | 0                   | Require authentication for AI APIs |
| `AETHERRA_AI_API_TOKEN`         | -                   | Authentication token               |
| `AETHERRA_AGENTS_API_ENABLED`   | 1                   | Enable agent orchestration APIs    |
| `AETHERRA_NET_STRICT`           | 0                   | Enforce network allowlist          |
| `AETHERRA_NETWORK_ALLOWLIST`    | localhost,127.0.0.1 | Allowed network hosts              |

### Common Response Headers

```
Content-Type: application/json
X-Hub-Version: 0.5.0
X-Request-Id: req-abc-123
Access-Control-Allow-Origin: *
```

### HTTP Methods Summary

| Method | Usage                                    |
| ------ | ---------------------------------------- |
| GET    | Retrieve resources, read-only operations |
| POST   | Create resources, trigger actions        |
| PUT    | Update resources (full replacement)      |
| PATCH  | Update resources (partial modification)  |
| DELETE | Remove resources                         |

---

Status: ✅ Complete - Comprehensive API reference for 50+ endpoints across 15 categories

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
