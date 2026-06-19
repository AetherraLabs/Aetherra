# Root Script and Workflow Triage

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Status: Root test and utility migration complete

This document records the cautious root script and `.aether` workflow triage.
It is intentionally conservative: files are classified before any move/delete
operation so operational launchers, signed workflows, and validation harnesses
are not broken by cleanup.

## Triage Principles

- Keep public launchers and package entry points at the repository root until a
  compatibility shim strategy exists.
- Keep signed `.aether` workflows in their current operational paths.
- Move root tests only after updating harnesses, workflows, and documentation
  that call exact filenames.
- Prefer `tools/`, `scripts/`, `tests/`, `demos/`, or `docs/reports/` over
  root-level sprawl.
- Delete only generated artifacts or obsolete files with no active references.

## Immediate Fixes Applied

- `.gitignore` now explicitly preserves tracked operational `.aether` workflows.
- `.gitignore` now explicitly preserves the tracked root `.vscode/tasks.json`.
- `.gitignore` now explicitly preserves tracked Aetherra cleanup utilities.
- `git ls-files -ci --exclude-standard` should remain empty after this pass.
- Phase 5 harness-owned and remaining non-workflow standalone tests now live
  under `tests/legacy/root_standalone/`.
- Root manual probes were moved into focused `tests/*/manual/` folders or
  `demos/`. Only `test_unicode_workflow_fix.py` remains at the root because
  active workflows call that exact path.
- Root maintenance, GitHub administration, and operator helper scripts were
  moved into `tools/maintenance/`, `tools/github/`, and `tools/ops/`.

## Keep At Root

These files are public entry points, packaging files, or widely referenced
compatibility launchers.

| File | Reason |
| --- | --- |
| `aether.py` | Primary Aether script runtime / CLI surface; widely referenced. |
| `aetherra_os.py` | Main OS launcher entry point. |
| `aetherra_os_launcher.py` | Compatibility launcher with many references. |
| `aetherra_self_incorporation.py` | Active system entry point used by current Self-Improvement / Guardian work. |
| `main.py` | Convenience launcher alias. |
| `setup.py` | Packaging compatibility. |
| `pyproject.toml` | Project metadata and test/tool configuration. |

## Keep In Place For Now

These root scripts are active modules/services or have enough references that a
move should be done as a dedicated refactor with import shims.

| Group | Files |
| --- | --- |
| Kernel and services | `aetherra_kernel_loop.py`, `aetherra_service_registry.py`, `aetherra_shared_service_registry.py`, `aetherra_script_service.py`, `aetherra_hmr_controller.py` |
| Plugin/runtime support | `aetherra_plugin_discovery.py`, `aetherra_plugin_viewer.py`, `aetherra_persistent_memory.py`, `aetherra_file_watcher.py`, `aetherra_registry_daemon.py` |
| System modules | `aetherra_agent_fabric.py`, `aetherra_agent_daemon.py`, `aetherra_event_bus.py`, `aetherra_module_manager.py`, `aetherra_meta_memory.py` |
| Compatibility shims | `beyond_transcendence_engine.py`, `quantum_memory_bridge.py`, `launch_aetherra_unicode.py` |

## Move Candidates

These should be moved in focused follow-up commits, not all at once.

| Destination | Candidates | Notes |
| --- | --- | --- |
| `tests/legacy/` or targeted `tests/*/` folders | remaining workflow-pinned root tests | `test_unicode_workflow_fix.py` still has exact workflow references and should move only with workflow updates. |
| `tools/maintenance/` | Future maintenance utilities discovered at root | Existing known maintenance utilities have been moved. |
| `tools/github/` | Future GitHub administration helpers discovered at root | Existing known GitHub helpers have been moved. |
| `tools/ops/` | Future operator diagnostics discovered at root | Existing known operator helpers have been moved. |
| `demos/` | `adk_demo_ui.py`, `agent_pipeline_ui.py`, `chat_stream_ui.py`, `kernel_status_ui.py`, `storm_traffic_test.py` | Demo or manual probe scripts. |

## Protect Workflows

The tracked `.aether` files are currently signed and referenced. They should not
be removed or moved until the Aether script verification/signature workflows and
runtime path discovery are updated together.

| Path | Action |
| --- | --- |
| `Aetherra/aetherra_core/system/*.aether` | Keep in place. |
| `Aetherra/plugins/examples/advanced-memory-system/memory_plugin.aether` | Keep in place. |
| `Aetherra/scripts/self_organizer.aether` | Keep in place. |
| `Aetherra/tools/curiosity_conflict_resolution.aether` | Keep in place. |

## Next Safe Step

Continue root script cleanup:

1. Keep `test_unicode_workflow_fix.py` at root until
   `.github/workflows/auto-fix-workflow-failures.yml` and
   `quick_fix_workflows.py` are updated together.
2. Review root demo/UI scripts and move clear manual launchers into `demos/`.
3. Review historical root reports and move still-useful records into
   `docs/archive/` or `docs/reports/`.
4. Review root runtime databases/logs and remove tracked generated artifacts
   after confirming no workflow depends on them.
5. Run targeted smoke checks after each group.

This keeps the cleanup reversible and avoids mixing test-layout migration with
runtime module relocation.
