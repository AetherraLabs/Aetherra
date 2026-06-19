# Aetherra & Lyrixa — Pre-Pack Validation Tracking

**Date Started:** 2025-10-31
**Target Release:** Beta v0.9.0
**Owner:** Aetherra Labs
**Status:** 🟡 IN PROGRESS

---

## Quick Status Dashboard

| Category               | Status | Critical Blockers | Warnings | Notes                    |
| ---------------------- | ------ | ----------------- | -------- | ------------------------ |
| **0. One-Glance**      | 🟡      | 0                 | 0        | Need runtime validation  |
| **1. Kernel System**   | 🟡      | 0                 | 0        | Queue metrics needed     |
| **2. AI Engine**       | 🟡      | 0                 | 0        | Session mgmt ready       |
| **3. Agent System**    | 🟡      | 0                 | 0        | Need task flow test      |
| **4. Chat System**     | 🟡      | 0                 | 0        | SSE v2 validation needed |
| **5. Memory System**   | 🟡      | 0                 | 1        | STORM shadow mode        |
| **6. Security**        | 🔴      | 1                 | 2        | **STRICT MODE REQUIRED** |
| **7. Aether Scripts**  | 🟡      | 0                 | 0        | Need signature audit     |
| **8. Coding (Lyrixa)** | 🟡      | 0                 | 0        | Spec→Tests gate          |
| **9. Homeostasis**     | 🟢      | 0                 | 0        | Metrics flowing          |
| **10. Lyrixa Bridge**  | 🟡      | 0                 | 0        | Need persona test        |
| **11. AI Trainer**     | 🟢      | 0                 | 0        | Correctly disabled       |
| **12. Hub/Endpoints**  | 🟡      | 0                 | 0        | Need smoke suite         |
| **13. Packaging**      | 🔴      | 3                 | 5        | **NOT READY**            |

**Legend:** 🟢 Ready | 🟡 In Progress | 🔴 Blocked/Critical

---

## Section 0: One-Glance Status

### What to Verify First

- [ ] **Kernel loop & queues** — running, heartbeats flowing, metrics counters rising, HMR available
  - How: Check `/api/kernel/status`, `/api/kernel/metrics`
  - Verify: queue sizes, backpressure, HMR counters
  - Status: ⏳ PENDING
  - Notes: _Need to start hub and run live check_

- [ ] **AI Engine** — session creation, memory store/recall, response payload
  - How: `/api/ai/ask` smoke test
  - Verify: `session_id`, `relevant_memories_count`, `confidence`
  - Status: ⏳ PENDING
  - Notes: _Need coordinator runtime test_

- [ ] **Memory (Core + Advanced)** — SQLite present, store/recall OK
  - How: Call advanced engine health & narrative
  - Verify: typed recall works
  - Status: ⏳ PENDING
  - Notes: _Database integrity check needed_

- [ ] **Chat System** — SSE v2 envelopes monotonic
  - How: Stream and confirm `Last-Event-ID` resume
  - Verify: final with normalized `evidence[]`
  - Status: ⏳ PENDING
  - Notes: _Need SSE v2 integration test_

- [ ] **Agents** — submit task, see status lifecycle
  - How: `/api/tasks` + `/api/tasks/{id}`
  - Verify: pending → running → completed
  - Status: ⏳ PENDING
  - Notes: _If enabled_

- [ ] **Security** — strict flags block unsigned scripts/plugins
  - How: Run signature verifier + test jailbreak string
  - Verify: prompt-injection guard triggers
  - Status: 🔴 **CRITICAL**
  - Notes: _MUST enable AETHERRA_SIGNING_STRICT=1 for prod_

- [ ] **Homeostasis & Maintenance** — health score reported
  - How: Check metrics & logs
  - Verify: auto fixes counted, metrics bridged
  - Status: ⏳ PENDING
  - Notes: _Metrics flowing, need validation_

---

## Section 1: Kernel System (OS Runtime & Boot)

### Capabilities Implemented ✅

- [x] Priority queues (high/normal/background) with metrics
- [x] Heartbeats per service
- [x] Registry status snapshots
- [x] Health broadcasts (`kernel.health`)
- [x] Night Cycle orchestration (02:00–04:00)
- [x] Plugin invoke safety (capability checks, timeouts, CB, retries, DLQ)
- [x] HMR Phase 1-2 (quiesce, swap, rollback, audit)

### Verification Checklist

- [ ] **Queue Status Check**
  ```powershell
  # Test with hub running
  Invoke-WebRequest -Uri "http://localhost:3001/api/kernel/status" | ConvertFrom-Json
  ```
  - Expected: `running`, `uptime`, `queue_sizes`, `hmr` counters
  - Status: ⏳ PENDING

- [ ] **HMR Swap Test**
  ```powershell
  $env:AETHERRA_HMR_ENABLED = "1"
  # Call HMR reload task via API
  ```
  - Expected: swap/rollback telemetry
  - Status: ⏳ PENDING

- [ ] **Circuit Breaker Test**
  - Force plugin timeout
  - Verify CB open/cooldown counters
  - Status: ⏳ PENDING

### Environment Variables

| Variable                             | Default | Prod Value | Verified |
| ------------------------------------ | ------- | ---------- | -------- |
| `AETHERRA_KERNEL_QSIZE_HIGH`         | 100     | 200        | ⏳        |
| `AETHERRA_KERNEL_QSIZE_NORMAL`       | 500     | 1000       | ⏳        |
| `AETHERRA_KERNEL_QSIZE_BACKGROUND`   | 1000    | 2000       | ⏳        |
| `AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC` | 30      | 30         | ⏳        |
| `AETHERRA_HMR_ENABLED`               | 0       | **0**      | ⏳        |
| `AETHERRA_KERNEL_DLQ_ENABLED`        | 1       | 1          | ⏳        |

**🔴 BLOCKER:** HMR must be disabled (`0`) for production builds

---

## Section 2: Aetherra AI Engine

### Capabilities Implemented ✅

- [x] Session management
- [x] Message pipeline (persist → recall → reason → synthesize)
- [x] Task execution via Agent Orchestrator
- [x] System status payload aggregation
- [x] Graceful mock fallbacks

### Verification Checklist

- [ ] **Session Creation Test**
  ```python
  from Aetherra.ai_engine.coordinator import AetherraAICoordinator
  coordinator = AetherraAICoordinator()
  session_id = coordinator.start_conversation()
  assert session_id is not None
  ```
  - Status: ⏳ PENDING

- [ ] **Message Processing Test**
  ```python
  result = coordinator.process_message(session_id, "Test query")
  assert result.get("relevant_memories_count", 0) >= 0
  assert "confidence" in result
  ```
  - Status: ⏳ PENDING

- [ ] **Task Execution Test**
  ```python
  task_id = coordinator.execute_task("test_task", {})
  status = coordinator.get_task_status(task_id)
  # Verify: pending → running → completed
  ```
  - Status: ⏳ PENDING

### Planned Features 🧪

- [ ] RAG pipeline with evidence window
- [ ] Confidence breakdown (model/grounding/coherence/safety)
- Status: Future release

---

## Section 3: Agent System

### Capabilities Implemented ✅

- [x] Agent registry
- [x] Task submit/status
- [x] Sequential/parallel stubs
- [x] Capability checks
- [x] Bounded retries/timebox
- [x] Optional Hub API (`/api/agents`, `/api/tasks`, SSE stream)

### Verification Checklist

- [ ] **Agent Registry Test**
  ```python
  from aetherra_agent_fabric import AetherraAgentFabric
  fabric = AetherraAgentFabric()
  agents = fabric.list_agents()
  assert len(agents) > 0
  ```
  - Status: ⏳ PENDING

- [ ] **Task Submission Test**
  ```python
  task_id = fabric.submit_task({
      "task_name": "test",
      "task_data": {}
  })
  status = fabric.get_task_status(task_id)
  # Verify lifecycle
  ```
  - Status: ⏳ PENDING

- [ ] **Capability Unavailable Test**
  ```python
  # Submit task with unavailable capability
  # Expect: capability_unavailable error
  ```
  - Status: ⏳ PENDING

---

## Section 4: Chat System

### Capabilities Implemented ✅

- [x] `/api/ai/ask` and `/api/ai/stream` with SSE v2 envelopes
- [x] Resume via `Last-Event-ID`
- [x] Normalized `evidence[]`
- [x] Policy snapshot events
- [x] Lyrixa bridge `/api/lyrixa/chat`
- [x] Persona defaulting & edit plan synthesis
- [x] Backpressure + DLQ parity
- [x] Rate limits & circuit breakers

### Verification Checklist

- [ ] **SSE v2 Envelope Test**
  ```powershell
  # Stream a prompt
  curl -N http://localhost:3001/api/ai/stream -d '{"message":"test"}'
  # Verify: status → policy → usage → final
  # Check: confidence_breakdown present
  ```
  - Status: ⏳ PENDING

- [ ] **Resume Test**
  ```powershell
  # Reconnect with Last-Event-ID
  # Verify: strictly increasing IDs
  ```
  - Status: ⏳ PENDING

- [ ] **Lyrixa Bridge Test**
  ```powershell
  curl -X POST http://localhost:3001/api/lyrixa/chat -d '{"message":"test"}'
  # Verify: persona default, edit_plan[] mirroring
  ```
  - Status: ⏳ PENDING

### Environment Variables

| Variable                        | Default | Prod Value   | Verified |
| ------------------------------- | ------- | ------------ | -------- |
| `AETHERRA_AI_API_ENABLED`       | 0       | 1            | ⏳        |
| `AETHERRA_AI_API_STREAM`        | 1       | 1            | ⏳        |
| `AETHERRA_AI_API_REQUIRE_TOKEN` | 0       | **1**        | 🔴        |
| `AETHERRA_AI_API_TOKEN`         | -       | **REQUIRED** | 🔴        |
| `AETHERRA_CHAT_RATE_LIMIT`      | 60      | 60           | ⏳        |

**🔴 BLOCKER:** Token authentication MUST be enabled for production

---

## Section 5: Memory System

### Capabilities Implemented ✅

- [x] Core SQLite store/recall with typed models
- [x] Legacy adapters
- [x] Deterministic IDs (BLAKE2s-128)
- [x] Advanced Orchestrator (narratives, reflections, pulse/health)
- [x] Concept clusters, episodic timeline
- [x] QFAC compression with quantum-hybrid bridge
- [x] STORM retrieval (shadow mode prod-ready)

### Verification Checklist

- [ ] **Core Memory Test**
  ```python
  from Aetherra.memory.core.store import AetherraMemoryStore
  store = AetherraMemoryStore()

  # Write/read test
  store.store_memory(...)
  result = store.recall_memories(...)

  # Health check
  health = store.health_pulse()
  assert "coherence" in health
  assert "drift" in health
  assert "compression_ratio" in health
  ```
  - Status: ⏳ PENDING

- [ ] **QFAC Test**
  ```powershell
  $env:AETHERRA_QFAC_MODE = "hybrid"
  # Store & retrieve
  # Inspect get_system_status() for node stats
  ```
  - Status: ⏳ PENDING
  - ⚠️ **WARNING:** QFAC is experimental

- [ ] **STORM Test**
  ```powershell
  $env:AETHERRA_MEMORY_STORM = "1"
  # Run recalls
  # Confirm metadata.storm (ot, coh, pers)
  # Check shadow comparison metrics
  ```
  - Status: ⏳ PENDING
  - ⚠️ **WARNING:** STORM is shadow mode

### Environment Variables

| Variable                | Default  | Prod Value | Verified |
| ----------------------- | -------- | ---------- | -------- |
| `AETHERRA_QFAC_MODE`    | disabled | disabled   | ⏳        |
| `AETHERRA_MEMORY_STORM` | 0        | **0**      | ⏳        |
| `AETHERRA_STORM_SHADOW` | 1        | 1          | ⏳        |

**🟡 RECOMMENDATION:** Keep QFAC and STORM disabled for initial production release

---

## Section 6: Security System 🛡️

### Capabilities Implemented ✅

- [x] `.aether` signing (HMAC-SHA256)
- [x] Strict verifier & static risk report
- [x] Plugin manifest signing (ed25519, partial)
- [x] Secrets mgmt with optional encrypt-at-rest
- [x] Rotation & leak checks
- [x] Sandbox & capability model
- [x] Network allow/deny
- [x] Prompt-injection heuristic guard

### Verification Checklist

- [ ] **Script Signing Test**
  ```powershell
  python tools/verify_aether_scripts.py --strict --root . --output aether_static_report.md
  # Inspect report for unsigned scripts
  ```
  - Status: ⏳ PENDING
  - **CRITICAL:** Must pass 100%

- [ ] **Strict Mode Test**
  ```powershell
  $env:AETHERRA_SIGNING_STRICT = "1"
  # Attempt to load unsigned plugin
  # Expected: failure/rejection
  ```
  - Status: ⏳ PENDING
  - 🔴 **BLOCKER:** Must enforce in prod

- [ ] **Network Policy Test**
  ```powershell
  $env:AETHERRA_NET_STRICT = "1"
  $env:AETHERRA_NETWORK_ALLOWLIST = "localhost,127.0.0.1,.aetherra.dev"
  # Call unallowlisted host
  # Expected: policy deny
  ```
  - Status: ⏳ PENDING
  - 🔴 **BLOCKER:** Must enforce in prod

- [ ] **Prompt Injection Test**
  ```python
  # Test with canned jailbreak payloads
  # Verify guard triggers and blocks
  ```
  - Status: ⏳ PENDING

- [ ] **Secrets Encryption Test**
  ```powershell
  $env:AETHERRA_KEYS_MASTER = "<master-key>"
  # Verify secrets encrypted at rest
  ```
  - Status: ⏳ PENDING
  - ⚠️ **WARNING:** Required for production

### Environment Variables

| Variable                        | Default | Prod Value   | Verified |
| ------------------------------- | ------- | ------------ | -------- |
| `AETHERRA_SIGNING_STRICT`       | 0       | **1**        | 🔴        |
| `AETHERRA_SCRIPT_VERIFY_STRICT` | 0       | **1**        | 🔴        |
| `AETHERRA_REQUIRE_STRICT`       | 0       | **1**        | 🔴        |
| `AETHERRA_REQUIRE_CAPABILITIES` | 0       | **1**        | ⏳        |
| `AETHERRA_NET_STRICT`           | 0       | **1**        | 🔴        |
| `AETHERRA_NETWORK_ALLOWLIST`    | -       | **REQUIRED** | 🔴        |
| `AETHERRA_KEYS_MASTER`          | -       | **REQUIRED** | 🔴        |

**🔴 CRITICAL BLOCKERS:** 6 security flags MUST be set for production

---

## Section 7: Aether Script Language

### Capabilities Implemented ✅

- [x] v1.1 grammar (goals, workflows, parallel/await)
- [x] Transactions
- [x] `require:`, `policy:`, `plugin_contract:`
- [x] I/O schema checks
- [x] Trace & narration
- [x] Determinism profile

### Verification Checklist

- [ ] **Workflow Execution Test**
  ```powershell
  $env:AETHERRA_TRACE = "1"
  python aether.py workflows/parallel_workflow_demo.aether
  # Verify: trace output, retry, timeout, requires gates
  ```
  - Status: ⏳ PENDING

- [ ] **Strict Requires Test**
  ```powershell
  $env:AETHERRA_REQUIRE_STRICT = "1"
  # Run workflow with missing plugin
  # Expected: abort
  ```
  - Status: ⏳ PENDING

- [ ] **Signature Audit**
  ```powershell
  python tools/verify_aether_scripts.py --strict
  # Review aether_static_report.md
  ```
  - Status: ⏳ PENDING
  - **CRITICAL:** All scripts must be signed

---

## Section 8: Coding System (Lyrixa Code Studio)

### Capabilities Implemented ✅

- [x] IDE-grade editing, refactors, test runners
- [x] Security/scans
- [x] Autonomy modes (Assist/Co-drive/Autopilot)
- [x] Spec→Tests gate
- [x] Plugin scaffolder
- [x] Sign/verify tools

### Verification Checklist

- [ ] **Test Generation (Spec→Tests Gate)**
  ```
  # Use Command Palette to generate unit/acceptance tests
  # Verify: gate enforces spec presence before patch
  ```
  - Status: ⏳ PENDING

- [ ] **Quality Gates Test**
  ```powershell
  python tools/quality_gates.py
  # Verify: coverage no-drop enforced
  ```
  - Status: ⏳ PENDING

- [ ] **Aether Risk Analyzer**
  ```powershell
  # Run .aether risk analyzer
  # Confirm PASS/FAIL gating
  ```
  - Status: ⏳ PENDING

---

## Section 9: Homeostasis & Maintenance

### Capabilities Implemented ✅

- [x] Metric collection (15+)
- [x] PID controller
- [x] Actuators (service mgmt, resource tuning, GC, cognitive)
- [x] Alerting
- [x] Night-cycle optimization
- [x] Autonomous error corrector (6 categories)
- [x] Self-improvement metrics bridge
- [x] Self-incorporation service
- [x] Health APIs & metrics

### Verification Checklist

- [ ] **Health Score Check**
  ```python
  # Confirm system_health_score
  # Verify: actions_executed, errors_detected, fixes_successful
  ```
  - Status: 🟢 READY
  - Notes: Metrics flowing

- [ ] **Self-Incorporation Scan**
  ```python
  # Trigger scan
  # Expect: index entries, classifications
  # Verify: non-trusted code quarantined
  ```
  - Status: ⏳ PENDING

- [ ] **Induced Fault Test**
  ```python
  # Trigger fault condition
  # Verify: auto-correction triggered
  # Check: metrics increment
  ```
  - Status: ⏳ PENDING

---

## Section 10: Lyrixa Chat & UI Bridge

### Capabilities Implemented ✅

- [x] Lyrixa chat bridge stabilized
- [x] Persona default
- [x] Edit plan mirroring suggestions
- [x] Confidence floor 0.5
- [x] CLI/UI clients consume normalized stream

### Verification Checklist

- [ ] **Persona Default Test**
  ```powershell
  curl -X POST http://localhost:3001/api/lyrixa/chat -d '{"message":"test"}'
  # Verify: persona default {name:"Lyrixa"} on empty identity
  ```
  - Status: ⏳ PENDING

- [ ] **Edit Plan Mirroring Test**
  ```python
  # Verify: suggestions[] → edit_plan[] 1:1 mapping
  ```
  - Status: ⏳ PENDING

---

## Section 11: AI Trainer System

### Status: Design Scaffolding Only 🧪

- [ ] **Trainer Disabled Check**
  ```powershell
  # Ensure AETHERRA_TRAINER_ENABLED absent/0 in prod builds
  ```
  - Status: 🟢 READY
  - Notes: Correctly disabled

### Environment Variables

| Variable                   | Default | Prod Value | Verified |
| -------------------------- | ------- | ---------- | -------- |
| `AETHERRA_TRAINER_ENABLED` | 0       | **0**      | 🟢        |

**✅ CONFIRMED:** Trainer is OFF for production

---

## Section 12: Hub/Endpoints & Env Index

### Endpoints to Smoke Test

- [ ] `/health` - Basic health check
- [ ] `/status` - System status
- [ ] `/api/stats` - System statistics
- [ ] `/api/memory/status` - Memory system status
- [ ] `/api/ai/ask` - AI query endpoint
- [ ] `/api/ai/stream` - AI streaming endpoint
- [ ] `/api/agents` - Agent registry (if enabled)
- [ ] `/api/tasks` - Task submission (if enabled)
- [ ] `/api/kernel/status` - Kernel status
- [ ] `/api/kernel/metrics` - Kernel metrics
- [ ] `/api/lyrixa/chat` - Lyrixa chat bridge

Status: ⏳ PENDING - Need comprehensive smoke suite

---

## Section 13: Pre-.exe Packaging — Master Checklist

### A. Deterministic/Testable Build

- [ ] All tests pass (`pytest`)
  - Status: ⏳ PENDING
  - Command: `pytest -q tests/`

- [ ] Coverage ≥ baseline (no drop)
  - Status: ⏳ PENDING
  - Command: `python tools/quality_gates.py`

- [ ] Smoke tests pass
  - Status: ⏳ PENDING
  - Command: `pytest -q tests/smoke`

- [ ] Go-NoGo gates pass
  - Status: ⏳ PENDING
  - Command: `python tools/run_go_no_go_gates.py --all`

- [ ] LLM setup verified
  - Status: ⏳ PENDING
  - Command: `python tools/verify_llm_setup.py`

### B. Safety & Signing 🛡️

- [ ] All `.aether` scripts signed
  - Status: ⏳ PENDING
  - Command: `python tools/verify_aether_scripts.py --strict`
  - 🔴 **BLOCKER:** Must be 100%

- [ ] All plugins signed (if applicable)
  - Status: ⏳ PENDING
  - 🔴 **BLOCKER:** Required for strict mode

- [ ] Strict mode enforced
  - Status: 🔴 **NOT SET**
  - Required: `AETHERRA_SIGNING_STRICT=1`
  - 🔴 **BLOCKER:** CRITICAL

- [ ] Network policy configured
  - Status: 🔴 **NOT SET**
  - Required: `AETHERRA_NET_STRICT=1` + allowlist
  - 🔴 **BLOCKER:** CRITICAL

- [ ] Secrets encrypted at rest
  - Status: 🔴 **NOT SET**
  - Required: `AETHERRA_KEYS_MASTER`
  - 🔴 **BLOCKER:** CRITICAL

- [ ] Prompt injection guard active
  - Status: ⏳ PENDING
  - Verify: Test with jailbreak payloads

### C. Runtime Health

- [ ] Kernel loop starts clean
  - Status: ⏳ PENDING
  - Verify: No errors in first 60s

- [ ] Heartbeats flow
  - Status: ⏳ PENDING
  - Check: `/api/kernel/status`

- [ ] Memory health stable
  - Status: ⏳ PENDING
  - Check: Health pulse scores

- [ ] No leaked resources
  - Status: ⏳ PENDING
  - Verify: Memory/file handles after 1hr runtime

### D. Memory Systems

- [ ] Core store operational
  - Status: ⏳ PENDING

- [ ] Advanced orchestrator ready
  - Status: ⏳ PENDING

- [ ] QFAC disabled (recommended)
  - Status: ⏳ PENDING
  - Set: `AETHERRA_QFAC_MODE=disabled`

- [ ] STORM disabled (recommended)
  - Status: ⏳ PENDING
  - Set: `AETHERRA_MEMORY_STORM=0`

### E. Chat/Agents/API

- [ ] SSE v2 envelopes correct
  - Status: ⏳ PENDING

- [ ] Resume works (`Last-Event-ID`)
  - Status: ⏳ PENDING

- [ ] Token auth enforced
  - Status: 🔴 **NOT SET**
  - Required: `AETHERRA_AI_API_REQUIRE_TOKEN=1`
  - 🔴 **BLOCKER:** CRITICAL

- [ ] Rate limits configured
  - Status: ⏳ PENDING

- [ ] Agent task lifecycle works
  - Status: ⏳ PENDING

### F. HMR & Strict Modes

- [ ] HMR disabled for pack
  - Status: ⏳ PENDING
  - Set: `AETHERRA_HMR_ENABLED=0`
  - 🔴 **BLOCKER:** Must be OFF

- [ ] Strict requires mode
  - Status: ⏳ PENDING
  - Set: `AETHERRA_REQUIRE_STRICT=1`

- [ ] Capability checks enforced
  - Status: ⏳ PENDING
  - Set: `AETHERRA_REQUIRE_CAPABILITIES=1`

---

## Section 14: Quick Smoke Commands

### Setup Check
```powershell
# LLM setup verification
python tools/verify_llm_setup.py
# Expected: exit 0
```

### Chat SSE Resume
```powershell
# Connect, read 2 events, reconnect with Last-Event-ID
# Confirm strictly increasing IDs
```

### Aether Strict Static
```powershell
$env:AETHERRA_SCRIPT_VERIFY_STRICT = "1"
python tools/verify_aether_scripts.py --strict
# Review: aether_static_report.md
```

### Kernel HMR Swap (Safe)
```powershell
# Enqueue hmr_reload for engine with mode:'safe'
# Assert last_swap_ms recorded
```

### STORM Shadow
```powershell
$env:AETHERRA_MEMORY_STORM = "1"
# Recall a query
# Ensure metadata.storm present and baseline unchanged
```

### Homeostasis Induced Fault
```powershell
# Temporarily raise plugin timeout low to trigger CB
# Check actions_executed & alerts
```

---

## Section 15: Packaging Notes (Windows .exe)

### Profile Configuration

```powershell
# Production profile
$env:AETHERRA_PROFILE = "prod"
$env:AETHERRA_QUIET = "1"
$env:AETHERRA_OFFLINE = "1"  # For air-gapped
```

### Secrets Management

- [ ] Encrypted keys configured
  - `AETHERRA_KEYS_MASTER` required
- [ ] Disallow unscoped key reads
  - Security policy enforced

### Telemetry

- [ ] Default opt-out
- [ ] Explicit enable required
- [ ] Token required before `/api/ai/*` opens

### HMR

- [ ] Leave OFF unless signed patch channel exists
- [ ] Keep audit path under `.aetherra/`

---

## Critical Blockers Summary

### 🔴 MUST FIX BEFORE PACKAGING

1. **Security Strict Mode** (Section 6)
   - `AETHERRA_SIGNING_STRICT=1` ❌
   - `AETHERRA_SCRIPT_VERIFY_STRICT=1` ❌
   - `AETHERRA_NET_STRICT=1` ❌

2. **Token Authentication** (Section 4)
   - `AETHERRA_AI_API_REQUIRE_TOKEN=1` ❌
   - `AETHERRA_AI_API_TOKEN=<value>` ❌

3. **Secrets Encryption** (Section 6)
   - `AETHERRA_KEYS_MASTER=<key>` ❌

4. **HMR Disabled** (Section 1)
   - `AETHERRA_HMR_ENABLED=0` ⏳

5. **All Scripts Signed** (Section 7)
   - 100% signature coverage ⏳

6. **Network Allowlist** (Section 6)
   - `AETHERRA_NETWORK_ALLOWLIST=<hosts>` ❌

---

## Validation Commands Checklist

### Automated Validation Suite

```powershell
# Run comprehensive pre-pack validation
python tools/pre_pack_validation.py --profile prod --verbose

# Review generated report
cat pre_pack_validation_report.json
```

### Manual Spot Checks

```powershell
# 1. Start the full stack
python aetherra_registry_daemon.py
python tools/run_hub_ai_api.py --port 3001
python aetherra_os_launcher.py --mode full -v

# 2. Hit all endpoints
Invoke-WebRequest -Uri "http://localhost:3001/health"
Invoke-WebRequest -Uri "http://localhost:3001/api/kernel/status"
Invoke-WebRequest -Uri "http://localhost:3001/api/memory/status"

# 3. Run smoke tests
pytest -q tests/smoke

# 4. Run capability tests
pytest -q tests/capabilities

# 5. Run Go-NoGo gates
python tools/run_go_no_go_gates.py --all
```

---

## Sign-Off Criteria

### ✅ Ready to Package When:

- [ ] All critical blockers resolved (6 items)
- [ ] All smoke tests pass
- [ ] Coverage no-drop verified
- [ ] Security audit clean
- [ ] All `.aether` scripts signed
- [ ] Runtime stability confirmed (1hr+ uptime)
- [ ] Memory leaks checked
- [ ] Documentation updated

### 📋 Pre-Package Checklist

- [ ] Version number updated in all manifests
- [ ] Changelog finalized
- [ ] Release notes drafted
- [ ] License headers verified
- [ ] Dependencies locked/vendored
- [ ] Build reproducible (checksum verified)

---

## Progress Log

### 2025-10-31
- ✅ Created pre-pack validation suite (`tools/pre_pack_validation.py`)
- ✅ Created tracking document (`docs/prepack/PRE_PACK_CHECKLIST_TRACKING.md`)
- 🟡 Identified 6 critical security blockers
- 🟡 Identified 3 packaging blockers
- ⏳ Awaiting runtime validation tests

### Next Steps
1. Set all critical security flags for production profile
2. Run automated validation suite
3. Execute manual smoke tests
4. Fix any discovered issues
5. Re-validate
6. Sign off for packaging

---

## Notes & Observations

- **Security posture:** Current configuration is development-friendly but NOT production-ready
- **Memory systems:** QFAC and STORM are experimental; recommend disabling for v0.9.0
- **HMR:** Powerful feature but needs signed patch infrastructure before enabling in production
- **Agent system:** Fully functional; can enable or disable via flags
- **Chat system:** SSE v2 implementation looks solid; needs integration testing
- **Homeostasis:** Metrics flowing well; system appears healthy

---

**Last Updated:** 2025-10-31
**Updated By:** Aetherra Labs
**Next Review:** Before .exe packaging
