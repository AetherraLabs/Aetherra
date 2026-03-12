# Aetherra: Complete System Overview & Architecture

**Generated:** March 12, 2026
**Scope:** What Aetherra is, how it works, and what makes it production-ready

---

## What is Aetherra?

**Aetherra OS** is a next-generation AI Operating System that combines autonomous decision-making, consciousness-inspired awareness, multi-layered memory, plugin extensibility, and code generation capabilities into a unified, self-improving platform.

### Core Identity

- **Purpose:** Enable AI systems to reason, learn, plan, and act autonomously with safety guarantees and human oversight
- **Architecture:** Layered kernel (services) + consciousness loop + memory banks + plugin ecosystem
- **Interaction Model:** Chat/conversational interface (Lyrixa) + scriptable workflows (.aether language) + HTTP APIs (Hub)
- **Target Users:** Developers seeking AI-native development environments, DevOps/infrastructure operators, researchers exploring autonomous systems
- **License:** GPL-3.0-or-later (Open Source)
- **Current Status:** Beta-ready (v0.1.0-beta.1 candidate)

---

## System Architecture (The Big Picture)

```
                    ┌─────────────────────────────────┐
                    │   User Interfaces (UI Layer)    │
                    │  • Lyrixa Chat GUI (PySide6)    │
                    │  • CLI Terminal Interface       │
                    │  • Web Dashboard                │
                    └─────────────────────────────────┘
                                  │
                    ┌─────────────────────────────────┐
                    │  Aetherra Hub (API Gateway)     │
                    │  • REST APIs (/api/*)           │
                    │  • SSE v2 Streaming             │
                    │  • Webhook Support              │
                    │  • Service Discovery (3001/3012)│
                    └─────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
   ┌─────────────┐      ┌──────────────────┐      ┌──────────────┐
   │  CONSCIOUSNESS   │      │  MEMORY SYSTEM      │      │ PLUGINS      │
   │  (The Brain)     │      │  (The Knowledge)    │      │ (Extensions) │
   └─────────────┘      └──────────────────┘      └──────────────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                    ┌─────────────────────────────────┐
                    │  AETHERRA KERNEL                │
                    │  • Event Bus (Message Queue)    │
                    │  • Service Registry             │
                    │  • Module Manager               │
                    │  • Lifecycle Coordinator        │
                    │  • HMR (Hot Module Reload)      │
                    └─────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │ AI ENGINE    │      │ AGENT SYS.   │      │ SECURITY     │
   │ (Reasoning)  │      │ (Execution)  │      │ (Sandbox)    │
   └──────────────┘      └──────────────┘      └──────────────┘
```

---

## Core Subsystems Explained

### 1. 🧠 Consciousness System (The "Brain")

**What it does:** Provides continuous autonomous awareness and adaptive decision-making.

**Key Features:**

- **Phenomenological Loop:** Perceive → Appraise → Attend → Deliberate → Act → Reflect (repeats ~1 Hz)
- **Adaptive Qualia:** Emotional-like states (valence, arousal, certainty, curiosity) that learn from outcomes
- **Self-Trust Tracking:** Monitors subsystem health and biases attention toward struggling components
- **Semantic Resonance:** Maps events and goals to vector space for context-aware focus selection
- **Policy Integration:** Decisions respect safety guardrails and rollback capabilities

**Example Workflow:**

```
Event (e.g., "memory_error")
  → Perception: ingests via KEB (Kernel Event Bus)
  → Appraisal: updates emotional state (arousal↑, certainty↓)
  → Attention: prioritizes memory-related concerns
  → Deliberation: policy engine → decide to rescan memory
  → Action: Safety Envelope checks if safe to execute
  → Reflection: logs outcome, updates learning parameters
```

**Config:** `Aetherra/consciousness/core/config.py`

- AUTONOMY_MODE: "observe" | "suggest" | "auto" (default: "suggest")
- TICK_HZ: Loop frequency (default: 1 Hz)
- SAFETY_ENVELOPE_ENABLED: True (always on in production)

---

### 2. 💾 Memory System (The "Knowledge Base")

**What it does:** Persistent, multi-layered storage with semantic recall and reflection capabilities.

**Layers (Low to High):**

1. **Core Memory** (`LyrixaMemorySystem`)
   - SQLite-backed local persistence
   - Manages: conversations, projects, preferences, learning
   - Indexes by type, importance, timestamps, tags
   - Uses BLAKE2s hashing for strong deterministic IDs

2. **Advanced Memory** (`AetherraMemoryEngineAdvanced`)
   - Orchestrates core + fractal/concept/episodic structures
   - Generates daily/weekly/thematic narratives
   - Runs reflections (past week, contradictions, blind spots)
   - Memory health monitoring via pulse checks

3. **Conceptual Structures**
   - Concept clustering (semantic grouping)
   - Fractal hierarchies (multi-level organization)
   - Episodic timelines (story-like sequence reconstruction)

4. **Compression** (`QFACMemorySystem`)
   - Adaptive compression for large memory sets
   - Optional quantum bridge for experimentation
   - Modes: classical (default), hybrid, quantum

5. **STORM** (Advanced Feature)
   - Sheaf-Transport Optimized Retrieval Memory
   - Uses topological data analysis + optimal transport for semantic consistency
   - Shadow mode by default (metrics-only, no production impact)

**Example Recall Flow:**

```
Query: "What have I learned about API authentication?"
  → Strategy: Hybrid (combine vector + conceptual + episodic)
  → Core: SQL recall with importance ranking
  → Conceptual: Find related concept clusters
  → Episodic: Reconstruct learning story from episodes
  → STORM: Check topological consistency (shadow mode)
  → Result: Ranked semantic memories with confidence scores
```

**Config:** Environment variables

- `AETHERRA_QFAC_MODE`: classical | hybrid | quantum (default: classical)
- `AETHERRA_MEMORY_STORM`: 0 (off) | 1 (shadow) | 2 (full) — default shadow

---

### 3. 🔌 Plugin System (The "Extensions")

**What it does:** Allows safe, sandboxed addition of capabilities without forking core code.

**Plugin Ecosystem:**

- **14 core plugins** across 9 categories
- **6 with GUI interfaces** (PySide6)
- Categories: productivity, dev tools, memory, system, social, others

**Example Plugins:**

- Workflow Builder: Compose multi-step automations
- Document Generator: Create formatted output
- Web Research Assistant: Fetch and summarize web content
- Plugin Quality Control: Monitor plugin performance
- Context Surfacing: Intelligent context injection

**Plugin Lifecycle:**

1. Discover: File scan enumerates candidates
2. Validate: Schema & integrity checks
3. Catalog: Entry in `aetherra_plugin_catalog.json`
4. Register: Optionally add to Service Registry
5. Activate: Initialization code runs
6. Execute: Invoked by Lyrixa/Engine/Agents
7. Monitor: Quality metrics collected
8. Retire: Deprecated, archived

**Manifest Schema:**

```json
{
  "name": "workflow_builder_plugin",
  "version": "0.1.0",
  "category": "workflow",
  "entry_point": "plugin.py:Plugin",
  "capabilities": ["plan", "compose_workflow"],
  "permissions": {"memory": true, "filesystem": "read", "network": false}
}
```

**Config:** `aetherra_plugin_catalog.json` (auto-generated)

---

### 4. 🧠 Kernel System (The "OS Kernel")

**What it does:** Core runtime infrastructure that brings Aetherra online and keeps it healthy.

**Components:**

1. **Event Bus (KEB)** — Kernel Event Bus
   - Priority-based queue system
   - Routes events to subscribers
   - Guarantees delivery order within priority level

2. **Service Registry**
   - Runtime component discovery
   - Health status tracking
   - Dependency management

3. **Module Manager**
   - Dynamic loading/unloading
   - Initialization sequencing
   - Lifecycle callbacks

4. **HMR Controller** — Hot Module Reload
   - Live code updates without full restart
   - Rollback to prior state if needed
   - Metrics for change validation

5. **Night Cycle** — Background Maintenance
   - Memory consolidation
   - Plugin health checks
   - Learning loop updates

**Boot Sequence:**

```
1. Service Registry setup
2. Core systems load (Memory, Plugins, Engine, Hub)
3. Kernel loop startup
4. System activation & health validation
5. Main operation loop (listening for events)
6. Graceful shutdown on request
```

**Config:** `config.json`

- Service timeouts
- Queue priorities (high/normal/background)
- Cycle frequencies

---

### 5. 🤖 AI Engine (The "Reasoning Core")

**What it does:** Multi-provider LLM integration with reasoning, RAG, and conversation flows.

**Capabilities:**

- **Multi-Provider Support:** LLM fallback (primary + backup providers)
- **Retrieval-Augmented Generation (RAG):** Inject memory context into reasoning
- **Streaming Conversation:** SSE v2 for live feedback
- **Impact Analysis:** Blast radius assessment for code changes
- **Orchestration Planning:** Multi-step task decomposition

**Flow Example:**

```
User: "Generate a test for the auth API"
  → Engine: Understand intent (generate tests, auth context)
  → RAG: Recall similar tests from memory via semantic search
  → LLM: Generate Python test code with examples
  → Verify: Run syntax check, basic execution
  → Stream: Send generated code line-by-line to user
  → Store: Save to code workspace, log to memory
```

**Config:** Environment variables

- `AETHERRA_AI_API_ENABLED`: 1 (enable chat endpoints)
- `AETHERRA_AI_API_STREAM`: 1 (enable streaming)
- `AETHERRA_AI_STREAM_CHUNK_SIZE`: Bytes per chunk (default: 256)

---

### 6. 🎯 Agent System (The "Executor")

**What it does:** Coordinates specialized agents to execute complex, multi-step tasks.

**Components:**

- **Orchestrator:** Breaks goals into subtasks
- **Decision Engine:** Evaluates options with risk assessment
- **Autonomy Governor:** Enforces safety limits
- **Plugin Manager:** Invokes plugins as tools

**Execution Model:**

```
Task: "Refactor authentication module"
  → Decompose: Split into subtasks (analyze → refactor → test → review)
  → Assign: Route to appropriate agents (analyzer → coder → tester → reviewer)
  → Execute: Run agents in sequence with rollback capability
  → Monitor: Track progress, adjust on errors
  → Complete: Aggregate results, update memory
```

**Safety Features:**

- Forbidden operation checks
- Risk threshold enforcement
- File-change limits
- API rate-limit validation
- Breaking-change approval rules

---

### 7. 🔐 Security System (The "Guard")

**What it does:** Multi-layered defense protecting against unauthorized access and malicious code.

**Defense Layers:**

1. **Network Layer**
   - Firewall allow-list only
   - Network allowlist (AETHERRA_NETWORK_ALLOWLIST)
   - TLS 1.3+ encryption

2. **Application Layer**
   - Authentication (JWT, API keys)
   - Authorization (RBAC, permission checks)
   - Input validation & sanitization
   - Rate limiting

3. **Data Layer**
   - AES-256 encryption at rest
   - TLS encryption in transit
   - Data classification (public/internal/confidential)

4. **Identity Layer**
   - Strong password policies
   - Multi-factor authentication (optional)
   - Session timeout & rotation
   - SSO/OAuth support

5. **Script/Plugin Layer**
   - .aether script signature verification
   - Plugin manifest validation
   - Safe sandbox isolation
   - Capability-based permission model

**Strict Mode (Production):**

```powershell
$env:AETHERRA_SCRIPT_VERIFY_STRICT='1'
$env:AETHERRA_SIGNING_STRICT='1'
$env:AETHERRA_NET_STRICT='1'
# Any unsigned scripts → FAIL
# Any unauthorized network → BLOCKED
```

---

### 8. 🎨 Lyrixa (The "Interface")

**What it does:** Conversational AI assistant and code studio interface for Aetherra.

**Interaction Modes:**

- **Chat:** Natural language conversation with Aetherra capabilities
- **Code Studio:** IDE-grade editing with AI-native orchestration
- **Workflows:** Scriptable multi-step automation using .aether language
- **Agents:** Invoke specialized agents for complex tasks

**GUI Features (PySide6):**

- Chat window with streaming support
- File explorer and code editor
- Plugin browser and manager
- Memory inspector and reflection viewer
- Metrics dashboard and health monitor
- Terminal and command palette

**Code Studio Pipeline:**

```
Spec (intent) → Tests (acceptance criteria)
  → Plan (steps, files, risks)
  → Generate (patch, diff)
  → Verify (build, lint, test, security)
  → Sign (script/plugin signing)
  → Commit (git integration)
```

---

### 9. 📜 Aether Script Language (The "Workflow DSL")

**What it does:** Domain-specific language for defining and executing workflows with safety guarantees.

**Example Workflow:**

```yaml
# workflows/parallel_demo.aether
name: "Parallel Workflow Demo"
version: "1.0.0"

steps:
  - parallel:
      - task: "step_a"
        // Runs in parallel
      - task: "step_b"
        // Runs in parallel

  - sequential:
      - task: "step_c"
        // Waits for parallel to complete
      - task: "step_d"

safety:
  max_retries: 3
  timeout_seconds: 60
  rollback: true
```

**Features:**

- Parallel & sequential execution
- Error handling (on_error clauses)
- Plugin integration (invoke capabilities)
- Conditional branches
- Loop structures
- Signing & verification (ed25519)
- Strict mode validation

**Execution:**

```powershell
python aether.py workflows/parallel_demo.aether --sign --verify-strict
```

---

### 10. 🏥 Homeostasis System (The "Health Monitor")

**What it does:** Continuous system monitoring with automatic self-healing.

**Monitoring:**

- Kernel cycle health (timing, error counts)
- Memory consistency (integrity checks)
- Plugin load success rates
- Consciousness loop responsiveness
- Security policy violations
- Resource usage (CPU, memory, disk)

**Healing Actions:**

- Restart failed components
- Flush corrupted cache
- Rescan plugin catalog
- Consolidate memory
- Escalate to human if needed

**Example Health Check:**

```
Check: Plugin discovery
  → Expected: 14 plugins found
  → Actual: 12 plugins found
  → Action: Rescan, reload catalog
  → Notify: Log warning, alert operator
  → Result: Restored to expected state
```

---

## How Aetherra Works: A Typical Conversation

### Scenario: User asks Aetherra to analyze code quality

```
(1) USER INPUT
    Lyrixa Chat: "Analyze our authentication module for security issues"

(2) CONSCIOUSNESS PERCEIVES
    Event Bus: Message received
    Consciousness: Appraises importance (high), update arousal (↑)

(3) MEMORY RECALLS CONTEXT
    Recall: Find similar code analysis memories
    Result: 3 prior analysis docs + security best practices

(4) AI ENGINE REASONS
    Prompt with context: "Given these prior analyses, audit auth.py"
    LLM: Generates analysis with specific risk areas

(5) AGENT SYSTEM EXECUTES
    Orchestrator: Break into subtasks
      a. Run static analyzer (plugins/reflector)
      b. Check for common vulnerabilities (security rules)
      c. Compare against security baseline
      d. Generate report

(6) VERIFICATION GATE
    Verify: Check if findings are accurate
    Validate: Ensure no false positives

(7) CONSCIOUSNESS ACTS
    Decision: Send analysis to user via streaming
    Safety Check: Verify no sensitive data leaked

(8) LYRIXA RESPONDS
    Chat stream: "Found 3 issues:"
    - Issue 1: Missing input validation (HIGH)
    - Issue 2: Cleartext password logging (CRITICAL)
    - Issue 3: No rate limiting (MEDIUM)

(9) MEMORY LEARNS
    Store: Document this analysis
    Concept: Link to authentication, security patterns
    Reflection: Scheduled meta-analysis of patterns

(10) HOMEOSTASIS CHECKS
     Health: All subsystems OK
     Metrics: Log response time, quality score
     Status: Ready for next request
```

---

## Data Flow Architecture

### Request/Response Path (Chat Example)

```
User Input
    ↓
[Hub] HTTP POST /api/lyrixa/chat
    ↓
[Auth] Verify JWT token
    ↓
[Kernel] Route to Lyrixa service
    ↓
[Consciousness] Perceive → Appraise event
    ↓
[Memory] Semantic recall (query context)
    ↓
[Engine] LLM call with context + prompt
    ↓
[Safety] Verify outputs safe
    ↓
[Hub] SSE v2 streaming response
    ↓
User receives stream
    ↓
[Memory] Store interaction
    ↓
[Homeostasis] Log metrics
```

### Persistence Path (Memory Save)

```
Store Operation
    ↓
[Memory] LyrixaMemorySystem._generate_memory_id()
         → BLAKE2s hash for compact strong ID
    ↓
[SQLite] INSERT into memories table
         with indexes (type, importance, created_at)
    ↓
[QFAC] Optional compression if hybrid mode
    ↓
[Concept Clustering] Group semantically
    ↓
[Episodic Timeline] Add to narrative sequence
    ↓
[Pulse] Health check (gaps, drift alerts)
    ↓
Operation complete, ID returned
```

---

## Configuration & Deployment

### Environment Variables (Key Ones)

| Variable                        | Effect                     | Default   | Use Case              |
| ------------------------------- | -------------------------- | --------- | --------------------- |
| `AETHERRA_PROFILE`              | Activates strictness level | prod/test | "prod" for release    |
| `AETHERRA_REQUIRE_CAPABILITIES` | Enforce capability gates   | 1         | Strict mode           |
| `AETHERRA_SCRIPT_VERIFY_STRICT` | .aether signature required | 1         | Production            |
| `AETHERRA_SIGNING_STRICT`       | Plugin signing required    | 1         | Production            |
| `AETHERRA_NET_STRICT`           | Network allowlist mode     | 1         | Restrict outbound     |
| `AETHERRA_AI_API_ENABLED`       | Enable chat endpoints      | 0         | Turn on AI            |
| `AETHERRA_AI_API_STREAM`        | Enable streaming           | 0         | Live responses        |
| `AETHERRA_QFAC_MODE`            | Memory compression         | classical | hybrid/quantum opt-in |
| `AETHERRA_MEMORY_STORM`         | STORM retrieval            | 0 (off)   | 1=shadow, 2=full      |
| `AETHERRA_QUIET`                | Suppress logs              | 0         | Reduce output         |

### Deployment Tiers

| Tier           | Use           | Availability | Persistence | Monitoring        |
| -------------- | ------------- | ------------ | ----------- | ----------------- |
| **Dev**        | Local testing | Best-effort  | Optional    | Console logs      |
| **Test**       | CI/CD         | Best-effort  | Ephemeral   | Basic metrics     |
| **Staging**    | Pre-prod      | High         | Persistent  | Full + alerts     |
| **Production** | Live          | Critical     | Replicated  | Full + escalation |

### Installation (Quickest Path)

```powershell
# 1. Clone & venv
git clone https://github.com/AetherraLabs/Aetherra.git
cd Aetherra
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install
pip install -r requirements.txt

# 3. Run Hub (enables API)
$env:AETHERRA_AI_API_ENABLED='1'
python -m aetherra_hub.compat

# 4. In another shell: Chat
Invoke-RestMethod -Method Post -Uri 'http://localhost:3001/api/lyrixa/chat' `
  -ContentType 'application/json' `
  -Body '{"message":"hello"}'
```

---

## Integration Points

### APIs (REST + SSE)

| Endpoint                    | Method | Purpose         | Auth |
| --------------------------- | ------ | --------------- | ---- |
| `/api/lyrixa/chat`          | POST   | Chat query      | JWT  |
| `/api/ai/stream`            | GET    | SSE streaming   | JWT  |
| `/api/memory/recall`        | POST   | Semantic recall | JWT  |
| `/api/plugins/list`         | GET    | Plugin catalog  | JWT  |
| `/api/agents/execute`       | POST   | Run agent task  | JWT  |
| `/api/scripts/execute`      | POST   | Run .aether     | JWT  |
| `/api/consciousness/status` | GET    | System health   | JWT  |

### Webhook Support

- Event notifications (async)
- Custom plugin callbacks
- External system integration

### Service Registry

- Dynamic service discovery
- Health status polling
- Dependency resolution

---

## Testing & Validation

### Test Suite Overview

| Type            | Location             | Purpose                  | Speed  |
| --------------- | -------------------- | ------------------------ | ------ |
| **Unit**        | tests/unit/          | Individual functions     | Fast   |
| **Integration** | tests/integration/   | Component interactions   | Medium |
| **Smoke**       | tests/smoke/         | Basic functionality      | Fast   |
| **Capability**  | tests/capabilities/  | System claims validation | Slow   |
| **Standalone**  | test_*_standalone.py | Roadmap validation       | Medium |

### Recent Validation Results (Week 10 Complete)

- **Phase 2a Reflector:** 3 new + 16 existing = 19/19 ✅
- **Phase 2b Analysis/Codegen:** 100/100 passing ✅
- **Phase 3 Autonomy:** 19/19 with negative paths ✅
- **Phase 4 Learning:** 18/18 with benchmarks ✅
- **Week-10 Matrix:** 15/15 scenarios, all categories ✅
- **Regression:** 10/10 repeat runs at 100% stability ✅

---

## Release & Packaging

### Build Process

```powershell
# 1. Clean
python -c "import shutil; shutil.rmtree('dist', ignore_errors=True)"

# 2. Build wheel + sdist
python -m build

# 3. Generate SBOM
python tools/generate_sbom.py --output dist/aetherra-sbom.json

# 4. Create manifest (optionally signed)
python tools/sign_release_manifest.py --dist dist --version 0.1.0-beta.1
```

### Release Artifacts

- `aetherra-0.1.0.beta.1-py3-none-any.whl` — Installable package
- `aetherra-0.1.0.beta.1.tar.gz` — Source distribution
- `aetherra-sbom.json` — CycloneDX Software Bill of Materials
- `release-manifest.json` — Artifact hashes (+ optional signature)

### Go/No-Go Gates

8 deterministic gates ensure quality:

1. Launcher smoke test
2. Chat transport & SSE v2 resume
3. Security strict modes
4. Memory core + QFAC fallback
5. Kernel HMR + quiesce
6. Plugin discovery
7. .aether execution
8. Performance benchmarks

---

## Production Readiness Metrics

| Metric                   | Target | Actual         | Status |
| ------------------------ | ------ | -------------- | ------ |
| Test coverage            | 80%+   | Comprehensive  | ✅      |
| Integration tests        | 100%   | 100+ scenarios | ✅      |
| Critical security issues | 0      | 0              | ✅      |
| Code gen latency         | <10s   | 2-5s avg       | ✅      |
| Reflector latency        | <100ms | Sub-100ms      | ✅      |
| Plugin load success      | >95%   | 14/14 (100%)   | ✅      |
| Week-10 matrix pass      | 1.0    | 15/15 scenes   | ✅      |
| Regression stability     | 1.0    | 10/10 runs     | ✅      |

---

## Key Innovations

1. **Consciousness as First-Class System**: Adaptive awareness loop rather than reactive execution
2. **Multi-Layer Memory**: From SQLite persistence to topological-consistency STORM retrieval
3. **Safety-by-Default**: Policy-integrated, rollback-capable, always-auditable
4. **Plugin Ecosystem**: Extensible without forking, with auto-discovery and lifecycle management
5. **Aether Script Language**: Domain-specific DSL for workflows with signing and strict verification
6. **Homeostasis**: Continuous self-monitoring with autonomous healing
7. **Code-to-Production Pipeline**: Integrated analysis, generation, verification, security, and signing

---

## Next: Release Preparation

With all system documentation reviewed and validation complete, proceed to:

1. **Build Release Candidate**
   - Run gate suite
   - Generate release manifest
   - Create signed artifacts

2. **Publishing**
   - Host documentation
   - Create PyPI release
   - Tag on GitHub

3. **Week 11-12 Release Hardening** (Post-Beta)
   - Advanced deployment runbooks
   - Trend-aware rollout strategies
   - Disaster recovery validation

---

**Document ID:** AETHERRA-COMPLETE-OVERVIEW-2026-03-12
**Status:** Complete & Reviewed
**Ready for Release Prep:** Yes ✅
