# Aetherra Self-Improvement API

Updated: 2026-06-17

This document describes the Self-Improvement API endpoints exposed by the Aetherra Hub, which enable manual approval and application of autonomously generated improvement proposals. These endpoints integrate with the Lyrixa GUI Self-Improve tab and support both Hot Module Reload (HMR) and manual OS restart workflows.

## Purpose and scope

- Define the REST API contract for applying self-improvement proposals
- Document harmonized HTTP status codes and response schemas
- Explain the `restart_required` flag semantics and HMR integration
- Provide guidance for UI integration and error handling
- Document batch operations and approval workflows

## Architecture overview

The Self-Improvement API is part of the Aetherra Maintenance System autonomous feedback loop:

1. **Homeostasis System** monitors OS health and detects performance issues
2. **Self-Improvement Engine** generates optimization proposals based on metrics
3. **Self-Improvement API** (this document) enables manual review and approval via GUI
4. **Hot Module Reload (HMR) Controller** applies approved proposals at runtime when enabled
5. **Self-Incorporation Service** integrates changes and reports outcomes back to metrics

The API provides a human-in-the-loop gate for proposal application, ensuring safe evolution with user oversight.

## Endpoints

### GET /api/selfimprove/status

Return read-only self-improvement engine status.

**Success response (HTTP 200):**

```json
{
  "improvement_active": true,
  "total_proposals": 3,
  "active_proposals": 3,
  "implemented_proposals": 0,
  "learning_outcomes": 0,
  "tracked_metrics": 8,
  "analysis_cycles": 12,
  "autonomous_implementation_enabled": false,
  "autonomous_implementation_requested": false,
  "implementation_authority": "guardian_controlled_execution"
}
```

`autonomous_implementation_enabled` remains `false` for the foundation milestone. If the legacy
`AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT=1` environment flag is present, the status response reports
`autonomous_implementation_requested: true`, but generated proposals remain reviewable recommendations until a
Guardian-gated controlled execution path handles application.

### GET /api/selfimprove/proposals

List active improvement proposals without applying them.

Supported query parameters:

- `status`
- `type` or `improvement_type`
- `readiness` or `readiness_status`
- `max_risk`
- `min_confidence`
- `limit`

**Success response (HTTP 200):**

```json
{
  "status": "ok",
  "summary": {
    "total_reviewable": 3,
    "by_status": {"active": 3},
    "by_type": {"performance": 2, "reliability": 1},
    "by_readiness": {"candidate": 2, "needs_evidence": 1},
    "risk_bands": {"low": 2, "medium": 1, "high": 0}
  },
  "proposals": [
    {
      "proposal_id": "SI-42",
      "improvement_type": "performance",
      "description": "Optimize memory retrieval indexing",
      "expected_benefit": 0.15,
      "implementation_cost": 0.2,
      "risk_level": 0.1,
      "affected_components": ["memory"],
      "success_criteria": ["retrieval latency improves"],
      "issue": "Memory retrieval latency is increasing",
      "potential_cause": "Index pressure or retrieval path contention",
      "proposed_change": "Simulate and review memory index tuning",
      "evidence": ["metric:memory_rtt", "trend:degrading"],
      "simulation": {
        "estimated_impact": 0.15,
        "implementation_cost": 0.2,
        "risk_level": 0.1,
        "confidence": 0.785,
        "testable": true,
        "rollback_available": true,
        "recommendation": "candidate"
      },
      "rollback_plan": "Restore prior memory index configuration",
      "proposal_fingerprint": "ab12cd34ef56...",
      "occurrence_count": 2,
      "readiness_status": "candidate",
      "readiness_reasons": ["ready_for_review"],
      "status": "active"
    }
  ]
}
```

### GET /api/selfimprove/proposals/{proposal_id}

Return one active improvement proposal without applying it. Terminal proposals are not returned through this
active-review endpoint.

**Success response (HTTP 200):**

```json
{
  "status": "ok",
  "proposal": {
    "proposal_id": "SI-42",
    "status": "active",
    "issue": "Memory retrieval latency is increasing",
    "simulation": {
      "confidence": 0.785,
      "testable": true,
      "rollback_available": true
    }
  }
}
```

**Not found response (HTTP 404):**

```json
{
  "status": "not_found",
  "proposal": null
}
```

### GET /api/selfimprove/proposals/{proposal_id}/history

Return bounded review lifecycle history for one proposal.

**Success response (HTTP 200):**

```json
{
  "status": "ok",
  "proposal_id": "SI-42",
  "events": [
    {
      "proposal_id": "SI-42",
      "event_type": "dismissed",
      "from_status": "active",
      "to_status": "dismissed",
      "actor": "operator",
      "reason": "Not useful for the current milestone",
      "timestamp": "2026-06-17T00:00:00",
      "metadata": {}
    }
  ]
}
```

### POST /api/selfimprove/proposals/{proposal_id}/dismiss

Dismiss a reviewable proposal without applying it. Requires Hub control authorization.

**Request body:**

```json
{
  "reason": "Not useful for the current milestone"
}
```

**Success response (HTTP 200):**

```json
{
  "ok": true,
  "status": "ok",
  "proposal_id": "SI-42",
  "proposal_status": "dismissed"
}
```

### POST /api/selfimprove/proposals/{proposal_id}/reopen

Reopen a dismissed proposal for active review. Requires Hub control authorization.

**Request body:**

```json
{
  "reason": "Reconsider after new evidence"
}
```

**Success response (HTTP 200):**

```json
{
  "ok": true,
  "status": "ok",
  "proposal_id": "SI-42",
  "proposal_status": "active"
}
```

Lifecycle endpoints mutate only proposal review state. They do not apply proposals, modify code, reload modules,
or bypass Guardian. Applying a proposal still requires `/api/selfimprove/apply` or `/batch-apply`.

### GET /api/selfimprove/learning/outcomes

Return bounded, sanitized learning outcomes recorded after controlled downstream execution.

Supported query parameters:

- `proposal_id`
- `status`
- `limit`

The response does not include raw execution payload values. It exposes only proposal linkage, outcome status,
numeric outcome metadata, and the names of result detail fields that were present.

**Success response (HTTP 200):**

```json
{
  "status": "ok",
  "summary": {
    "total_outcomes": 1,
    "by_status": {"accepted": 1},
    "average_improvement_achieved": 0.25
  },
  "outcomes": [
    {
      "session_id": "session-1",
      "method": "reinforcement",
      "target_component": "memory",
      "improvement_achieved": 0.25,
      "confidence": 1.0,
      "timestamp": "2026-06-17T00:00:00",
      "proposal_id": "SI-42",
      "plan_id": "plan-1",
      "status": "accepted",
      "details_keys": ["improvement_achieved", "raw_payload"]
    }
  ]
}
```

### GET /api/selfimprove/trends

Return read-only metric trends from the self-improvement engine.

**Success response (HTTP 200):**

```json
{
  "status": "ok",
  "trends": {
    "response_time": {
      "trend_direction": "degrading",
      "trend_value": 0.04,
      "statistics": {}
    }
  }
}
```

### POST /api/selfimprove/apply

Apply a single improvement proposal with optional HMR-based hot reload.

**Request body:**

```json
{
  "proposal_id": "string",          // Required: Unique ID of proposal to apply
  "force": false,                   // Optional: Skip safety checks (default: false)
  "user": "string"                  // Optional: User ID for audit trail
}
```

**Success response (HTTP 200):**

```json
{
  "ok": true,
  "status": "approved",             // Proposal approved
  "message": "Proposal applied successfully via HMR",
  "restart_required": false,        // HMR applied, no restart needed
  "proposal_id": "string"
}
```

**Success response (HTTP 200 - HMR unavailable):**

```json
{
  "ok": true,
  "status": "approved",
  "message": "Proposal approved - HMR not available, OS restart required",
  "restart_required": true,         // Manual OS restart needed
  "proposal_id": "string"
}
```

**Error response (HTTP 400):**

```json
{
  "ok": false,
  "error": "string",                // Error description
  "details": "string"               // Optional: Additional error context
}
```

**Response codes:**

- **200 OK**: Proposal approved (may require restart based on `restart_required` flag)
- **400 Bad Request**: Invalid request, proposal application failed, or HMR error

**Restart required semantics:**

| HMR Status          | Applied | restart_required | HTTP Code | UI Behavior                      |
| ------------------- | ------- | ---------------- | --------- | -------------------------------- |
| Enabled & available | Yes     | `false`          | 200       | Show success, no restart badge   |
| Unavailable         | No      | `true`           | 200       | Show "OS Restart Required" badge |
| Error during apply  | No      | `true`           | 400       | Show error message               |
| Disabled            | No      | `true`           | 200       | Show "OS Restart Required" badge |

### POST /api/selfimprove/batch-apply

Apply multiple improvement proposals in a single operation.

**Request body:**

```json
{
  "proposal_ids": ["string", ...],  // Required: Array of proposal IDs
  "force": false,                   // Optional: Skip safety checks (default: false)
  "user": "string"                  // Optional: User ID for audit trail
}
```

The endpoint also accepts expanded proposal objects when per-proposal metadata is needed:

```json
{
  "proposals": [
    {
      "proposal_id": "string",
      "method": "auto",
      "description": "string",
      "rollback_plan": "string"
    }
  ],
  "user": "string"
}
```

**Success response (HTTP 200):**

```json
{
  "ok": true,
  "applied": 3,                     // Count of successfully applied proposals
  "failed": 1,                      // Count of failed proposals
  "restart_required": true,         // Any proposal requiring restart?
  "results": [
    {
      "proposal_id": "string",
      "ok": true,
      "status": "approved",
      "message": "Applied via HMR",
      "restart_required": false
    },
    {
      "proposal_id": "string",
      "ok": false,
      "error": "Application failed",
      "restart_required": true
    }
  ]
}
```

**Response codes:**

- **200 OK**: Batch operation completed (check individual results for per-proposal status)
- **400 Bad Request**: Invalid request format or critical error

**Batch semantics:**

- Batch operation continues even if individual proposals fail
- Global `restart_required` is `true` if **any** proposal requires restart
- Individual results include per-proposal `restart_required` flags
- Empty `proposal_ids` array returns 400 Bad Request

## Status code harmonization

Prior to 2025-01-26, the Self-Improvement API used multiple HTTP status codes to signal different outcomes (503 for HMR unavailable, 502 for selfinc failure, 500 for HMR errors). This created complexity in client logic and violated REST conventions.

**Current harmonized approach:**

1. **HTTP 200**: Proposal approved (check `restart_required` flag to determine if OS restart needed)
2. **HTTP 400**: Request invalid or proposal application failed

**Benefits:**

- Simplified client logic: Check `body.ok` and `restart_required` flag only
- RESTful semantics: 2xx for success, 4xx for client errors
- Single source of truth: `restart_required` flag drives UI behavior

**Migration note:** Clients previously checking `res.status === 503` should now check `body.restart_required === true`.

## Hot Module Reload (HMR) integration

## Service registry messages

The Self-Improvement Engine also supports internal service-registry messages:

- `selfimprovement.record_metric`: record a performance metric.
- `selfimprovement.status`: return read-only engine status.
- `selfimprovement.trends`: return read-only metric trends.
- `selfimprovement.proposals`: return active proposals.
- `selfimprovement.proposal_history`: return bounded lifecycle history for a proposal.
- `selfimprovement.learning_outcomes`: return bounded sanitized downstream outcome history.
- `selfimprovement.proposal_result`: record a bounded downstream outcome after controlled execution.

`selfimprovement.proposal_result` records proposal ID, plan ID, status, numeric improvement, and result detail
keys. It does not copy raw execution payload values into the learning record.

HMR enables runtime application of approved proposals without OS restart. When HMR is enabled and available, the Self-Improvement API will attempt to apply proposals via the HMR Controller.

### Enabling HMR

Set these environment variables before launching Aetherra OS:

```bash
export AETHERRA_HMR_ENABLED=1          # Enable HMR system
export AETHERRA_HMR_MODE=safe          # Use safe reload mode
export AETHERRA_HMR_AUTO_RELOAD=1      # Auto-reload on file changes
```

Or in PowerShell:

```powershell
$env:AETHERRA_HMR_ENABLED = "1"
$env:AETHERRA_HMR_MODE = "safe"
$env:AETHERRA_HMR_AUTO_RELOAD = "1"
```

### HMR availability detection

The API checks HMR availability before applying proposals:

1. **HMR enabled**: `restart_required: false` when successfully applied
2. **HMR unavailable**: `restart_required: true`, user must manually restart OS
3. **HMR error**: HTTP 400 with error details

### HMR safety guarantees

- **Safe mode**: Only applies proposals passing safety validation
- **Rollback**: Automatic rollback on application errors
- **Audit trail**: All HMR operations logged to kernel metrics
- **SLO monitoring**: Homeostasis monitors post-application health

## UI integration

The Lyrixa GUI Self-Improve tab integrates with this API to provide manual proposal review and approval.

### Workflow

1. **Fetch proposals**: UI calls `GET /api/selfimprove/proposals` to list pending proposals
2. **User review**: Proposals displayed with title, description, and metrics
3. **Approval**: User clicks "Approve" button on selected proposal
4. **Apply**: UI calls `POST /api/selfimprove/apply` with proposal ID
5. **Check result**:
   - If `ok: true` and `restart_required: false`: Show success (HMR applied)
   - If `ok: true` and `restart_required: true`: Show "OS Restart Required" badge
   - If `ok: false`: Show error message

### React example (App.tsx)

```typescript
const approveSuggestion = async (proposalId: string) => {
  try {
    const res = await fetch('/api/selfimprove/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ proposal_id: proposalId })
    });

    const body = await res.json();

    if (body && body.ok === true) {
      // Proposal approved successfully
      if (body.restart_required) {
        // Show "OS Restart Required" badge
        showRestartBadge(proposalId);
      } else {
        // HMR applied, no restart needed
        showSuccess("Proposal applied successfully");
      }
    } else {
      // Application failed
      showError(body.error || "Application failed");
    }
  } catch (err) {
    showError("Network error: " + err.message);
  }
};
```

### Batch approval example

```typescript
const approveMultiple = async (proposalIds: string[]) => {
  const res = await fetch('/api/selfimprove/batch-apply', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ proposal_ids: proposalIds })
  });

  const body = await res.json();

  if (body.ok) {
    console.log(`Applied: ${body.applied}, Failed: ${body.failed}`);

    if (body.restart_required) {
      showRestartBadge("multiple");
    }

    // Process individual results
    body.results.forEach(result => {
      if (result.ok) {
        updateProposalStatus(result.proposal_id, "approved");
      } else {
        showProposalError(result.proposal_id, result.error);
      }
    });
  }
};
```

## Error handling

### Common error scenarios

**Invalid proposal ID:**

```json
{
  "ok": false,
  "error": "Proposal not found",
  "details": "proposal_id 'invalid-id' does not exist"
}
```

**HMR application error:**

```json
{
  "ok": false,
  "error": "HMR application failed",
  "details": "Module reload failed: ImportError in target module"
}
```

**Self-Incorporation service unavailable:**

```json
{
  "ok": false,
  "error": "Self-Incorporation service not available",
  "details": "Cannot apply proposal without selfinc service"
}
```

### Client retry strategy

- **400 Bad Request**: Do not retry (client error)
- **500 Internal Server Error**: Retry with exponential backoff
- **Network errors**: Retry up to 3 times with exponential backoff

## Security and audit

### Authorization

- Proposals require manual user approval via GUI
- Batch operations limited to 10 proposals per request
- `force` flag requires elevated privileges (planned)

### Audit trail

All proposal applications are logged with:

- Timestamp
- User ID (if provided)
- Proposal ID
- Application outcome
- HMR status
- Restart required flag

Audit logs available via kernel metrics and Homeostasis reporting.

## Configuration

### Environment variables

- `AETHERRA_HMR_ENABLED`: Enable HMR system (default: 0)
- `AETHERRA_HMR_MODE`: HMR mode (safe/aggressive, default: safe)
- `AETHERRA_HMR_AUTO_RELOAD`: Auto-reload on file changes (default: 0)
- `AETHERRA_SELFINC_STRICT`: Require signed proposals (default: 0)

### Runtime configuration

Configuration available via `config.json`:

```json
{
  "self_improvement": {
    "enabled": true,
    "hmr_enabled": true,
    "hmr_mode": "safe",
    "batch_limit": 10,
    "require_approval": true
  }
}
```

## Observability

### Metrics

Self-Improvement API metrics exposed via `/metrics` endpoint:

- `aetherra_selfimprove_apply_total`: Total apply attempts (labels: status, restart_required)
- `aetherra_selfimprove_apply_duration_seconds`: Apply operation duration
- `aetherra_selfimprove_hmr_success_total`: Successful HMR applications
- `aetherra_selfimprove_hmr_error_total`: Failed HMR applications

### Health checks

Check Self-Improvement Engine status:

```bash
GET /api/stats
```

Response includes:

```json
{
  "self_improvement_engine": {
    "enabled": true,
    "status": "idle",
    "proposals_pending": 3
  }
}
```

## Related documentation

- [AETHERRA_MAINTENANCE_SYSTEM.md](./AETHERRA_MAINTENANCE_SYSTEM.md): Overall maintenance architecture
- [AETHERRA_LYRIXA_SYSTEM.md](./AETHERRA_LYRIXA_SYSTEM.md): Lyrixa UI integration
- [AETHERRA_AGENT_SYSTEM.md](./AETHERRA_AGENT_SYSTEM.md): Agent orchestration and task lifecycle

## Appendices

### Complete response schema

**ApplyResponse:**

```typescript
interface ApplyResponse {
  ok: boolean;              // Operation success
  status?: string;          // "approved" | "rejected" | "error"
  message: string;          // Human-readable outcome
  restart_required: boolean; // OS restart needed?
  proposal_id: string;      // Applied proposal ID
  error?: string;           // Error message if ok: false
  details?: string;         // Additional error context
}
```

**BatchApplyResponse:**

```typescript
interface BatchApplyResponse {
  ok: boolean;              // Overall operation success
  applied: number;          // Count of successful applications
  failed: number;           // Count of failures
  restart_required: boolean; // Any proposal requiring restart?
  results: ApplyResponse[]; // Per-proposal results
}
```

### Example curl commands

**Apply single proposal:**

```bash
curl -X POST http://localhost:3001/api/selfimprove/apply \
  -H "Content-Type: application/json" \
  -d '{"proposal_id": "prop-123", "user": "admin"}'
```

**Batch apply:**

```bash
curl -X POST http://localhost:3001/api/selfimprove/batch-apply \
  -H "Content-Type: application/json" \
  -d '{"proposal_ids": ["prop-123", "prop-456"], "user": "admin"}'
```

---

Status: ✅ Implemented (harmonized status codes, restart_required flag, HMR integration, batch operations)

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
