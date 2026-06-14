# UI Migration Map

Status: Draft v1
Purpose: Exact disposition map for UI-related surfaces during Aetherra unification.

## Decision Legend

- **KEEP**: remains active in primary architecture
- **TRANSITIONAL KEEP**: retained temporarily for compatibility
- **ARCHIVE**: move out of active runtime path first
- **REMOVE**: delete after archive + verification
- **INTERNALIZE**: keep code but remove user-facing branding/entrypoints

## 1) Canonical Runtime Entry

| Path                      | Decision | Notes                                          |
| ------------------------- | -------- | ---------------------------------------------- |
| `aetherra_os.py`          | KEEP     | Primary launcher contract                      |
| `aetherra_os_launcher.py` | KEEP     | Core orchestration and boot flow               |
| `frontend/`               | KEEP     | Canonical user-facing UI stack                 |
| `aetherra_hub/`           | KEEP     | Backend services supporting canonical frontend |

## 2) Aetherra GUI Directory

| Path                                        | Decision          | Wave   | Notes                                                             |
| ------------------------------------------- | ----------------- | ------ | ----------------------------------------------------------------- |
| `Aetherra/gui/aetherra_os_gui.py`           | TRANSITIONAL KEEP | Wave 1 | Keep until canonical frontend fully replaces native GUI workflows |
| `Aetherra/gui/launch_enhanced_neural_os.py` | TRANSITIONAL KEEP | Wave 1 | Compatibility wrapper                                             |
| `Aetherra/gui/run_aetherra_os.py`           | TRANSITIONAL KEEP | Wave 1 | Compatibility wrapper                                             |
| `Aetherra/gui/README.md`                    | KEEP              | Wave 1 | Update wording to Aetherra-only identity                          |
| `Aetherra/gui/__init__.py`                  | KEEP              | Wave 1 | Package stability                                                 |
| `Aetherra/gui/boot_menu.py`                 | ARCHIVE -> REMOVE | Wave 2 | Covered by canonical startup flow                                 |
| `Aetherra/gui/boot_monitor.py`              | ARCHIVE -> REMOVE | Wave 2 | Fold behavior into boot interaction contract                      |
| `Aetherra/gui/chat_hardened.py`             | ARCHIVE -> REMOVE | Wave 2 | Duplicate chat surface                                            |
| `Aetherra/gui/event_bus.py`                 | INTERNALIZE       | Wave 2 | Keep only if imported by core runtime                             |
| `Aetherra/gui/lyrixa_gui.py`                | ARCHIVE -> REMOVE | Wave 2 | Retire Lyrixa public UI surface                                   |
| `Aetherra/gui/performance_monitor.py`       | ARCHIVE -> REMOVE | Wave 2 | Move metrics into canonical dashboard                             |
| `Aetherra/gui/plugin_installer.py`          | ARCHIVE -> REMOVE | Wave 2 | Replace with plugin manager in canonical UX                       |
| `Aetherra/gui/plugin_lifecycle.py`          | ARCHIVE -> REMOVE | Wave 2 | Replace with lifecycle panel in canonical UX                      |
| `Aetherra/gui/plugin_ui_host.py`            | ARCHIVE -> REMOVE | Wave 2 | Superseded by canonical frontend plugin host                      |
| `Aetherra/gui/zone_manager.py`              | ARCHIVE -> REMOVE | Wave 2 | Lyrixa-era construct; retire from user path                       |

## 3) Root-Level UI Scripts

| Path                   | Decision | Wave   | Notes                                      |
| ---------------------- | -------- | ------ | ------------------------------------------ |
| `adk_demo_ui.py`       | ARCHIVE  | Wave 1 | Demo-only; keep out of active root runtime |
| `chat_stream_ui.py`    | ARCHIVE  | Wave 1 | Duplicate chat experiment                  |
| `agent_pipeline_ui.py` | ARCHIVE  | Wave 1 | Developer demo                             |
| `kernel_status_ui.py`  | ARCHIVE  | Wave 1 | Replace with canonical status panel        |

## 4) Lyrixa UI Surface

| Path                                  | Decision                     | Wave   | Notes                                                                        |
| ------------------------------------- | ---------------------------- | ------ | ---------------------------------------------------------------------------- |
| `Aetherra/lyrixa/gui/`                | INTERNALIZE then CONSOLIDATE | Wave 1 | Migrate useful components into canonical `frontend/`; remove as separate app |
| `Aetherra/lyrixa/gui/main_window.py`  | TRANSITIONAL KEEP            | Wave 1 | Minimal compatibility shim for tests/launchers during UI migration           |
| `Aetherra/lyrixa/lyrixa_basic_gui.py` | ARCHIVE -> REMOVE            | Wave 2 | Legacy GUI                                                                   |
| `Aetherra/lyrixa/plugins/*_ui.py`     | ARCHIVE -> REMOVE            | Wave 2 | Convert to plugin manifests + canonical UI views                             |
| `Aetherra/lyrixa/ui/`                 | REMOVE (scripted)            | Wave 2 | Legacy folder already targeted by prune tooling                              |

## 5) Dashboards and Web Fragments

| Path                           | Decision          | Wave   | Notes                                                  |
| ------------------------------ | ----------------- | ------ | ------------------------------------------------------ |
| `quantum_dashboard/`           | ARCHIVE -> REMOVE | Wave 2 | Merge functionality into canonical frontend dashboards |
| `templates/` (dashboard pages) | ARCHIVE -> REMOVE | Wave 2 | Keep only templates still used by live backend routes  |

## 6) Do-Not-Touch Safety Boundaries

Never include in bulk removal operations:

- `dist-packages/**`
- `**/node_modules/**` (unless specifically cleaning within a controlled frontend workspace)
- `.git/**`, `.github/**`
- Dependency manifests and lockfiles

## 7) Dry-Run Findings (Captured)

Dry-run results from:

- `tools/prune_aetherra_gui.py`
- `tools/prune_lyrixa_gui.py`

Key observations:

1. `Aetherra/gui/GUI_CURATION_PLAN.md` is now preserved by prune keep-rules.
2. `Aetherra/lyrixa/gui/node_modules` is no longer targeted by default, which keeps transition risk low.
3. The current Lyrixa GUI dry-run candidate set is limited to `.env`, `__init__.py`, `build`, `dist`, and `Aetherra/lyrixa/ui`.

## 8) Recommended Wave Execution

## Wave 1 (non-destructive)

1. Archive root demo UI files.
2. Internalize Lyrixa naming in launch/help docs.
3. Build canonical startup UX flow from boot contract.

## Wave 2 (controlled removal)

1. Review current prune candidate lists and approve per-batch apply.
2. Re-run dry-run and approve candidate list.
3. Run prune scripts with `--apply` in reviewed batches.

## Wave 3 (hardening)

1. Remove stale imports/tests referencing removed UI paths.
2. Add CI checks preventing new duplicate UI entrypoints.
