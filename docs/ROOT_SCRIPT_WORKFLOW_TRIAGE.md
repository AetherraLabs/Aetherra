# Root Script and Workflow Triage

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Status: Initial classification pass

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
| `tests/legacy/` or targeted `tests/*/` folders | root `test_*.py` files | `pyproject.toml` discovers `tests/` only, but `tools/phase5_validation_harness.py` and at least one GitHub workflow call exact root test filenames. Update those references first. |
| `tools/maintenance/` | `aetherra_core_analyzer.py`, `aetherra_core_cleaner.py`, `aetherra_import_updater.py`, `aetherra_lyrixa_cleaner.py`, `aetherra_plugins_cleaner.py`, `analyze_stubs.py`, `stub_finder.py`, `generate_stub_inventory.py` | Maintenance utilities should not remain root-level long term. |
| `tools/github/` | `create_github_issues.py`, `create_labels.py`, `quick_fix_workflows.py` | GitHub administration helpers. |
| `tools/ops/` | `check_agents.py`, `check_metrics.py`, `force_homeostasis_active.py`, `restart_aetherra.py`, `start_aetherra_stack.py` | Operator actions and diagnostics. |
| `demos/` | `adk_demo_ui.py`, `agent_pipeline_ui.py`, `chat_stream_ui.py`, `kernel_status_ui.py`, `test_agent_api.py`, `storm_traffic_test.py` | Demo or manual probe scripts. |

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

Start with root standalone tests:

1. Create `tests/legacy/root_standalone/`.
2. Move a small batch of root `test_*_standalone.py` files.
3. Update `tools/phase5_validation_harness.py` command paths.
4. Update docs that mention those exact root paths.
5. Run the moved tests directly and the Phase 5 harness slice.

This keeps the cleanup reversible and avoids mixing test-layout migration with
runtime module relocation.
