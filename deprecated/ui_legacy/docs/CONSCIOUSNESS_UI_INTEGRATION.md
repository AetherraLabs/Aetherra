# Consciousness UI Integration — Wiring Guide

This document describes how the consciousness system is wired to the Lyrixa UI for real-time visualization.

## Architecture Overview

```
┌─────────────────────┐
│ ConsciousnessCore   │ ← tick() loop: perceive→appraise→attend→intend→reflect
│ (always-on)         │
└──────────┬──────────┘
           │
           ├──→ ThinkStream._ui_callback()
           │    (state snapshot generation)
           │
           ▼
┌─────────────────────────────────┐
│ aetherra_hub/blueprints/        │
│   consciousness.py              │
│                                 │
│ _update_state_snapshot()        │
│ (stores latest qualia/focuses)  │
└──────────┬──────────────────────┘
           │
           │ GET /api/consciousness/state
           │
           ▼
┌─────────────────────────────────┐
│ Lyrixa GUI                      │
│   ConsciousnessMonitor.tsx      │
│                                 │
│ useApiPoll(..., 2000ms)         │
│ (live qualia bars, focuses list,│
│  intentions, narrative stream)  │
└─────────────────────────────────┘
```

## Components Created

### 1. Frontend Component
**File**: `Aetherra/lyrixa/gui/src/components/ConsciousnessMonitor.tsx`

React component that:
- Polls `/api/consciousness/state` every 2 seconds
- Displays qualia vector with 6 dimensions (valence, arousal, certainty, curiosity, care, fatigue)
- Shows current attention focuses (top-k resonance-sorted events)
- Lists active intentions with priority and blocked status
- Streams narrative moments (significant consciousness reflections)

**Usage**: Navigate to "Consciousness" in the Lyrixa GUI sidebar

### 2. Backend API Endpoint
**File**: `aetherra_hub/blueprints/consciousness.py`

Flask blueprint that:
- Exposes `GET /api/consciousness/state` endpoint
- Returns JSON snapshot of current consciousness state
- Provides offline fallback when consciousness system not running
- Includes `register_think_stream()` function for wiring ThinkStream callbacks

**Registered**: Automatically loaded in `aetherra_hub/app.py` BLUEPRINTS list

### 3. Integration Point
**File**: `Aetherra/consciousness/core/think_stream.py`

ThinkStream has `_ui_callback` and `_telemetry_callback` hooks:
```python
def on_tick(self, core: ConsciousnessCore):
    state = self._build_state_snapshot(core)
    if self._ui_callback:
        self._ui_callback(state)  # ← Sends to Hub API
```

## Running the System

### Step 1: Start Consciousness Loop
```bash
python Aetherra/runners/run_consciousness.py
```

This starts:
- PerceptionBus with OS adapters (WindowsProcAdapter, LinuxProcAdapter, etc.)
- ConsciousnessCore tick loop at AETHERRA_CONSCIOUSNESS_HZ (default 2 Hz)
- ThinkStream for state snapshots
- Actuator with safety envelope and policy engine

### Step 2: Wire ThinkStream to Hub API
Add to `run_consciousness.py` before main loop:

```python
# Import the blueprint's registration function
try:
    from aetherra_hub.blueprints.consciousness import register_think_stream
    register_think_stream(think_stream)
    print("[CONSCIOUSNESS] ThinkStream wired to Hub API")
except ImportError:
    print("[CONSCIOUSNESS] Hub API not available - UI callbacks disabled")
```

This registers `_update_state_snapshot()` as the UI callback so each tick updates the Hub's state.

### Step 3: Start Aetherra Hub
```bash
python tools/run_hub_ai_api.py --port 3001
```

The Hub will now expose `GET /api/consciousness/state` with live data.

### Step 4: Start Lyrixa GUI
```bash
cd Aetherra/lyrixa/gui
npm run dev
```

Navigate to http://localhost:5173 and click "Consciousness" in the sidebar.

## State Schema

### Qualia Vector
```typescript
{
  valence: number;       // -1 (bad) to +1 (good)
  arousal: number;       // 0 (calm) to 1 (excited)
  certainty: number;     // 0 (uncertain) to 1 (certain)
  curiosity: number;     // 0 (none) to 1 (high)
  care: number;          // 0 (detached) to 1 (engaged)
  fatigue: number;       // 0 (fresh) to 1 (tired)
}
```

### Focus
```typescript
{
  source: string;        // e.g., "PROC_SNAPSHOT"
  target: string;        // e.g., "python.exe"
  resonance: number;     // 0.0 to 1.0 importance
  why: string;           // Human-readable reason
}
```

### Intent
```typescript
{
  goal: string;          // e.g., "Maintain system stability"
  priority: number;      // Urgency score
  blocked: boolean;      // Permission check failed
  why: string;           // Reason for intent
}
```

### Narrative Moment
```typescript
{
  tick_id: number;
  timestamp: string;     // ISO 8601
  summary: string;       // Micro-reflection text
  significant: boolean;  // Logged to QFAC if true
}
```

## Autonomy Modes

From `Aetherra/safety_envelope/policy_engine.py`:

1. **observe-only**: No actions allowed (consciousness aware but passive)
2. **suggest-only**: Can propose actions but requires human approval
3. **gated**: Limited autonomy within pre-approved capability set
4. **full**: Unrestricted autonomy (use with extreme caution)

Displayed in UI badge next to consciousness status.

## QFAC Integration

Significant narrative moments (where `significant=true`) are automatically stored to QFAC:

```python
# From consciousness_core.py _reflect_micro()
if narrative.significant:
    from Aetherra.aetherra_core.memory.qfac.qfac_api import qfac_store
    qfac_store(tag="consciousness_narrative",
               text=narrative.summary,
               metadata={"tick": narrative.tick_id})
```

This ensures consciousness reflections are preserved in episodic memory for future recall.

## Polling Frequency

Frontend polls `/api/consciousness/state` every 2 seconds by default:
```typescript
const consciousnessData = useApiPoll<ConsciousnessState>("/api/consciousness/state", 2000);
```

Consciousness loop runs at 2 Hz (configurable via `AETHERRA_CONSCIOUSNESS_HZ`).

## Offline Behavior

When consciousness system is not running:
- API returns 503 Service Unavailable
- Frontend displays "OFFLINE" badge
- All metrics show zero/empty state
- Narrative stream shows connection message

## Zero Simulation Principle

All displayed data comes from **real perception events**:
- No mocked metrics
- No simulated telemetry
- No placeholder values

If the perception bus receives no events, the UI will show minimal activity. This is correct behavior — awareness without stimulus is quiescence.

## Troubleshooting

**Problem**: UI shows "OFFLINE" even after starting run_consciousness.py

**Solution**: Ensure you've added the `register_think_stream()` call to wire the callback. Check terminal for "[CONSCIOUSNESS] ThinkStream wired to Hub API" message.

**Problem**: Qualia values never change from 0.0

**Solution**: Verify perception adapters are running and publishing events. Check Windows PowerShell permissions or Linux /proc access. Set `AETHERRA_CONSCIOUSNESS_HZ=0.5` to see slower evolution.

**Problem**: Narrative stream is empty

**Solution**: Narrative moments only appear when consciousness appraises events as significant. Trigger activity (e.g., run plugins, execute .aether scripts) to generate stimulation.

## Development Notes

- ThinkStream callbacks are optional (system runs headless without UI)
- Multiple frontends can poll the same endpoint
- State snapshots are immutable (no threading issues)
- Narrative accumulates in memory (consider periodic cleanup for long runs)

## Related Files

- `Aetherra/consciousness/core/types.py` - Dataclass definitions
- `Aetherra/consciousness/core/config.py` - Environment-based settings
- `Aetherra/consciousness/core/consciousness_core.py` - Main tick loop
- `Aetherra/perception_bus/adapters/windows.py` - Windows telemetry
- `Aetherra/perception_bus/adapters/linux.py` - Linux telemetry
- `Aetherra/safety_envelope/actuator.py` - Action execution with rollback
- `docs/CONSCIOUSNESS_PHASE1_COMPLETE.md` - Architecture documentation
