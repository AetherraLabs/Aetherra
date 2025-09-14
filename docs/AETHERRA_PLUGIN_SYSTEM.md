# Aetherra Plugin System

Updated: 2025-09-06

This document describes the Aetherra Plugin System: the facilities that allow the Aetherra OS and Lyrixa to discover, load, execute, evaluate, and evolve pluggable cognitive, memory, workflow and tooling modules. It follows the common system‑document structure used across the repository.

## Purpose and scope

- Provide a unified, safe, and extensible mechanism to add new capabilities to the Aetherra OS without forking core code
- Standardize plugin packaging (manifest + code + optional assets) and lifecycle (create → install → register → activate → execute → retire)
- Enable adaptive / self‑improvement loops (quality control, analytics, lifecycle memory) to observe and refine plugins over time
- Support categories spanning cognition, memory, workflow automation, analysis, training, and introspection
- Integrate with Service Registry, Hub API surface, Lyrixa chat layer, Engine, Memory, and Agent Orchestrator where appropriate

## At‑a‑glance status

| Area                               | Status                | Notes                                                                   |
| ---------------------------------- | --------------------- | ----------------------------------------------------------------------- |
| Local discovery & catalog          | ✅ Implemented         | `aetherra_plugin_discovery.py`, updated JSON catalog                    |
| Plugin manager / lifecycle helpers | ✅ Implemented         | Consolidated manager & cleaner utilities                                |
| Dynamic loading / execution hooks  | ✅ Implemented (local) | Safe fallback paths when execution unsupported                          |
| Creation / scaffolding tools       | ✅ Implemented         | GUI wizard + programmatic generation tools                              |
| Quality control & analytics        | ✅ Implemented         | Metrics & lifecycle memory plugins with dashboards                      |
| Plugin categories (core set)       | ✅ Implemented         | 14 plugins across 9 organized categories                                |
| GUI Integration                    | ✅ Implemented         | 6 plugins with PySide6 interfaces, plugin UI host system                |
| Hub integration (remote registry)  | 🔄 Planned             | Roadmap Phase 2+ (central registry & distribution)                      |
| Security hardening / sandboxing    | 🔄 Partial             | Basic validation & signing hooks; deeper isolation planned              |
| Versioning & dependency resolution | 🔄 Planned             | Manifest fields reserved; resolver not active yet                       |
| Remote fetch / install             | 🔄 Planned             | To be enabled once registry API online                                  |
| Prometheus / structured metrics    | 🔄 Partial             | Some counters via existing subsystems; dedicated plugin metrics planned |

## 1) Core components

Primary files & artifacts (current codebase):

- `aetherra_plugin_discovery.py` — Scans plugin directories, builds catalog
- `aetherra_plugin_viewer.py` — Introspection / human‑readable listing utilities
- `aetherra_plugins_cleaner.py` — Removes stale / invalid plugin entries
- `aetherra_plugin_catalog.json` — Generated catalog / registry snapshot (local)
- `tools/agents_probe.py --create-tool` (Toolsmith path) — Can scaffold plugin‑adjacent tools
- `Aetherra/plugins/` — Source tree of core & experimental plugins
- Plugin lifecycle / analytics helpers (e.g. `plugin_quality_control`, `plugin_analytics`, `plugin_lifecycle_memory`)
Recent full OS sessions reported discovery of these plugins:

```text
advanced-memory-system (aetherplug)
hello_plugin (aetherplug)
ai_plugin_generator_v2 (python)
plugin_manager (python)
plugin_creation_wizard (python)
plugin_discovery (python)
plugin_generator_plugin (python)
plugin_quality_control (python)
assistant_trainer_plugin (python)
context_aware_surfacing (python)
introspector_plugin (python)
workflow_builder_plugin (python)
plugin_analytics (python)
plugin_lifecycle_memory (python)
```

**Plugin Status Summary (v0.3.0):**
- **Total**: 14 plugins (2 .aetherplug, 12 Python)
- **With GUIs**: 6 plugins have PySide6-based interfaces
- **Categories**: 9 distinct categories for proper organization
- **Quality**: Duplicates resolved, proper categorization implemented

## 2) Manifest & schema

Each plugin folder is expected to contain a manifest file (canonical name evolving — latest internal draft: `Aetherra-plugin.json`). Representative fields:

```jsonc
{
  "name": "workflow_builder_plugin",
  "version": "0.1.0",
  "description": "Assists with constructing multi-step workflows",
  "category": "workflow",
  "entry_point": "plugin.py:Plugin",
  "capabilities": ["plan", "compose_workflow"],
  "permissions": { "memory": true, "filesystem": "read", "network": false },
  "requires": ["core>=0.9.0"],
  "authors": ["Aetherra Labs"],
  "license": "GPL-3.0-or-later",
  "signatures": { "sha256": "..." },
  "telemetry": { "opt_in": true }
}
```

Planned / reserved keys:
- `dependencies` (other plugins) & version constraints
- `sandbox` configuration for isolation modes
- `metrics` export descriptors
- `hooks`: lifecycle callbacks (activate, deactivate, upgrade)

## 3) Plugin lifecycle

1. Discover: File system scan enumerates candidate folders / manifests
2. Validate: Basic schema & integrity checks (naming, fields, hash/signature if present)
3. Catalog: Entry written into `aetherra_plugin_catalog.json` with status & metadata
4. Register: Optionally added to Service Registry (if provides runtime service endpoint)
5. Activate: Initialization code runs (capability exposure, handlers, adapters)
6. Execute: Core entry points invoked by Lyrixa, Engine, Agents, or workflows
7. Monitor: Quality control plugin observes performance, success/error ratios
8. Persist: Lifecycle memory plugin stores usage summaries, learned heuristics
9. Update / Retrain: AI plugin generator / trainer produce improved variant (optional)
10. Retire: Deprecated plugin flagged, catalog entry archived or cleaned

## 4) Execution model

A plugin’s entry class typically exposes a lightweight contract (subject to category):

- `initialize(context) -> Awaitable[bool]` (optional)
- `capabilities() -> list[str]`
- `invoke(action: str, payload: dict, context) -> Awaitable[dict|str]`
- Optional specialized methods (e.g., `analyze(memory)`, `plan(workflow_spec)`, etc.)

Dispatch patterns:

- Direct invocation via Lyrixa when chat suggestions require plugin capability
- Workflow engine / Aether scripts referencing plugin steps by name
- Agent Orchestrator selecting a plugin as a tool in task execution

Graceful fallback: If a plugin fails to initialize, the system logs a WARN and excludes it (no global crash).

## 5) Developer workflow (local)

| Step                 | Action                                                                              |
| -------------------- | ----------------------------------------------------------------------------------- |
| Scaffold             | Copy an existing plugin folder or use a creation wizard/tool (planned improvements) |
| Author               | Implement entry class & update manifest fields                                      |
| Validate             | Run discovery script or diagnostics; ensure it appears in catalog                   |
| Activate             | Launch full OS; confirm plugin listed in discovery log (e.g., 13 plugins found)     |
| Test                 | Use Lyrixa chat / workflows / agents to exercise capabilities                       |
| Iterate              | Refine, add telemetry hooks, update version                                         |
| Prepare for Registry | Ensure licensing, signatures, and semantic versioning correct                       |

Planned CLI (registry era):
```
aetherra plugins create <name>
aetherra plugins validate <path>
aetherra plugins pack <path>
aetherra plugins publish --token <t>
aetherra plugins search <query>
aetherra plugins install <name>
```

## 6) Categories & currently available plugins

**Updated Plugin Categories (v0.3.0):**

### **Memory & Persistence**
- **`advanced-memory-system`** (.aetherplug) - Enhanced episodic and semantic memory with vector search
- **`plugin-lifecycle-memory`** (python) - Plugin lifecycle memory persistence and learning

### **System Infrastructure**
- **`plugin_manager`** (python) - Core plugin lifecycle management and orchestration
- **`plugin_discovery`** (python) - Plugin discovery and catalog management system

### **Development Tools**
- **`plugin_creation_wizard`** (python) - GUI wizard for interactive plugin creation ✅ Has PySide6 UI
- **`plugin_generator_plugin`** (python) - Programmatic plugin code generation and templating
- **`ai_plugin_generator_v2`** (python) - Advanced AI-powered plugin generation

### **Monitoring & Analytics**
- **`plugin_quality_control`** (python) - Plugin quality assurance and validation
- **`plugin_analytics`** (python) - Plugin performance metrics and analytics ✅ Has PySide6 Dashboard UI

### **AI & Intelligence**
- **`assistant_trainer_plugin`** (python) - AI assistant training and improvement ✅ Has PySide6 UI
- **`context_aware_surfacing`** (python) - Intelligent plugin recommendations ✅ Has PySide6 UI

### **Analysis & Introspection**
- **`introspector_plugin`** (python) - Autonomous code analysis and self-insight ✅ Has PySide6 UI

### **Workflow & Automation**
- **`workflow_builder_plugin`** (python) - Visual workflow design and automation ✅ Has PySide6 UI

### **Examples & Learning**
- **`hello_plugin`** (.aetherplug) - Simple demonstration plugin for tutorials

**GUI Integration Status:**
- **6 plugins** have full PySide6-based graphical interfaces
- **Plugin UI Host** system manages GUI integration and lifecycle
- **Auto-generated panels** when plugins declare UI surfaces

## 7) Security & policy

Current safeguards:
- Manifest presence & basic schema validation
- License field required (GPL-3.0-or-later enforced for official set)
- (Planned) Signature verification & trust tiers
- Memory / file / network access flags (honored defensively; enforcement to tighten)

Planned enhancements:
- Sandboxed execution contexts (sub‑interpreter or process boundary)
- Capability-based permission gating integrated with Kernel security system
  - Per-capability limits supported via `~/.aetherra/policy/capabilities.json` under `limits`:

    ```json
    {
      "allow": { "core:webhook_manager": ["network:webhook"] },
      "limits": {
        "network:outbound": { "timeout_sec": 10, "max_concurrency": 1 },
        "network:webhook": { "timeout_sec": 8 }
      }
    }
    ```
  - Env override for concurrency by capability: `AETHERRA_PLUGIN_CAP_CONCURRENCY_MAP` (JSON)
- Quarantine flow for suspicious or repeatedly failing plugins
- Provenance attestation embedded in catalog entries

## 8) Observability & telemetry

Implemented basics:
- Discovery logs: count + names per startup
- Quality control plugin: can record success/failure summaries (persisted via memory system)
- Lifecycle memory plugin: stores usage frequency & contextual insights

Planned:
- Structured Prometheus metrics (per plugin load time, invoke latency, failure rate)
- Plugin trace IDs linking chat → plugin invocation → memory writes
- Auto regression detection comparing new vs prior version performance

## 9) Configuration & environment

Existing / emerging flags (subject to evolution):
- `AETHERRA_PLUGIN_DISABLE=<name1,name2>` — Skip specified plugins (planned)
- `AETHERRA_PLUGIN_SAFE_MODE=1` — Load only verified / core set (planned)
- `AETHERRA_PLUGIN_DISCOVERY_VERBOSE=1` — Extra discovery diagnostics
- `AETHERRA_PROFILE=test` — Deterministic behavior for test runs

Catalog / storage locations:
- Source: `Aetherra/plugins/<plugin_name>/`
- Local catalog: `aetherra_plugin_catalog.json`
- (Future) Package cache: `~/.aetherra/plugins/` or workspace overlay

## 10) Extension & integration points

- Lyrixa Chat: Suggests or calls plugin capabilities for context retrieval, workflow assistance, or optimization hints
- Aether Scripts: Steps reference plugin actions (future script operator integration)
- Service Registry: Selected long‑running plugin services may register (e.g., continuous analyzers)
- Agent Orchestrator: Plugins provide tools/skills for agents to invoke
- Memory System: Plugins can read/write categorized memories (respecting future permission filters)
- Self‑Improvement Engine: Generates improved variants (plugin generator + trainer synergy)

## 11) Roadmap alignment (June → now)

Roadmap Phase mapping:
- Phase 1 (Foundation) — Local discovery, manager, example plugins ✅
- Phase 2 (Registry Platform) — Central API, search, publishing (in progress / not yet in repo)
- Phase 3 (Core Library Expansion) — Several seed categories present; continued enrichment planned
- Phase 4 (Community & Ecosystem) — Governance scaffolding and submission workflow pending public registry

Additions since June vision:
- Analytics & lifecycle memory plugins integrated with memory subsystem
- Generator / trainer toolchain prototypes present locally
- Workflow builder & introspection utilities surfaced earlier than initially targeted

## 12) Known limitations

- No authenticated remote registry yet (local only)
- Limited isolation; plugins share process context (sandbox forthcoming)
- Version conflict / dependency resolution unimplemented
- Error handling coarse; partial failures rely on log inspection
- Manifest schema not yet validated against a published JSON Schema spec

## 13) Quick examples

Listing discovered plugins (from recent startup log):

```text
[PLUGINS] Scanning for installed plugins...
[PLUGINS] Found 13 installed plugins:
  - advanced-memory-system
  - ai_plugin_generator_v2
  - enhanced_plugin_manager
  - plugin_creation_wizard
  - plugin_discovery
  - plugin_generator_plugin
  - plugin_quality_control
  - assistant_trainer_plugin
  - context_aware_surfacing
  - introspector_plugin
  - workflow_builder_plugin
  - plugin_analytics
  - plugin_lifecycle_memory
```

(Planned) Programmatic invocation (illustrative):

```python
from aetherra_plugin_discovery import get_local_catalog
from aetherra_plugin_loader import load_plugin  # future utility

catalog = get_local_catalog()
plugin_meta = catalog.get("workflow_builder_plugin")
plugin = await load_plugin(plugin_meta)
resp = await plugin.invoke("compose", {"goal": "refactor memory subsystem"}, context)
```

## 14) References

- Roadmap (June): `docs/roadmap/AETHERRA_PLUGIN_ROADMAP.md`
- Lyrixa System: `docs/AETHERRA_LYRIXA_SYSTEM.md`
- Memory System: `docs/AETHERRA_MEMORY_SYSTEM.md`
- Agent System: `docs/AETHERRA_AGENT_SYSTEM.md`
- Kernel System: `docs/AETHERRA_KERNEL_SYSTEM.md`

---

**Status (v0.3.0 Stable):** ✅ Core local system implemented · ✅ 14 production plugins active · ✅ GUI integration complete · 🛠 Registry & sandboxing in progress · 🔭 Advanced telemetry forthcoming

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
