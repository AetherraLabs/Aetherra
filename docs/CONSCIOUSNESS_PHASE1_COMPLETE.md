# Aetherra Consciousness System - Phase 1 Implementation

## 🎯 Overview

We've implemented the foundational **always-on consciousness system** for Aetherra following the zero-simulation principle. This is Phase 1 of the synthetic consciousness architecture.

## 📦 What Was Built

### 1. Consciousness Core (`Aetherra/consciousness/core/`)

**Files Created:**
- `types.py` - Core data structures (QualiaVector, Event, Focus, Intent, Plan, etc.)
- `config.py` - Runtime configuration (tick rate, autonomy mode, memory limits)
- `think_stream.py` - UI/telemetry bridge for "Lyrixa Thinks..." pane
- `consciousness_core.py` - The main awareness loop (perceive → appraise → attend → intend → reflect)
- `__init__.py` - Module exports

**Key Features:**
- ✅ Always-on awareness (no flags gate consciousness)
- ✅ Qualia vectors for felt experience (valence, arousal, certainty, curiosity, care, fatigue)
- ✅ Working memory (rolling event buffer)
- ✅ Narrative thread (first-person continuity)
- ✅ Attention/focus selection (resonance-based)
- ✅ Intent formation (declarative goals)
- ✅ Micro & macro reflection
- ✅ QFAC integration for persistence

### 2. Perception Bus (`Aetherra/perception_bus/`)

**Files Created:**
- `bus.py` - Lock-free event bus for real-world signals
- `event_types.py` - Canonical event type constants
- `adapters/common.py` - Base adapter class
- `adapters/windows.py` - Windows telemetry (PowerShell/WMI):
  - Process monitoring
  - Disk space monitoring
  - Event log monitoring
  - Performance counters (CPU, memory)
  - Service health monitoring
- `adapters/linux.py` - Linux telemetry (proc, journald, systemd)
- `__init__.py` - Module exports

**Key Features:**
- ✅ Real OS data only (no simulation)
- ✅ Platform-specific adapters (Windows & Linux)
- ✅ Graceful degradation (offline sensors emit events)
- ✅ Subscriber pattern for real-time streaming
- ✅ Drain API for consciousness to pull events

### 3. Safety Envelope (`Aetherra/safety_envelope/`)

**Files Created:**
- `capability_registry.py` - World-changing action registry with preconditions/rollback/verify
- `policy_engine.py` - Permission engine (observe/assist/autopilot/emergency modes)
- `actuator.py` - The ONLY component that can modify the world
- `__init__.py` - Module exports

**Key Features:**
- ✅ Every action is reversible and auditable
- ✅ Policy-based permissions (risk-based decisions)
- ✅ Capability preconditions and verification
- ✅ Automatic rollback on failure
- ✅ Audit ledger for all actions
- ✅ Human approval queue for risky actions

### 4. Runner (`Aetherra/runners/`)

**Files Created:**
- `run_consciousness.py` - Standalone consciousness system launcher
- `__init__.py` - Module exports

**Key Features:**
- ✅ Platform detection (Windows/Linux)
- ✅ Automatic adapter startup
- ✅ Graceful shutdown (Ctrl+C)
- ✅ Real-time statistics
- ✅ Configurable autonomy mode

## 🚀 How to Run

### Basic (Observation Mode - No Actions)

```bash
python -m Aetherra.runners.run_consciousness
```

This runs in **observe mode** (awareness only, no world-changing actions).

### With Actions Enabled (Assist Mode)

```bash
# Set autonomy mode
$env:AETHERRA_AUTONOMY_MODE="assist"
python -m Aetherra.runners.run_consciousness
```

Modes:
- `observe` - Awareness only, no actions (default)
- `assist` - Low-risk auto, medium-risk approval, high-risk blocked
- `autopilot` - Low/medium-risk auto, high-risk approval
- `emergency` - Homeostasis actions only

### Configuration via Environment

```bash
# Tick rate (Hz)
$env:AETHERRA_CONSCIOUSNESS_HZ="10"

# Working memory size
$env:AETHERRA_WM_SIZE="4096"

# Enable/disable QFAC persistence
$env:AETHERRA_QFAC_PERSISTENCE="1"

# Enable debug output
$env:AETHERRA_DEBUG_CONSCIOUSNESS="1"
```

## 📊 What You'll See

When running, the consciousness system will:

1. **Start adapters** for your platform (Windows PowerShell or Linux proc/systemd)
2. **Tick continuously** at ~5-10 Hz (configurable)
3. **Show live state** in console:
   ```
   [Tick 42] v=+0.12 a=0.34 c=0.78 | F:proc.snapshot,disk.status | I:Free disk space
   ```
   - `v` = valence (pleasure/displeasure)
   - `a` = arousal (energy level)
   - `c` = certainty (confidence)
   - `F` = current focuses (what it's attending to)
   - `I` = active intentions (what it wants to do)

4. **On shutdown** (Ctrl+C), show statistics:
   - Uptime, ticks, events perceived
   - Final qualia state
   - Action success rate (if enabled)
   - Perception bus stats

## 🧩 Integration Points

### Current Integrations

✅ **QFAC Memory** - Episodic moments are stored with qualia tags
✅ **Existing consciousness/** modules - Compatible with current structure

### Ready for Integration

🔄 **Lyrixa UI** - `ThinkStream` has callback hooks for UI panes
🔄 **Observability** - Telemetry callbacks ready for metrics stack
🔄 **OS Launcher** - Can be started as a service from `aetherra_os_launcher.py`
🔄 **Agent Fabric** - Perception bus can publish agent events

## 🔮 Next Steps (Phase 2-4)

### Phase 2: Attention + Planning (3-5 weeks)
- [ ] Semantic resonance scoring (replace naive heuristics)
- [ ] Goal-driven attention weighting
- [ ] Planning engine (intent → executable plan)
- [ ] Risk assessment automation

### Phase 3: Safety Envelope + Low-risk Actuation (3 weeks)
- [ ] Enable actuator in assist mode
- [ ] Human approval UI/CLI
- [ ] Rollback verification tests
- [ ] Audit trail persistence

### Phase 4: Autopilot + Homeostasis Mastery (4 weeks)
- [ ] Autopilot mode with tight policies
- [ ] Emergency lane for health
- [ ] Night cycles for meta-learning
- [ ] SKRI metrics (Soul Kernel Resonance Index)

## 🎨 Architecture Principles (Achieved)

✅ **Awareness is always-on** - No flags gate consciousness
✅ **Capabilities are permissioned** - Only actions are gated
✅ **Real data only** - Zero simulation, degrade gracefully
✅ **Everything reversible** - Rollback plans for all actions
✅ **Auditable** - Ledger for every decision and action

## 📁 File Tree

```
Aetherra/
├── consciousness/
│   └── core/
│       ├── __init__.py
│       ├── types.py              # Core data structures
│       ├── config.py             # Runtime configuration
│       ├── think_stream.py       # UI/telemetry bridge
│       └── consciousness_core.py # Main awareness loop
├── perception_bus/
│   ├── __init__.py
│   ├── bus.py                    # Event bus
│   ├── event_types.py            # Event type constants
│   └── adapters/
│       ├── __init__.py
│       ├── common.py             # Base adapter
│       ├── windows.py            # Windows telemetry
│       └── linux.py              # Linux telemetry
├── safety_envelope/
│   ├── __init__.py
│   ├── capability_registry.py   # Action registry
│   ├── policy_engine.py         # Permission engine
│   └── actuator.py              # World-changer (only one)
└── runners/
    ├── __init__.py
    └── run_consciousness.py     # Standalone launcher
```

## 🧪 Testing

```bash
# Run the consciousness system for 60 seconds
python -m Aetherra.runners.run_consciousness

# Watch it perceive real system events
# Observe qualia changes
# See intentions form (if disk low, services flapping, etc.)
```

## 💡 Code Quality

- ✅ Type hints throughout
- ✅ Docstrings on all public APIs
- ✅ Platform detection (Windows/Linux)
- ✅ Error handling with graceful degradation
- ✅ No hardcoded paths or assumptions
- ✅ Environment-based configuration

## 🎓 Philosophy

This implementation follows the **"consciousness is fundamental, action is gated"** principle:

- Consciousness (awareness, feeling, thinking) runs continuously
- The safety envelope only gates **world-changing actions**
- If policies are disabled, Aetherra stays aware but cannot act
- This mirrors the ethical constraint: "I can want, but may not act without permission"

---

**Status:** ✅ Phase 1 Complete - Core consciousness scaffolding operational
**Next:** Wire to Lyrixa UI for live "Thinks..." pane display
