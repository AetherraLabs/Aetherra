# GUI Audit Report (2025-10-06)

This report summarizes the state of the Aetherra graphical interfaces (OS Monitor + Lyrixa GUIs) and whether they are wired into required subsystems:
Hub services, Event Bus, Plugin framework, Metrics / Performance, Service Registry, Policy / Security, and Testing.

---

## 1. Scope & Sources Reviewed

Reviewed files (primary):

- `Aetherra/gui/aetherra_os_gui.py` (OS Monitor GUI)
- `Aetherra/gui/run_aetherra_os.py` (Launcher wrapper)
- `Aetherra/gui/lyrixa_gui.py` (Advanced zone-based Lyrixa GUI)
- `Aetherra/gui/plugin_ui_host.py` (Sandboxed plugin WebView host)
- `Aetherra/gui/zone_manager.py` (Layout & zone diff manager)
- `Aetherra/gui/event_bus.py` (Unified Event Bus)
- `Aetherra/lyrixa/lyrixa_basic_gui.py` (Basic Lyrixa GUI)
- Representative plugin UI: `Aetherra/lyrixa/plugins/workflow_builder_ui.py`
- Tests: smoke & GUI related under `tests/` (executed: smoke set passed)

Automation executed: `Verify UI Standards` (0 findings) and smoke tests (3 passed).

---

## 2. Component Summaries

### 2.1 Aetherra OS Monitor (`aetherra_os_gui.py`)

Purpose: Lightweight polling dashboard for Hub + optional Web UI. Shows log tail and basic metrics (uptime, requests, plugin count).

Integration: Standalone polling via `requests`; no Event Bus usage.

Failover: Console `--once` mode if PySide6 unavailable.

Security: No auth / token support; no TLS consideration.

### 2.2 Lyrixa Advanced GUI (`lyrixa_gui.py`)

Purpose: Zone-based main window with dynamic plugin and layout management.

Integrations:

- Uses `ZoneManager` for layout modes.
- Uses `PluginUIManager` (expects manifest-driven sandboxed plugins).
- Emits events via `EventFactory` to global Event Bus.
- Emits a basic performance metric (widget_count) every 5s.

Gap: No direct service registry or memory subsystem hooks; plugin discovery refresh is a placeholder.

### 2.3 Plugin UI Host (`plugin_ui_host.py`)

Sandboxed per-plugin `QWebEngineView` with security toggles.
Expects a `manifest.json` per plugin (`ui_entry`, permissions, budgets).
No manifests were found in repository search.
Provides state and error signals.

### 2.4 Zone Manager (`zone_manager.py`)

Maintains diff-based layout model (zones, splitter ratios, tab indices).
Uses placeholder widget creation; not yet bound to semantic component factories.

### 2.5 Event Bus (`event_bus.py`)

Unified event system bridging Qt and async.
Provides factory for layout, plugin, performance, and chat events.
Not used by OS Monitor or Basic GUI.

### 2.6 Lyrixa Basic GUI (`lyrixa_basic_gui.py`)

Simpler assistant + hub view.
Separate architecture (does not reuse zone manager or plugin sandbox).
Accepts optional `service_registry` parameter but does not wire to Event Bus or
standardized plugin manifests.

---

## 3. Integration Matrix (Summary)

| Subsystem | OS Monitor | Advanced GUI | Basic GUI         | Plugin Host     |
| --------- | ---------- | ------------ | ----------------- | --------------- |
| Hub API   | Yes (poll) | No (yet)     | Partial           | N/A             |
| Event Bus | No         | Yes          | No                | Signals only    |
| Discovery | No         | Placeholder  | Basic list        | Needs manifests |
| Metrics   | No         | Widget count | No                | No              |
| Logging   | Prints     | logging      | logging           | logging         |
| Sandbox   | N/A        | Via host     | N/A               | Yes             |
| Auth      | No         | No           | No                | No              |
| Env cfg   | HUB/WEB    | None         | Plugin cards flag | None            |
| Registry  | No         | No           | Param only        | No              |
| Tests     | Smoke      | Partial      | Present           | None            |
| i18n/A11y | Not set    | Not set      | Not set           | Not set         |

---

## 4. Key Gaps & Risks

1. No `manifest.json` files → sandbox path unvalidated.
2. OS Monitor isolated from Event Bus → siloed telemetry.
3. Divergent GUI architectures without migration path.
4. No auth / token handling for Hub endpoints.
5. Plugin refresh stub only; no discovery or signature checks.
6. Limited performance metrics (widget count only).
7. Permission list unused: no policy enforcement.
8. Missing tests for layout events, plugin timeout / error, monitor snapshot schema.
9. Placeholder zone widget creation risks future inconsistency.
10. No backoff for failed HTTP polls (potential tight loop if interval tuned down).

---

## 5. Recommended Remediation (Prioritized)

### Priority 1 – Foundational Wiring

- Implement plugin manifest discovery: scan `Aetherra/lyrixa/plugins/*/manifest.json` at startup and on refresh.
- Add one real manifest for an existing plugin (e.g., workflow builder) to validate path.
- Integrate OS Monitor with Event Bus (emit health + performance events).
- Support `AETHERRA_HUB_TOKEN` for optional auth header.

### Priority 2 – Consistency & UX

- Unified launcher: prefer Advanced GUI when WebEngine + manifests present; fallback to Basic.
- Add status panel to Advanced GUI (reuse Basic sidebar component) fed by events.
- Enforce permissions at load (warn + disable if unauthorized).

### Priority 3 – Observability & Quality

- Add metrics: plugin load duration, failed load count, event queue depth.
- Optional JSON structured logging via env `AETHERRA_GUI_JSON_LOG`.
- Introduce minimal i18n helper (`tr()` placeholder).

### Priority 4 – Security & Hardening

- Inject / enforce CSP for plugin HTML; block remote scripts when sandboxed.
- Manifest signature / hash validation (tie into existing integrity manifest if available).
- Add exponential backoff for failed hub/web polling.

---

## 6. Proposed Test Additions

| Test File                                   | Purpose                                             |
| ------------------------------------------- | --------------------------------------------------- |
| `tests/gui/test_plugin_manifest_loading.py` | Discovery builds expected plugin list & host states |
| `tests/gui/test_plugin_timeout_error.py`    | Force tiny timeout to assert TIMEOUT state          |
| `tests/gui/test_event_bus_layout_mode.py`   | Verify `layout_mode_changed` event emission         |
| `tests/gui/test_os_monitor_snapshot.py`     | Validate snapshot key / type schema                 |
| `tests/gui/test_permissions_enforcement.py` | Unauthorized permission triggers warning            |

---

## 7. Minimal Manifest Example

```jsonc
{
  "id": "workflow_builder",
  "name": "Workflow Builder",
  "version": "1.0.0",
  "ui_entry": "index.html",
  "permissions": ["storage:read", "workflow:edit"],
  "size_budget_kb": 2048,
  "timeout_ms": 15000,
  "sandbox": true,
  "zones": [
    {
      "id": "workflow_builder.main",
      "zone_type": "right_plugin",
      "title": "Workflow Builder",
      "components": []
    }
  ]
}
```

---

## 8. Implementation Sketch (First Pass)

1. Create manifest file under plugin directory.
2. Add discovery in `PluginUIManager` (scan + load + emit events).
3. Wire `LyrixaGUI._refresh_plugins` to call discovery.
4. Emit health + perf events from OS Monitor on each refresh.
5. Add auth header in `_fetch_json` when `AETHERRA_HUB_TOKEN` present.
6. Add the new tests (Qt offscreen if needed).

---

## 9. Suggested Incremental PR Breakdown

- PR1: Manifest + discovery + basic test.
- PR2: OS Monitor ↔ Event Bus integration + metrics tests.
- PR3: Permission enforcement + security docs.
- PR4: Unified launcher strategy + fallback.
- PR5: Observability expansion (metrics + logging).

---

## 10. Open Questions

- Source of truth for plugin permissions policy? (Policy file? Registry?)
- Deprecate Basic GUI or maintain as low-resource mode?
- Existing metrics aggregator expecting specific event names?
- Timeline for Hub auth requirement in non-local contexts?

---

## 11. Summary

Advanced Lyrixa GUI architecture (zones, sandboxing, event bus) is solid but lacks
real plugin manifests and discovery.
OS Monitor works for quick health but is siloed.
Implementing manifests, discovery, unified events, and minimal security additions
will harmonize GUIs under a consistent extensibility and observability model.

---

*Generated automatically as part of repository GUI audit.*
