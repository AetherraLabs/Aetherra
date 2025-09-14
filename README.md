<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

# Aetherra

> AI-native development environment unifying code, memory, and intelligent automation

![Status](https://img.shields.io/badge/Status-STABLE-green)
![Version](https://img.shields.io/badge/Version-v0.3.0-0891b2)
![License](https://img.shields.io/badge/License-GPLv3-0891b2)
![Language](https://img.shields.io/badge/Language-Python%20%2B%20Aetherra-8b5cf6)
![Responsible AI](https://img.shields.io/badge/Responsible%20AI-Policies%20Published-22c55e)

Aetherra pairs a lightweight Hub (APIs + metrics) with the Lyrixa AI assistant,
pluggable memory systems, an intent-driven workflow language (.aether), and
first-class observability. Core subsystems ship ready-to-use: **Engine**,
**Memory**, **Agents**, **Kernel**, **Chat**, **Security**, and **Coding system**.

## Stable Release Acceptance Checklist

✅ **Chat streams**: SSE v2 resume (Last-Event-ID), consistent final payload
with evidence[] and scratchpad_policy.

✅ **Plugin UX**: install/uninstall from GUI; sidebar/panels auto-reconfigure
without blocking chat. (Hub lists/install endpoints provide the backend.)

✅ **Plugin safety**: manifest signing on (or policy explained), capability
gates enforced, network allowlist documented.

✅ **Kernel health**: night cycle runs; heartbeats/metrics green; backpressure
limits set in env (document defaults).

✅ **Memory health**: core works even when optional components are absent;
typed recall + legacy adapters described.

✅ **Spec→Tests gate** enabled in your dev flow; tools/verify_aether_scripts.py
wired in CI.

## v0.3.0 Release Status

| Area                | Status                                                     |
| ------------------- | ---------------------------------------------------------- |
| Tests               | 98 passed, 1 skipped (99%)                                 |
| Security            | All scans clean                                            |
| QFAC & Core Systems | Operational                                                |
| Code Quality        | PEP 585, lint-clean                                        |
| Coverage            | **13.80%** (↑ from 8.36%); gate enforces **no regression** |

**🚀 v0.3.0 shipped as "Stable"** - High test reliability and security readiness achieved.

### Coverage Plan (Post-release)
- **v0.3.1 (≤ 30 days):** ≥ **25%**
- **v0.3.2 (≤ 60 days):** ≥ **40%**
- **v0.3.3 (≤ 90 days):** ≥ **60%**

*Coverage waiver active: No regression below 13.80% allowed; new/changed files require unit tests.*

---

## Project Features

| Subsystem         | Core Capabilities                                           | Value Proposition                               |
| ----------------- | ----------------------------------------------------------- | ----------------------------------------------- |
| **Engine**        | Multi-provider AI routing with deterministic fallbacks      | Reliable intelligence even under outages/quotas |
| **Memory**        | Persistent + quantum-augmented (QFAC) layers                | Rich recall & experimentation continuity        |
| **Agents**        | Orchestrator API with task submission and status tracking   | Composable automation workflows                 |
| **Kernel**        | Event-driven service coordination with backpressure control | Predictable resource management                 |
| **Chat**          | SSE v2 streaming with resume capability                     | Flawless conversational experience              |
| **Security**      | Script/plugin signing, capability gates, network allowlist  | Trust & audit trail for automation              |
| **Coding system** | .aether workflow language with static verification          | Intent-driven development surface               |

**Why Aetherra**: Explicit feature gating via environment flags (secure by default),
Prometheus-first metrics for every subsystem, and human-readable workflow artifacts
for auditable evolution.

---

## Architecture & Repository Map

`
Aetherra/
├── aetherra_core/           # Core engine, kernel, and orchestration
│   ├── aetherra_os.py      # Main OS launcher
│   ├── aetherra_kernel_loop.py
│   └── aetherra_agent_fabric.py
├── lyrixa/                 # AI assistant and chat interfaces
│   ├── lyrixa_basic.py     # Core chat implementation
│   └── ui/                 # GUI components
└── plugins/                # Extensible plugin system
    ├── memory_plugins/
    └── agent_plugins/
`

**Public Hub Endpoints** (default port 3001):
- /api/ai/ask - Direct chat interface
- /api/ai/stream - SSE streaming chat
- /api/lyrixa/chat - Lyrixa bridge
- /api/agents/submit - Task orchestrator
- /api/plugins/* - Plugin management
- /metrics - Prometheus metrics

---

## Quickstart

### 1. Headless Smoke Test

Verify kernel and services start properly:

```bash
python tools/os_smoke.py
```

### 2. Start the Hub

Launch local APIs and services:

```bash
python aetherra_hub_server.py
# Hub starts on http://localhost:3001
```

### 3. Test Chat Endpoints

**Direct Ask**:

```bash
curl -X POST http://localhost:3001/api/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, what can you help me with?"}'
```

**SSE Streaming**:

```bash
curl -N http://localhost:3001/api/ai/stream \
  -H "Accept: text/event-stream" \
  -d "query=Tell me about Aetherra"
```

**Lyrixa Bridge**:

```bash
curl -X POST http://localhost:3001/api/lyrixa/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "System status check", "context": {}}'
```

### 4. Verify Setup

Check system health:

```bash
curl http://localhost:3001/metrics
curl http://localhost:3001/api/health
```

---

## Agents Quick Demo

Submit tasks to the orchestrator and track their progress:

### Submit a Task

```bash
curl -X POST http://localhost:3001/api/agents/submit \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "analysis",
    "description": "Analyze system performance metrics",
    "priority": "normal",
    "context": {}
  }'
```

**Task Shape**:

- `task_type`: analysis, automation, monitoring, custom
- `description`: Human-readable task description
- `priority`: low, normal, high, urgent
- `context`: Additional parameters and data

### Check Task Status

```bash
# Get task by ID
curl http://localhost:3001/api/agents/status/{task_id}

# List all tasks
curl http://localhost:3001/api/agents/tasks
```

**Task States**: `pending` → `running` → `completed` | `failed` | `cancelled`

---

## Plugins

Manage plugins dynamically through Hub endpoints with automatic UI updates:

### Plugin Management

```bash
# List installed plugins
curl http://localhost:3001/api/plugins/list

# Install plugin
curl -X POST http://localhost:3001/api/plugins/install \
  -H "Content-Type: application/json" \
  -d '{"name": "plugin_name", "source": "local|registry"}'

# Uninstall plugin
curl -X DELETE http://localhost:3001/api/plugins/uninstall/plugin_name

# Plugin status and metadata
curl http://localhost:3001/api/plugins/status/plugin_name
```

### Plugin UI Integration

Lyrixa's GUI automatically refreshes when plugins change:

- **Sidebar panels**: Auto-generated when plugin declares UI surface
- **Install/uninstall**: Available directly from the GUI
- **Non-intrusive**: Plugin operations don't block chat functionality
- **Real-time updates**: Plugin status changes reflect immediately

See `/api/plugins/*` endpoints for complete plugin management API.

---

## Lyrixa GUI Stability

"Stable" GUI means flawless user experience across all core interactions:

### Chat Experience
- **SSE v2 resume**: Last-Event-ID support for reliable stream resumption
- **Consistent payloads**: Final responses include evidence[] and scratchpad_policy
- **No interruptions**: Plugin operations never block chat functionality

### Plugin Integration
- **UI auto-generation**: Panels automatically appear when plugins declare UI surfaces
- **Live install/uninstall**: Direct from GUI without service restarts
- **Sidebar management**: Plugin panels dynamically reconfigure layout
- **State preservation**: Chat context maintained during plugin changes

### Technical Guarantees
- Streaming connections handle network interruptions gracefully
- Plugin manifest validation before UI integration
- Resource isolation prevents plugin failures from affecting chat
- Responsive design adapts to plugin panel additions/removals

The GUI meets "stable" criteria when these behaviors work consistently
under normal operation and edge cases (network drops, plugin failures).

---

## Configuration (Environment Flags)

High-value environment variables for system behavior:

### Core APIs & Tokens

```bash
# Enable AI APIs with authentication
export AETHERRA_AI_API_ENABLED=1
export AETHERRA_AI_API_TOKEN=your_secure_token
export AETHERRA_AI_API_REQUIRE_TOKEN=1

# Enable streaming chat
export AETHERRA_AI_API_STREAM=1
```

### Safety & Network

```bash
# Enable safety mode (strict validation)
export AETHERRA_SAFETY_MODE=1

# Network allowlist for security
export AETHERRA_NETWORK_ALLOWLIST="localhost,127.0.0.1,.aetherra.dev"
export AETHERRA_NET_STRICT=1
```

### Performance & Limits

```bash
# Kernel queue and backpressure control
export AETHERRA_KERNEL_QUEUE_SIZE=1000
export AETHERRA_KERNEL_BACKPRESSURE_LIMIT=5000

# Plugin timeouts and concurrency
export AETHERRA_PLUGIN_TIMEOUT=30
export AETHERRA_PLUGIN_MAX_CONCURRENT=10
```

See [Environment Variables Index](docs/ENVIRONMENT_VARIABLES.md) for complete list.

---

## Security & Privacy

### Script & Plugin Signing
- **Manifest verification**: All plugins require signed manifests
- **Code integrity**: .aether scripts validated with cryptographic signatures
- **Trust chains**: Configurable signing authorities and key management

### Capability Gates
- **Permission model**: Plugins request specific capabilities (network, file, memory)
- **Runtime enforcement**: Capability violations terminate plugin execution
- **Audit logging**: All capability requests and denials logged

### Network Security
- **Allowlist enforcement**: Configurable network destination restrictions
- **Protocol filtering**: HTTP/HTTPS only in strict mode
- **Proxy support**: Corporate network compatibility

### Privacy & Telemetry
- **Opt-in telemetry**: No data collection without explicit consent
- **Differential privacy**: Statistical noise added to usage metrics
- **Local-first**: Core functionality works without network connectivity

### Strict Mode Toggles

```bash
# Lock down all security features
export AETHERRA_PROFILE=prod
export AETHERRA_NET_STRICT=1
export AETHERRA_SCRIPT_VERIFY_STRICT=1
export AETHERRA_PLUGIN_SIGNING_REQUIRED=1
```

---

## .aether Script Basics

Intent-driven workflow language with static verification:

### Basic Structure

```aether
goal: "Analyze system performance and generate report"

workflow:
  - step: "collect_metrics"
    plugin: "system_monitor"
    params:
      duration: "5m"

  - step: "analyze_data"
    plugin: "data_analyzer"
    depends_on: ["collect_metrics"]

parallel:
  - task: "cpu_analysis"
    plugin: "cpu_profiler"
  - task: "memory_analysis"
    plugin: "memory_profiler"

policy:
  timeout: "10m"
  retry_count: 3
  failure_action: "notify"

require:
  capabilities: ["system_read", "file_write"]
  plugins: ["system_monitor>=1.0", "data_analyzer"]
```

### Static Verification

Verify .aether scripts in CI/CD:

```bash
# Basic verification
python tools/verify_aether_scripts.py --root .

# Strict mode (production)
python tools/verify_aether_scripts.py --root . --strict
export AETHERRA_SCRIPT_VERIFY_STRICT=1
```

Verification checks:

- Syntax validity and schema compliance
- Plugin dependency resolution
- Capability requirement validation
- Signature verification (in strict mode)

---

## Observability

### Health & Status Monitoring

```bash
# Kernel status and metrics
curl http://localhost:3001/api/kernel/status
curl http://localhost:3001/api/kernel/metrics

# Memory system health
curl http://localhost:3001/api/memory/status
curl http://localhost:3001/api/memory/stats

# Overall system health
curl http://localhost:3001/api/health
```

### Prometheus Metrics

Access metrics at `http://localhost:3001/metrics`:

- **aetherra_kernel_tasks_total**: Total tasks processed
- **aetherra_memory_operations_total**: Memory read/write operations
- **aetherra_plugin_executions_total**: Plugin execution counts
- **aetherra_api_requests_total**: HTTP API request metrics
- **aetherra_errors_total**: Error counts by subsystem

### Security Alerts Feed

```bash
# Security events and alerts
curl http://localhost:3001/api/security/alerts
curl http://localhost:3001/api/security/events/recent
```

Alerts include capability violations, signature failures, and network policy breaches.

---

## Quality Gates & Tests

### Smoke Tests

```bash
# Basic system boot verification
python tools/os_smoke.py

# Headless mode (CI/CD)
AETHERRA_QUIET=1 python tools/os_smoke.py
```

### Spec→Tests Gate

```bash
# Verify specification compliance
python tools/spec_tests_gate.py

# Check that tests cover documented features
python tools/verify_docs_consistency.py
```

### Coverage Protection

```bash
# Run tests with coverage no-drop validation
python tools/quality_gates.py

# Coverage must not decrease from baseline
pytest --cov=aetherra_core --cov-fail-under=85
```

### Static Verification

```bash
# .aether script validation
python tools/verify_aether_scripts.py --strict

# Code quality and security
python tools/quality_gates.py --all
```

### Capability Tests

Located in `tests/capabilities/`:

- **test_ownership_memory.py**: Memory ownership and isolation
- **test_lyrixa_ownership_answer.py**: Chat ownership validation
- **test_hub_metrics_observability.py**: Metrics and monitoring
- **test_lyrixa_chat_bridge_schema.py**: API schema compliance

```bash
# Run all capability tests
pytest tests/capabilities/

# Run specific capability validation
pytest tests/capabilities/test_ownership_memory.py
```

---

## v0.3.0 Release Highlights

### 🎯 Stability Achieved
- **QFAC**: Fixed timing-based test; system passes stability checks
- **Type system**: Full PEP 585 modernization (Dict→dict, Optional→| None)
- **Security**: All scanners clean; strict defaults validated
- **Tests**: 98 passed, 1 skipped; 13.80% coverage (up from 8.36%)

### 🔒 Security Hardening
- Script/plugin signing with manifest verification
- Capability gates enforced at runtime
- Network allowlist with strict mode toggles
- Audit logging for all security events

### 🚀 Performance & Reliability
- SSE v2 with Last-Event-ID resume capability
- Event-driven kernel with backpressure control
- Plugin UI auto-generation without chat blocking
- Prometheus metrics for all subsystems

### 📈 Quality Gates
- No-regression coverage gate (13.80% baseline)
- Spec→Tests gate enabled in CI
- Static verification for .aether scripts
- Enhanced test reliability across all subsystems

---

## Roadmap & Status

### ✅ Implemented (Stable)

- **Chat/Kernel**: SSE v2 streaming, event-driven coordination
- **Agents**: Task orchestrator with status tracking
- **Memory**: Persistent + quantum-augmented layers
- **Security**: Script signing, capability gates, network allowlist
- **Observability**: Prometheus metrics, health endpoints

### 🚧 Partial Implementation

- **Plugin Ecosystem**: Core system ready, expanding plugin library
- **GUI Stability**: Chat stable, plugin UI refinements ongoing
- **Documentation**: API docs complete, user guides expanding

### 🔮 Planned Features

- **AI Trainer System**: Adaptive model fine-tuning
- **Advanced Memory**: Semantic search and graph relationships
- **Enterprise Features**: SSO integration, advanced RBAC
- **Multi-tenant**: Isolated workspaces and resource quotas

### Development Status

**🚀 v0.3.0 Released as Stable** (Current)

Major achievements:
- 98 passed, 1 skipped tests (99% pass rate)
- All security scans clean
- QFAC & core systems operational
- PEP 585 modernization complete
- Coverage improved from 8.36% → 13.80%

**Next Focus: Coverage Growth & Enhancement**

- **v0.3.1 (≤ 30 days):** Coverage to 25%, plugin ecosystem expansion
- **v0.3.2 (≤ 60 days):** Coverage to 40%, GUI stability improvements
- **v0.3.3 (≤ 90 days):** Coverage to 60%, advanced memory features

Track progress at [GitHub Issues](https://github.com/AetherraLabs/Aetherra/issues)
and [Project Board](https://github.com/AetherraLabs/Aetherra/projects).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards,
and contribution guidelines.

## License

This project is licensed under the GNU General Public License v3.0 or later.
See [LICENSE](LICENSE) for details.
