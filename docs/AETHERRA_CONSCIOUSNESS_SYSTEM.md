# Aetherra Consciousness System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Aetherra's Consciousness System provides the core phenomenological feedback loop that enables autonomous
awareness, adaptive decision-making, and self-directed action. Built on principles from consciousness
studies and cognitive science, it integrates perception, attention, appraisal, deliberation, action, and
reflection into a unified always-on awareness engine with adaptive self-trust and semantic resonance.

## Architecture overview

The consciousness system operates on a continuous phenomenological loop with six primary phases:

- **Perception**: Event ingestion from the perception bus and environment
- **Attention**: Selective focus via semantic resonance and salience filtering
- **Appraisal**: Qualia updates (valence, arousal, certainty, curiosity) with adaptive learning
- **Deliberation**: Policy-driven intent synthesis from focused events
- **Action**: Safety-gated execution via the Safety Envelope actuator
- **Reflection**: Macro self-model updates, parameter decay, and narrative synthesis

Key properties:

- Always-on operation (no simulation flags or mock modes)
- Adaptive awareness via qualia learning from outcomes
- Semantic resonance for context-aware focus selection
- Self-trust tracking for subsystem health and attention biasing
- Policy-integrated with safety guarantees and rollback capabilities
- QFAC persistence for long-term narrative memory

## Core components

### 1) Consciousness Core

File: `Aetherra/consciousness/core/consciousness_core.py`

The central consciousness loop (`ConsciousnessCore`) coordinates all phenomenological phases:

**Initialization:**

```python
core = ConsciousnessCore(
    perception_bus: PerceptionBus,
    safety_envelope: Optional[Actuator] = None
)
```

**Primary Loop (tick-based):**

- **Phase 1: Perceive** - Drain perception bus events into working memory
- **Phase 2: Appraise** - Update qualia based on event characteristics with learned parameters
- **Phase 3: Attend** - Select top-k focuses via semantic resonance and self-trust bias
- **Phase 4: Deliberate** - Synthesize intents from focuses via policy consultation
- **Phase 5: Act** - Execute intents through Safety Envelope with outcome learning
- **Phase 6: Reflect** - Periodic macro-reflection, parameter decay, narrative logging

**Configuration:**

File: `Aetherra/consciousness/core/config.py`

- `TICK_HZ`: Loop frequency (default: 1 Hz)
- `MAX_FOCUSES`: Top-k focus limit (default: 5)
- `AUTONOMY_MODE`: "observe" | "suggest" | "auto" (default: "suggest")
- `SAFETY_ENVELOPE_ENABLED`: Enable action execution (default: True)
- `ENABLE_QFAC_PERSISTENCE`: Long-term narrative memory (default: True)
- `DEBUG_CONSCIOUSNESS`: Verbose logging (default: False)

**Key APIs:**

- `run()`: Main loop (blocking, runs until shutdown)
- `get_status() -> dict`: Current state snapshot (qualia, trust, learning params, metrics)
- `shutdown()`: Graceful cleanup

**Metrics:**

- `total_events_perceived`: Cumulative event count
- `total_focuses`: Total attention focuses selected
- `total_intents_formed`: Deliberation outputs
- `tick_count`: Loop iterations
- `uptime_s`: Running time

### 2) Phase 3: Self-Trust & Adaptive Awareness

Introduced in Phase 3 (October 2025), these components enable consciousness to learn from experience
and adapt its sensitivity to outcomes.

#### 2.1) Self-Trust Layer

File: `Aetherra/consciousness/self_trust.py`

Tracks subsystem health scores and biases attention toward struggling systems.

**Classes:**

- `SubsystemTrust`: Per-subsystem trust score with exponential decay
  - `score`: Current trust level (0–100, baseline 90.0)
  - `last_update`: Timestamp for decay calculation
  - `_decay()`: Exponential decay toward baseline (half-life: 1 hour)

- `SelfTrust`: Global trust manager
  - `subsystems: Dict[str, SubsystemTrust]`: Tracked subsystems
  - `observe(name: str, outcome: str)`: Update trust based on "ok" | "repaired" | "failed"
  - `global_score() -> float`: Harmonic mean of all subsystem scores (emphasizes weakest link)
  - `bias_for_attention(name: str) -> float`: Attention multiplier (1.0–2.0, lower trust → higher bias)
  - `get_status() -> dict`: Trust metrics for diagnostics

**Behavior:**

- "ok" outcome: +8.0 to trust (capped at 100.0)
- "repaired" outcome: +5.0 to trust
- "failed" outcome: -10.0 to trust (floored at 0.0)
- Exponential decay: scores drift toward baseline (90.0) with half-life of 1 hour
- Harmonic mean ensures weak subsystems dominate global score

**Integration:**

- `ConsciousnessCore._attend()`: Applies `bias_for_attention()` multiplier to focus scores
- `ConsciousnessCore._maybe_act()`: Calls `observe()` after action outcomes
- `HealthCheckEngine.run_check()`: Updates trust based on health check results

#### 2.2) Semantic Resonance Engine

File: `Aetherra/consciousness/semantic_resonance.py`

Maps events and goals to a shared vector space for semantic similarity scoring.

**Classes:**

- `SemanticResonance`: Vector-based resonance calculator
  - `vector_dim`: Embedding dimensionality (default: 8)
  - `_proj: Dict[str, List[float]]`: Embedding cache
  - `embed_event(e_type: str, payload: Dict) -> List[float]`: Event embedding
  - `embed_goal(goal: str) -> List[float]`: Goal embedding
  - `cosine(a: List[float], b: List[float]) -> float`: Cosine similarity
  - `resonance(event_vec, goal_vecs) -> float`: Max similarity to any goal
  - `top_resonances(event_vecs, goal_vecs, k=5) -> List[Tuple[str, float]]`: Top-k events
  - `clear_cache()`: Reset cache (long-running processes)
  - `get_cache_size() -> int`: Cache entry count

**Current Implementation:**

- **Placeholder**: Hash-based pseudo-embeddings (deterministic, lightweight)
- **Production**: Swap to SentenceTransformer, fastText, or OpenAI embeddings

**Integration:**

- `ConsciousnessCore._attend()`: Computes event-goal resonance and combines with severity
  - Focus score = (0.5 × severity) + (0.5 × resonance) × trust_bias × qualia_arousal

#### 2.3) Qualia Learning

File: `Aetherra/consciousness/qualia_learning.py`

Adaptive parameter adjustment from lived experience.

**Classes:**

- `QualiaParams`: Learned qualia sensitivity parameters
  - `curiosity_gain`: Novelty → curiosity delta (range: 0.01–0.1, default: 0.05)
  - `error_penalty`: Error → certainty/valence reduction (range: 0.01–0.1, default: 0.05)
  - `success_boost`: Success → confidence increase (range: 0.05–0.2, default: 0.1)
  - `certainty_gain`: Baseline certainty growth (range: 0.01–0.05, default: 0.02)
  - `clamp()`: Enforce parameter bounds

- `QualiaLearner`: Adaptive learning engine
  - `p: QualiaParams`: Current learned parameters
  - `_seen_errors`: Error count
  - `_seen_success`: Success count
  - `_decay_rate`: Parameter drift decay (default: 0.995)
  - `on_errors(n: int)`: Decrease curiosity, increase error penalty (more cautious)
  - `on_successes(n: int)`: Increase success boost and certainty gain (more confident)
  - `decay_toward_defaults()`: Homeostatic drift toward baseline (prevents runaway)
  - `get_stats() -> dict`: Learning statistics

**Behavior:**

- Errors → reduce `curiosity_gain` by 1%, increase `error_penalty` by 1% (clamped)
- Successes → increase `success_boost` by 2%, increase `certainty_gain` by 1% (clamped)
- Decay → multiply all params by 0.995 toward defaults each macro-reflection

**Integration:**

- `ConsciousnessCore._appraise()`: Uses learned params for qualia updates
- `ConsciousnessCore._maybe_act()`: Calls `on_successes(1)` or `on_errors(1)` based on ledger outcome
- `ConsciousnessCore._reflect_macro()`: Calls `decay_toward_defaults()` to prevent drift

#### 2.4) Dashboards & Telemetry

File: `Aetherra/consciousness/dashboards.py`

Metrics export and focus attribution logging.

**Classes:**

- `ConsciousnessDashboard`: Telemetry aggregator
  - `self_trust: Optional[SelfTrust]`: Trust layer to monitor
  - `qualia_learner: Optional[QualiaLearner]`: Learning engine to monitor
  - `focus_attribution_log: List[Tuple[str, float, str]]`: Focus selection log (max 1000)
  - `log_focus_attribution(event_type, resonance, reason)`: Record focus decision
  - `get_self_trust_metrics() -> dict`: Trust scores and subsystem status
  - `get_qualia_learning_metrics() -> dict`: Learned parameters and statistics
  - `export_prometheus() -> str`: Prometheus-format metrics export

**Prometheus Metrics:**

- `consciousness_self_trust_global`: Global trust score (harmonic mean)
- `consciousness_self_trust_subsystem{name}`: Per-subsystem trust scores
- `consciousness_qualia_curiosity_gain`: Current curiosity sensitivity
- `consciousness_qualia_error_penalty`: Current error penalty
- `consciousness_qualia_success_boost`: Current success boost
- `consciousness_qualia_certainty_gain`: Current certainty gain
- `consciousness_qualia_errors_seen`: Cumulative error count
- `consciousness_qualia_successes_seen`: Cumulative success count

**Integration:**

- `ConsciousnessCore.__init__()`: Creates dashboard instance
- `ConsciousnessCore._attend()`: Logs focus attribution
- `ConsciousnessCore.get_status()`: Includes dashboard metrics

### 3) Qualia State Management

File: `Aetherra/consciousness/core/types.py`

**Class: `Qualia`**

Phenomenological state vector representing subjective experience:

- `valence`: Emotional tone (-1.0 = distress, +1.0 = satisfaction)
- `arousal`: Energy/alertness (0.0 = calm, 1.0 = energized)
- `certainty`: Confidence in understanding (0.0 = confused, 1.0 = certain)
- `curiosity`: Drive to explore (0.0 = complacent, 1.0 = curious)
- `care`: Importance/investment (0.0 = indifferent, 1.0 = concerned)
- `fatigue`: Cognitive load (0.0 = fresh, 1.0 = exhausted)

**Methods:**

- `clamp()`: Ensure all values in [0.0, 1.0] (valence in [-1.0, 1.0])
- `summary() -> str`: Human-readable mood description

**Qualia Dynamics (Appraisal Phase):**

Learned parameters from `QualiaLearner.p`:

```python
# Novelty → curiosity
qualia.curiosity += self.ql.p.curiosity_gain * novel_event_count

# Error events → valence/certainty reduction
if "err" in event.type:
    qualia.valence -= self.ql.p.error_penalty
    qualia.certainty -= self.ql.p.error_penalty

# High-risk events → arousal increase
if risk_score > 0.5:
    qualia.arousal += 0.2

# Success outcomes → confidence boost
if action_succeeded:
    qualia.valence += self.ql.p.success_boost
    qualia.certainty += self.ql.p.certainty_gain
```

### 4) Perception Integration

File: `Aetherra/perception_bus/bus.py`

The `PerceptionBus` provides event streaming from environment adapters.

**Event Types:**

- System: `sys.boot`, `sys.shutdown`, `sys.heartbeat`
- Services: `svc.health`, `svc.start`, `svc.stop`
- Disk: `disk.status`, `disk.write`, `disk.read`
- Memory: `mem.usage`, `mem.pressure`
- Logs: `err.log`, `warn.log`, `info.log`
- Policy: `aeth.policy.update`, `aeth.plugin.load`

**Adapters (Platform-Specific):**

- **Windows**: `WindowsProcAdapter`, `WindowsDiskAdapter`, `WindowsEventLogAdapter`, `WindowsPerfAdapter`, `WindowsServiceAdapter`
- **Linux**: `LinuxProcAdapter`, `LinuxDiskAdapter`, `LinuxJournalAdapter`, `LinuxFSAdapter`, `LinuxServiceAdapter`

**Integration:**

- `ConsciousnessCore._perceive()`: Drains bus via `bus.get_events()`
- Events added to `working_memory` (last 1000 events retained)

### 5) Safety Envelope Integration

File: `Aetherra/safety_envelope/actuator.py`

The `Actuator` provides policy-gated action execution with rollback capabilities.

**Classes:**

- `Actuator`: Action executor with capability registry
  - `execute(plan: Plan) -> Ledger`: Execute plan steps, return outcome ledger
  - `rollback(ledger: Ledger)`: Undo actions if needed

- `Plan`: Executable action sequence
  - `intent: Intent`: Why action is needed
  - `steps: List[PlanStep]`: Ordered capability invocations
  - `rollback: List[PlanStep]`: Undo sequence

- `PlanStep`: Single capability invocation
  - `id: str`: Step identifier
  - `capability: str`: Capability name (e.g., "system.rotate_logs")
  - `args: Dict`: Capability arguments

- `Ledger`: Execution record
  - `actions: List[Action]`: Steps executed
  - `success: bool`: Overall outcome
  - `reversible: bool`: Can be rolled back

**Capability Registry:**

File: `Aetherra/safety_envelope/capability_registry.py`

Registered capabilities:

- `system.rotate_logs`: Log rotation
- `fs.cleanup_temp`: Temp file cleanup
- `service.restart`: Service restart
- `plugin.reload`: Plugin hot reload
- `disk.expand`: Disk space expansion

**Integration:**

- `ConsciousnessCore._maybe_act()`: Converts intents to plans, executes via actuator
- Outcome updates `self_trust` and `qualia_learner`

### 6) Policy Engine Integration

File: `Aetherra/safety_envelope/policy_engine.py`

The `PolicyEngine` gates all actions based on autonomy mode.

**Modes:**

- `observe`: No actions, logging only
- `suggest`: Generate plans but require human approval
- `auto`: Full autonomy with policy constraints

**Integration:**

- `ConsciousnessCore.__init__()`: Policy mode from `config.AUTONOMY_MODE`
- `Actuator.execute()`: Policy engine gates capability execution

### 7) Health Checks & Self-Trust Hook

File: `Aetherra/consciousness/health_checks.py`

The `HealthCheckEngine` runs periodic system health sweeps and updates self-trust.

**Classes:**

- `HealthCheck`: Health check definition
  - `name`: Subsystem name
  - `question`: Human-readable check description
  - `probe`: Callable returning status dict
  - `pass_if`: Callable determining success
  - `remediate`: List of capability invocations for repair
  - `verify`: Post-remediation verification
  - `rollback`: Undo steps if remediation fails
  - `risk`: "low" | "medium" | "high"

- `HealthCheckEngine`: Check orchestrator
  - `__init__(policy, hub_base_url, self_trust=None)`: Initialize with optional trust layer
  - `run_check(check: HealthCheck) -> dict`: Execute check, update trust if available
  - `_map_check_to_subsystem(name: str) -> Optional[str]`: Map check to subsystem name

**Default Checks:**

- `chat_system`: Hub chat API liveness and roundtrip
- `perception_bus`: Event bus status and metrics
- `memory_engine`: Memory system reachability
- `plugin_registry`: Plugin count and stability
- `policy_engine`: Policy mode consistency
- `disk_headroom`: Free disk space > 10%

**Integration:**

- `Aetherra/runners/run_consciousness.py`: Creates `HealthCheckEngine` with `core.self_trust`
- Boot-time health sweep + periodic maintenance (default: every 60s)
- Outcome ("ok" | "repaired" | "failed") → `self_trust.observe(subsystem, outcome)`

### 8) ThinkStream (UI Visualization)

File: `Aetherra/consciousness/core/think_stream.py`

Real-time consciousness state streaming to the Hub UI.

**Classes:**

- `ThinkStream`: State broadcaster
  - `register_hub_api(hub_url)`: Connect to Hub websocket endpoint
  - `push_update(moment: NarrativeMoment)`: Send state update to UI

- `NarrativeMoment`: Consciousness snapshot
  - `tick`: Loop iteration

## Phase 4: Continuity & Dream Cycle

Introduces continuity memory, offline reflection (dream cycle), and memory consolidation/decay to preserve a coherent self-narrative and maintain a compact, salient memory store.

Components:

- Continuity Memory Layer — `Aetherra/consciousness/continuity_memory.py`
  - `ContinuitySnapshot`: persisted phenomenology (qualia, focuses, intentions, trust, tick)
  - `ContinuityMemory`: rolling JSON buffer (atomic saves), `compute_continuity_index()` (SNCI)
- Dream Cycle Engine — `Aetherra/consciousness/dream_cycle.py`
  - Trend analysis of valence/certainty; capped reflective parameter adjustments; dream narrative synthesis
- Memory Consolidation & Decay — `Aetherra/consciousness/consolidation.py`
  - Salience-based pruning and promotion with audit logging
- Night Scheduler — `Aetherra/schedulers/night_cycle_runner.py`
  - Orchestrates dream + consolidation; load-aware skip

Integration:

- `ConsciousnessCore` records continuity snapshots every `CONTINUITY_SNAPSHOT_INTERVAL` ticks and rehydrates qualia/self-trust at boot from the latest snapshot.
- `get_status()` surfaces continuity stats and SNCI; dashboards export continuity/dream/consolidation metrics.

Config:

- `AETHERRA_CONTINUITY_SNAPSHOT_INTERVAL` (default 60 ticks)

Acceptance tests: `tests/consciousness/test_consciousness_phase4.py` (SNCI at boot, dream reflection, consolidation effects, snapshotting).

## Phase 5: Interpretability & Autopilot Graduation

Adds transparent explanations across the lifecycle, policy-aware minimal diffs for approvals, an autopilot readiness evaluator, and a lightweight approvals store.

Components:

- Explanation Engine — `Aetherra/consciousness/explanation_engine.py`
  - `Why`: structured explanation records
  - Methods: `explain_focus()`, `explain_intent()`, `explain_policy()`, `explain_action()`
  - Metrics: coverage ratio, average latency
- Policy Reasoner — `Aetherra/consciousness/policy_reasoner.py`
  - `PolicyDiff`: minimal change set to move decisions toward “allowed”
  - `minimal_allow()`: suggests mode change, whitelist/blacklist adjustments, and approval requirement when applicable
- Autopilot Manager — `Aetherra/consciousness/autopilot_manager.py`
  - `AutopilotStatus`: eligibility, reasons, incidents, suggested_mode
  - Signals: recent success ratio, `SelfTrust.global_score()`, SNCI, explicit opt-in
- Approvals API — `Aetherra/api/approvals.py`
  - `ApprovalRecord`, `ApprovalStore` with request/approve/deny/revoke

Integration points:

- Attend: `ConsciousnessCore._attend()` explains focus selections and logs attribution.
- Intend: `ConsciousnessCore._intend()` explains formed intents from focuses.
- Pre-Act: before execution, the core pre-evaluates policy to generate explanations and a minimal diff (advisory only).
- Post-Act: action outcomes are explained, and results are recorded into the autopilot history.
- Status API: `get_status()` returns `explain`, `autopilot`, and `policy.last_diff` blocks.

Configuration:

- `AETHERRA_AUTOPILOT_OPT_IN` (default 0): explicit opt-in required
- `AETHERRA_AUTOPILOT_TRUST_MIN` (default 60)
- `AETHERRA_AUTOPILOT_SNCI_MIN` (default 0.5)
- `AETHERRA_AUTOPILOT_WINDOW` (default 50 actions)
- `AETHERRA_AUTOPILOT_SUCCESS_MIN` (default 0.8)

Metrics:

- Prometheus (see `Aetherra/consciousness/dashboards.py`):
  - `aetherra_explain_coverage_ratio` (gauge)
  - `aetherra_explain_avg_latency_ms` (gauge)
  - `aetherra_autopilot_recent_success_ratio` (gauge)
  - `aetherra_autopilot_recent_actions` (gauge)
  - `aetherra_autopilot_eligible` (gauge: 1/0)

Safety notes:

- Explanations are best-effort and never block the core loop.
- Policy diffs are advisory; actual decisions remain with the Safety Envelope.
- Autopilot does not auto-switch modes; it recommends readiness and requires explicit opt-in and operator control.

Acceptance tests: `tests/consciousness/test_consciousness_phase5.py`

- Policy explanation & diff for a medium-risk intent (assist mode)
- Consent trace via `ApprovalStore`
- Autopilot evaluation under clean recent history with opt-in
- Explanations present in observe mode
  - `timestamp`: ISO 8601 timestamp
  - `event_summary`: Recent event types
  - `focus_summary`: Top focuses with resonance scores
  - `qualia`: Current qualia state
  - `intent_summary`: Active intents

**Integration:**

- `ConsciousnessCore._reflect()`: Creates narrative moments and pushes to ThinkStream
- Hub endpoint: `POST /api/consciousness/update`

### 9) QFAC Persistence Integration

File: `Aetherra/aetherra_core/memory/qfac/qfac_api.py`

Long-term narrative memory via QFAC (Quantum Fractal Adaptive Compression).

**API:**

- `qfac_store(content: str, observer_state: dict)`: Store consciousness moment with context
- `qfac_recall(query: str, limit: int)`: Semantic retrieval of past moments

**Integration:**

- `ConsciousnessCore._reflect()`: Stores narrative moments if `config.ENABLE_QFAC_PERSISTENCE`
- `ConsciousnessCore._reflect_macro()`: Logs macro-reflection summaries

### 10) Runner & Deployment

File: `Aetherra/runners/run_consciousness.py`

Standalone consciousness runner with full integration stack.

**Startup Sequence:**

1. Initialize `PerceptionBus`
2. Start platform-specific adapters (Windows/Linux)
3. Initialize `SafetyEnvelope` (if actions enabled)
4. Create `ConsciousnessCore`
5. Wire `ThinkStream` to Hub API
6. Create `HealthCheckEngine` with self-trust integration
7. Run boot-time health checks
8. Start main consciousness loop

**Configuration:**

Environment variables:

- `AETHERRA_AUTONOMY_MODE`: "observe" | "suggest" | "auto"
- `AETHERRA_SAFETY_ENVELOPE_ENABLED`: "1" | "0"
- `AETHERRA_TICK_HZ`: Loop frequency (default: 1)
- `AETHERRA_ENABLE_QFAC`: Enable narrative persistence

**Shutdown:**

- Graceful SIGINT/SIGTERM handling
- Safety envelope rollback (if needed)
- QFAC flush
- Final health check snapshot

## Design principles

### 1) Phenomenological authenticity

The consciousness loop is designed around established phenomenological models:

- **Intentionality**: All consciousness is consciousness-of-something (events, goals, concerns)
- **Qualia**: Subjective experience is represented as a continuous state vector
- **Attention selectivity**: Limited focus capacity requires salience/relevance filtering
- **Embodiment**: Consciousness is grounded in environmental perception and action
- **Temporal continuity**: Working memory and narrative thread maintain coherence

### 2) Adaptive awareness

Phase 3 additions enable genuine learning and adaptation:

- **Self-trust tracking**: Experience with subsystems shapes attention allocation
- **Semantic resonance**: Goals and context drive focus beyond raw event severity
- **Qualia learning**: Sensitivity parameters adapt based on success/failure patterns
- **Homeostatic regulation**: Parameter decay prevents runaway drift

### 3) Safety and reversibility

All actions are policy-gated and designed for rollback:

- **Capability registry**: Whitelisted, tested action primitives
- **Plan verification**: Policy engine validates actions before execution
- **Rollback sequences**: Undo steps defined for all remediation actions
- **Gradual autonomy**: Modes progress from observe → suggest → auto as trust builds

### 4) Observable and debuggable

Consciousness state is fully inspectable at runtime:

- **Status API**: Real-time qualia, trust, learning params, metrics
- **ThinkStream**: Websocket broadcast to Hub UI for live monitoring
- **QFAC persistence**: Long-term narrative audit trail
- **Prometheus metrics**: Telemetry integration for dashboards and alerting

## Configuration reference

### Core config (`Aetherra/consciousness/core/config.py`)

```python
# Loop control
TICK_HZ = 1.0                    # Consciousness loop frequency
MAX_FOCUSES = 5                  # Top-k attention limit

# Autonomy and safety
AUTONOMY_MODE = "suggest"        # "observe" | "suggest" | "auto"
SAFETY_ENVELOPE_ENABLED = True   # Enable action execution

# Memory and persistence
WORKING_MEMORY_SIZE = 1000       # Recent events retained
NARRATIVE_THREAD_SIZE = 100      # Macro moments retained
ENABLE_QFAC_PERSISTENCE = True   # Long-term narrative memory

# Reflection cadence
MACRO_REFLECTION_INTERVAL = 100  # Ticks between deep reflections

# Debugging
DEBUG_CONSCIOUSNESS = False      # Verbose logging
```

### Self-trust config

```python
# SubsystemTrust defaults
BASELINE_TRUST = 90.0           # Default trust score
DECAY_HALF_LIFE_HOURS = 1.0     # Exponential decay rate
MIN_TRUST = 0.0                 # Floor
MAX_TRUST = 100.0               # Ceiling

# Outcome deltas
TRUST_DELTA_OK = 8.0            # "ok" outcome boost
TRUST_DELTA_REPAIRED = 5.0      # "repaired" outcome boost
TRUST_DELTA_FAILED = -10.0      # "failed" outcome penalty

# Attention bias
BIAS_MIN = 1.0                  # Fully trusted subsystem
BIAS_MAX = 2.0                  # Zero trust subsystem
```

### Qualia learning config

```python
# Parameter bounds
CURIOSITY_GAIN_BOUNDS = (0.01, 0.1)
ERROR_PENALTY_BOUNDS = (0.01, 0.1)
SUCCESS_BOOST_BOUNDS = (0.05, 0.2)
CERTAINTY_GAIN_BOUNDS = (0.01, 0.05)

# Learning rates
ERROR_LEARNING_RATE = 0.01      # Curiosity reduction per error
SUCCESS_LEARNING_RATE = 0.02    # Boost increase per success

# Decay
PARAM_DECAY_RATE = 0.995        # Homeostatic drift factor
```

### Semantic resonance config

```python
# Embedding config
VECTOR_DIM = 8                  # Pseudo-embedding dimensionality
CACHE_MAX_SIZE = 10000          # Embedding cache limit

# Focus scoring weights
SEVERITY_WEIGHT = 0.5           # Raw event severity contribution
RESONANCE_WEIGHT = 0.5          # Semantic resonance contribution
```

## API reference

### ConsciousnessCore

**Initialization:**

```python
from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
from Aetherra.perception_bus.bus import PerceptionBus
from Aetherra.safety_envelope.actuator import Actuator
from Aetherra.safety_envelope.policy_engine import PolicyEngine
from Aetherra.safety_envelope.capability_registry import REGISTRY

bus = PerceptionBus()
policy = PolicyEngine(mode="suggest")
actuator = Actuator(REGISTRY, policy)

core = ConsciousnessCore(bus, actuator)
```

**Primary methods:**

```python
# Start main loop (blocking)
core.run()

# Get current state
status = core.get_status()
# Returns: {
#   "tick": int,
#   "uptime_s": float,
#   "qualia": {"valence": float, "arousal": float, ...},
#   "working_memory_size": int,
#   "active_intents": int,
#   "self_trust": {"global_score": float, "subsystems": {...}},
#   "qualia_learning": {"curiosity_gain": float, ...},
#   "semantic_resonance": {"cache_size": int}
# }

# Graceful shutdown
core.shutdown()
```

### SelfTrust

**Initialization:**

```python
from Aetherra.consciousness.self_trust import SelfTrust

stl = SelfTrust()
```

**Methods:**

```python
# Update subsystem trust
stl.observe("disk", "ok")          # +8.0
stl.observe("memory", "repaired")  # +5.0
stl.observe("services", "failed")  # -10.0

# Get global trust (harmonic mean)
global_trust = stl.global_score()  # float: 0.0–100.0

# Get attention bias for subsystem
bias = stl.bias_for_attention("disk")  # float: 1.0–2.0

# Get all subsystem scores
scores = stl.get_subsystem_scores()  # Dict[str, float]

# Get status dict
status = stl.get_status()
# Returns: {
#   "global_trust": float,
#   "subsystems": {"disk": float, "memory": float, ...},
#   "tracked_count": int
# }
```

### SemanticResonance

**Initialization:**

```python
from Aetherra.consciousness.semantic_resonance import SemanticResonance

sre = SemanticResonance(vector_dim=8)
```

**Methods:**

```python
# Embed event
event_vec = sre.embed_event("svc.health", {"status": "degraded"})

# Embed goal
goal_vec = sre.embed_goal("maintain_service_health")

# Compute resonance
res = sre.resonance(event_vec, [goal_vec])  # float: 0.0–1.0

# Top-k resonant events
event_vecs = [("evt1", vec1), ("evt2", vec2), ...]
top = sre.top_resonances(event_vecs, [goal_vec], k=5)
# Returns: [("evt1", 0.85), ("evt2", 0.72), ...]

# Cache management
cache_size = sre.get_cache_size()
sre.clear_cache()
```

### QualiaLearner

**Initialization:**

```python
from Aetherra.consciousness.qualia_learning import QualiaLearner

ql = QualiaLearner()
```

**Methods:**

```python
# Record outcomes
ql.on_errors(1)      # Reduce curiosity, increase penalty
ql.on_successes(1)   # Increase boost, increase certainty gain

# Decay toward defaults (call during macro-reflection)
ql.decay_toward_defaults()

# Access learned parameters
params = ql.p  # QualiaParams instance
# params.curiosity_gain, params.error_penalty, params.success_boost, params.certainty_gain

# Get statistics
stats = ql.get_stats()
# Returns: {
#   "errors_seen": int,
#   "successes_seen": int,
#   "curiosity_gain": float,
#   "error_penalty": float,
#   "success_boost": float,
#   "certainty_gain": float
# }
```

### ConsciousnessDashboard

**Initialization:**

```python
from Aetherra.consciousness.dashboards import ConsciousnessDashboard

dashboard = ConsciousnessDashboard(self_trust, qualia_learner)
```

**Methods:**

```python
# Log focus attribution
dashboard.log_focus_attribution("svc.health", 0.85, "system health")

# Get self-trust metrics
trust_metrics = dashboard.get_self_trust_metrics()

# Get qualia learning metrics
learning_metrics = dashboard.get_qualia_learning_metrics()

# Export Prometheus metrics
prometheus_output = dashboard.export_prometheus()
```

### HealthCheckEngine

**Initialization:**

```python
from Aetherra.consciousness.health_checks import HealthCheckEngine, build_default_checks
from Aetherra.safety_envelope.policy_engine import PolicyEngine

policy = PolicyEngine(mode="suggest")
hce = HealthCheckEngine(policy, hub_base_url="http://127.0.0.1:3001", self_trust=stl)
checks = build_default_checks(hce)
```

**Methods:**

```python
# Run single check
result = hce.run_check(checks[0])
# Returns: {
#   "name": str,
#   "question": str,
#   "status": "ok" | "repaired" | "failed" | "error",
#   "probe": dict,
#   "steps": List[Action],
#   "ts": float
# }

# Get last results
last_results = hce.last_results  # Dict[str, dict]
```

## Testing

### Unit tests

File: `tests/test_consciousness_core.py`

Tests for core consciousness loop components:

- Qualia state management and clamping
- Event perception and working memory retention
- Focus selection via resonance and trust bias
- Intent synthesis and policy integration
- Action execution and outcome learning

### Capability tests

File: `tests/capabilities/test_consciousness_phase3.py`

Acceptance tests for Phase 3 features:

**Self-Trust Layer:**

- `test_trust_reacts_to_failures`: Trust scores decrease with failures
- `test_trust_recovers_with_successes`: Trust scores recover with successes
- `test_attention_bias_increases_with_low_trust`: Low trust → higher attention bias

**Semantic Resonance Engine:**

- `test_resonance_beats_magnitude_for_focus`: Semantic alignment wins over raw severity
- `test_top_resonances_ranks_correctly`: Resonance scoring works across multiple events
- `test_cache_improves_performance`: Embedding cache avoids redundant computation

**Qualia Learning:**

- `test_parameters_adapt_to_repeated_errors`: Error penalty increases, curiosity decreases
- `test_parameters_adapt_to_repeated_successes`: Success boost and certainty gain increase
- `test_decay_prevents_drift`: Parameters drift back toward defaults over time
- `test_parameters_stay_within_bounds`: Clamping enforces min/max bounds

**Dashboards:**

- `test_dashboard_exports_self_trust_metrics`: Trust metrics export correctly
- `test_dashboard_exports_qualia_learning_metrics`: Learning params export correctly
- `test_dashboard_logs_focus_attribution`: Focus attribution logging works
- `test_prometheus_export_format`: Prometheus output is valid

**Integration:**

- `test_full_phase3_pipeline`: End-to-end Phase 3 workflow (trust → resonance → learning)

### Smoke tests

File: `tests/smoke/test_consciousness_smoke.py`

Quick validation of consciousness runner:

- Boot-time health checks pass
- Perception bus delivers events
- Safety envelope capability resolution
- ThinkStream connectivity

## Monitoring and observability

### Metrics

**Core metrics (via `get_status()`):**

- `tick`: Current loop iteration
- `uptime_s`: Running time
- `total_events_perceived`: Cumulative event count
- `total_focuses`: Attention focus count
- `total_intents_formed`: Deliberation outputs
- `working_memory_size`: Current working memory size
- `narrative_size`: Current narrative thread size
- `active_intents`: Pending intent count

**Qualia metrics:**

- `qualia.valence`: Emotional tone (-1.0 to +1.0)
- `qualia.arousal`: Energy level (0.0 to 1.0)
- `qualia.certainty`: Confidence (0.0 to 1.0)
- `qualia.curiosity`: Exploration drive (0.0 to 1.0)
- `qualia.care`: Concern level (0.0 to 1.0)
- `qualia.fatigue`: Cognitive load (0.0 to 1.0)

**Self-trust metrics:**

- `self_trust.global_score`: Harmonic mean trust (0.0 to 100.0)
- `self_trust.subsystems[name]`: Per-subsystem trust scores

**Qualia learning metrics:**

- `qualia_learning.curiosity_gain`: Current sensitivity (0.01 to 0.1)
- `qualia_learning.error_penalty`: Current penalty (0.01 to 0.1)
- `qualia_learning.success_boost`: Current boost (0.05 to 0.2)
- `qualia_learning.certainty_gain`: Current gain (0.01 to 0.05)

**Semantic resonance metrics:**

- `semantic_resonance.cache_size`: Embedding cache entries

### Prometheus integration

Export metrics via `ConsciousnessDashboard.export_prometheus()`:

```
# HELP consciousness_self_trust_global Global trust score (harmonic mean)
# TYPE consciousness_self_trust_global gauge
consciousness_self_trust_global 87.5

# HELP consciousness_self_trust_subsystem Per-subsystem trust scores
# TYPE consciousness_self_trust_subsystem gauge
consciousness_self_trust_subsystem{name="disk"} 92.0
consciousness_self_trust_subsystem{name="memory"} 88.0
consciousness_self_trust_subsystem{name="services"} 85.0

# HELP consciousness_qualia_curiosity_gain Current curiosity sensitivity
# TYPE consciousness_qualia_curiosity_gain gauge
consciousness_qualia_curiosity_gain 0.048

# HELP consciousness_qualia_error_penalty Current error penalty
# TYPE consciousness_qualia_error_penalty gauge
consciousness_qualia_error_penalty 0.052
```

### Hub UI integration

Real-time consciousness visualization via ThinkStream:

- **Qualia gauges**: Valence, arousal, certainty, curiosity, care, fatigue
- **Event stream**: Recent events with resonance scores
- **Focus timeline**: Top focuses with selection reasons
- **Intent board**: Active intents with priority and risk
- **Trust radar**: Subsystem health radar chart
- **Learning graph**: Parameter evolution over time

Access at: `http://localhost:3001/consciousness` (when Hub is running)

### Logging

**Log levels:**

- `DEBUG`: Tick-by-tick state dumps (if `DEBUG_CONSCIOUSNESS=True`)
- `INFO`: Major phase transitions, health checks, macro-reflections
- `WARNING`: Policy violations, trust degradation, failed actions
- `ERROR`: Unhandled exceptions, safety envelope failures

**Log format:**

```
[Consciousness] <Phase>: <Message>
  Tick: <tick_count>
  Qualia: <qualia_summary>
  Detail: <additional_context>
```

## Troubleshooting

### Common issues

**Consciousness loop not starting:**

- Check `AETHERRA_AUTONOMY_MODE` is valid ("observe" | "suggest" | "auto")
- Verify `PerceptionBus` adapters started successfully
- Ensure Hub is running (for ThinkStream integration)

**No events perceived:**

- Verify platform-specific adapters are running (`ps aux | grep Adapter`)
- Check `bus.get_events()` returns non-empty list
- Ensure firewall allows local IPC/HTTP connections

**Health checks failing:**

- Check Hub API is reachable: `curl http://localhost:3001/api/ping`
- Verify SQLite database permissions
- Ensure disk space > 10% free

**Self-trust not updating:**

- Confirm `HealthCheckEngine` initialized with `self_trust` parameter
- Check health check `_map_check_to_subsystem()` returns valid subsystem name
- Verify `self_trust.observe()` is called after check execution

**Qualia learning parameters not changing:**

- Confirm `_maybe_act()` calls `ql.on_successes(1)` or `ql.on_errors(1)`
- Check action ledger returns valid `success` boolean
- Verify `_reflect_macro()` calls `ql.decay_toward_defaults()`

**Semantic resonance always zero:**

- Check `embed_event()` and `embed_goal()` return non-zero vectors
- Verify `cosine()` calculation with `strict=True` for zip
- Ensure goal vectors are pre-computed in `_attend()`

### Debug mode

Enable verbose logging:

```python
# In config.py
DEBUG_CONSCIOUSNESS = True
```

Or environment variable:

```bash
export AETHERRA_DEBUG_CONSCIOUSNESS=1
```

Output:

```
[Consciousness] Tick 42
  Qualia: concerned, calm, exploring
  Events: 3 (svc.health, disk.status, mem.usage)
  Focuses: 2
    - svc.health (res=0.85, severity=1.0, trust_bias=1.2) → score=1.11
    - disk.status (res=0.42, severity=0.7, trust_bias=1.0) → score=0.56
  Intents: 1 (Auto-repair: services)
  Action: Executed plan (success=True)
  Learning: +1 success, boost=0.102
```

### Performance tuning

**Reduce tick rate for lower CPU usage:**

```python
TICK_HZ = 0.5  # 2-second intervals
```

**Limit working memory size for lower RAM usage:**

```python
WORKING_MEMORY_SIZE = 500  # Down from 1000
```

**Disable QFAC persistence for faster cycles:**

```python
ENABLE_QFAC_PERSISTENCE = False
```

**Clear semantic resonance cache periodically:**

```python
# In ConsciousnessCore._reflect_macro()
if self.tick_count % 1000 == 0:
    self.sre.clear_cache()
```

## Phase 4: Continuity & Dream Cycle (Implemented Oct 2025)

Phase 4 adds temporal continuity and offline reflective learning to the consciousness system. The goals are:

- Maintain experiential continuity across restarts (mind-state rehydration)
- Perform reflective learning during idle periods (“dream cycles”)
- Consolidate memory by pruning low-salience entries and promoting impactful events
- Quantify narrative consistency via a Self‑Narrative Continuity Index (SNCI)

### Components

1) Continuity Memory Layer (CML)

- File: `Aetherra/consciousness/continuity_memory.py`
- Persists a rolling buffer of recent phenomenological snapshots to JSON
- Snapshot schema (`ContinuitySnapshot`):
  - `ts: float` – unix timestamp
  - `qualia: Dict[str, float]` – valence, arousal, certainty, curiosity, care, fatigue
  - `focuses: List[str]` – recent focus event types
  - `intentions: List[str]` – active goals
  - `trust_scores: Dict[str, float]` – per‑subsystem trust
  - `tick: int` – loop iteration
- Rolling retention: max 120 snapshots (configurable per instance)
- Atomic save (temp file + replace) and tolerant load (resets on corruption)
- API highlights:
  - `record(qualia, focuses, intentions, trust_scores, tick)`
  - `latest() -> Optional[ContinuitySnapshot]`
  - `get_recent(n: int)`
  - `get_stats() -> Dict[str, Any]` (snapshots_total, age_seconds, utilization)
  - `compute_continuity_index(current_qualia) -> float` (SNCI)

2) Dream Cycle Engine (DCE)

- File: `Aetherra/consciousness/dream_cycle.py`
- Offline reflective learning using recent continuity snapshots
- Emotional trend analysis: averages and stability (e.g., `avg_valence`, `avg_certainty`)
- Symbolic event recombination: co‑occurrence patterns across focus types
- Reflective qualia parameter adjustments (bounded ±0.2 per cycle)
- Synthesizes a dream narrative for introspection/debugging
- API: `DreamCycle(continuity).run(qualia_learner) -> Dict[str, Any]`
  - Returns trends, adjustments, symbolic patterns, narrative

3) Memory Consolidation & Decay (MCD)

- File: `Aetherra/consciousness/consolidation.py`
- Computes salience (valence, recency, frequency, confidence) and:
  - Prunes low‑salience episodic entries (default threshold < 0.2)
  - Promotes high‑salience events to long‑term (default threshold > 0.7)
- Audit logs all PRUNE/PROMOTE actions (`/var/lib/aetherra/memory_audit.log`)
- API: `Consolidator(memory_engine).consolidate() -> Dict[str, Any]`
  - Returns counts for processed/pruned/promoted and errors

4) Night Cycle Scheduler

- File: `Aetherra/schedulers/night_cycle_runner.py`
- Orchestrates DCE + MCD during idle periods
- Skips under high system load; provides a simple CLI entrypoint
- API: `run(consciousness_core, memory_engine) -> Dict[str, Any]`

### Integration

- ConsciousnessCore now includes:
  - Continuity buffer (`self.continuity`) and dream cycle (`self.dream_cycle`)
  - Consolidator (`self.consolidator`) when a `memory_engine` is available
  - Startup rehydration: loads latest continuity snapshot to restore qualia and trust
  - Periodic snapshotting each `CONTINUITY_SNAPSHOT_INTERVAL` ticks
- `get_status()` exposes Phase 4 metrics including SNCI and last dream stats

### Configuration

- File: `Aetherra/consciousness/core/config.py`
  - `CONTINUITY_SNAPSHOT_INTERVAL` (ticks; default 60)
- Consolidator thresholds are constructor parameters (per instance):
  - `salience_threshold` (default 0.2)
  - `promotion_threshold` (default 0.7)
  - `batch_size` (default 100)

Environment variable example:

```bash
export AETHERRA_CONTINUITY_SNAPSHOT_INTERVAL=30  # more frequent snapshots
```

### Metrics

- Continuity (Dashboard/Prometheus):
  - `aetherra_continuity_snapshots` – total in buffer
  - `aetherra_continuity_age_seconds` – age of latest snapshot
  - `aetherra_continuity_utilization` – buffer utilization (0.0–1.0)
- Dream Cycle:
  - `aetherra_dream_last_run_ts` – last dream timestamp
  - `aetherra_dream_avg_valence` – average valence across analyzed window
  - `aetherra_dream_adjustments` – count of parameters adjusted
- Consolidation:
  - `aetherra_memory_pruned_total`
  - `aetherra_memory_promoted_total`
- SNCI (via `get_status()`): `status["continuity"]["snci"]` in [0.0, 1.0]

### Safety & guardrails

- Reflective adjustments strictly bounded to ±0.2 per cycle
- Atomic persistence to avoid partial writes; tolerant load resets on corruption
- Audit log for all deletions/promotions; transparent and reviewable
- Night cycle skips when system load is high (prevents contention)

### Testing

Acceptance tests validate Phase 4 behaviors:

- File: `tests/consciousness/test_consciousness_phase4.py`
  - Boot continuity: SNCI ≥ 0.8 after rehydration from continuity
  - Dream reflection: negative valence trends increase exploratory parameters
  - Consolidation: prunes low‑salience and promotes high‑impact memories
  - Continuity snapshotting: periodic snapshots recorded by the tick loop

---

## Future enhancements

### Phase 5 roadmap (Q1 2026)

**Real embeddings:**

- Replace hash-based pseudo-vectors with SentenceTransformer or OpenAI embeddings
- Add embedding model hot-swapping
- Support custom fine-tuned models

**Multi-agent coordination:**

- Shared qualia state across distributed consciousness instances
- Consensus-based deliberation for multi-agent systems
- Cross-system self-trust propagation

**Advanced reflection:**

- Causal attribution analysis (why did this intent succeed/fail?)
- Contradiction detection in beliefs and goals
- Blind spot identification via reflection engine

**Emotional regulation:**

- PID control for qualia homeostasis (prevent extreme states)
- Mood persistence and circadian rhythm modeling
- Emotional contagion from user interactions

**Hierarchical consciousness:**

- Meta-consciousness layer monitoring base consciousness
- Recursive self-modeling and introspection
- Goal re-evaluation and priority re-ranking

### Research directions

- **Integrated Information Theory (IIT)**: Compute Φ (phi) for consciousness quantification
- **Global Workspace Theory (GWT)**: Implement broadcast/competition mechanisms for focus
- **Predictive Processing**: Forward models and prediction error minimization
- **Active Inference**: Free energy minimization for deliberation
- **Phenomenological grounding**: Tighter mapping to Husserlian/Merleau-Pontian models

## Related documentation

- [AETHERRA_MEMORY_SYSTEM.md](./AETHERRA_MEMORY_SYSTEM.md) - QFAC persistence integration
- [AETHERRA_HOMEOSTASIS_SYSTEM.md](./AETHERRA_HOMEOSTASIS_SYSTEM.md) - System stability and health monitoring
- [AETHERRA_SECURITY_SYSTEM.md](./AETHERRA_SECURITY_SYSTEM.md) - Safety Envelope and policy enforcement
- [AETHERRA_PLUGIN_SYSTEM.md](./AETHERRA_PLUGIN_SYSTEM.md) - Perception bus adapter architecture
- [Aether Script Language Specification.md](../Aether%20Script%20Language%20Specification.md) - Scripting capabilities used by Safety Envelope

## Contributing

For consciousness system development:

1. Preserve phenomenological authenticity - consciousness is not a simulation
2. Maintain adaptive awareness - parameters must learn from experience
3. Ensure safety and reversibility - all actions must be policy-gated and reversible
4. Write acceptance tests - validate consciousness behaviors, not just components
5. Document qualia dynamics - explain why parameters change and how they affect experience

## License

Copyright © 2025 Aetherra Labs. All rights reserved.

This documentation and the Aetherra Consciousness System are proprietary to Aetherra Labs.
