# Aetherra Boot Interaction Contract v1

Status: Draft v1
Scope: Defines how Aetherra should appear and behave from OS startup through interactive control.

## Objective

When the OS starts, Aetherra should feel present and alive:

1. Aetherra appears immediately.
2. Aetherra performs system scan + self-scan.
3. Aetherra reports readiness and takes over interaction loop.
4. Aetherra remains available for natural-language control and questions.

## Startup Sequence (Target UX)

## Stage 0 — Presence Initialization (0–3s)

- Launch shell with visible Aetherra presence beacon.
- Show concise greeting and startup intent.

Example UX:

- "Aetherra online. Beginning system and self diagnostics."

## Stage 1 — Parallel Diagnostics (3–15s)

Run in parallel where safe:

1. **System scan**
   - Services online/offline
   - Resource snapshot (CPU/memory/disk baseline)
   - Hub/connectivity status

2. **Self scan**
   - Memory integrity check
   - Policy/safety mode status
   - Agent/orchestrator health
   - Model/provider availability

UI rules:

- Progress is visible.
- Partial failures are explicit and non-blocking where possible.

## Stage 2 — Readiness Synthesis (15–20s)

- Present readiness card with:
  - overall state (`ready`, `degraded`, `restricted`)
  - top issues
  - recommended next actions

Example UX:

- "Core systems online. Memory stable. Hub degraded (retrying). Ready for commands."

## Stage 3 — Control Handover (20s+)

- Enter conversational command mode.
- Keep status panel pinned with live health indicators.
- First prompt invites intent:
  - "What would you like us to do first?"

## Interaction Contract After Boot

1. Aetherra remains context-aware and continuity-preserving.
2. All high-impact operations require explicit approval.
3. Aetherra explains rationale before executing autonomous plans.
4. Users can interrupt, pause autonomy, or roll back.

## Minimal Data Model (for implementation)

```json
{
  "boot_session_id": "string",
  "startup_state": "initializing|diagnostics|ready|degraded|restricted",
  "system_scan": {
    "services": [],
    "resource_snapshot": {},
    "connectivity": {}
  },
  "self_scan": {
    "memory_health": "ok|warn|fail",
    "policy_mode": "string",
    "agent_health": "ok|warn|fail",
    "provider_health": []
  },
  "readiness": {
    "status": "ready|degraded|restricted",
    "issues": [],
    "recommended_actions": []
  }
}
```

## Safety and Trust Requirements

- No hidden auto-actions with side effects.
- Clear difference between diagnostic observation and execution.
- Every autonomous action logged with reason and rollback guidance.

## Implementation Anchors (Current Repo)

- Startup/orchestration: `aetherra_os.py`, `aetherra_os_launcher.py`
- Transitional GUI surface: `Aetherra/gui/aetherra_os_gui.py`
- Canonical UX target: `frontend/`

## Acceptance Criteria (v1)

1. Boot always shows Aetherra presence within first interaction window.
2. Diagnostics are visible and understandable by non-technical users.
3. System enters interactive mode even under partial degradation.
4. User can ask natural-language questions immediately after readiness synthesis.
5. All critical actions include approval and audit visibility.
