# UI Rebuild and Cleanup Plan

Status: Draft v1 (execution plan)
Goal: Rebuild Aetherra UX around one canonical interaction surface while reducing UI sprawl.

## 1) Outcome We Want

- One user-facing identity: **Aetherra**.
- One canonical frontend stack for primary interaction.
- No uncontrolled UI duplicates across root, `Aetherra/gui`, and Lyrixa legacy trees.
- Safe cleanup: no accidental deletion of bundled/runtime/vendor artifacts.

## 2) Current State Summary

Observed UI surface fragmentation includes:

- Root-level Python UIs (`*_ui.py`) used as demos/legacy entrypoints.
- PySide6 desktop UI under `Aetherra/gui`.
- Lyrixa-branded GUI and plugin UIs under `Aetherra/lyrixa/*`.
- Multiple dashboard implementations (React/static/Python).
- Existing cleanup scripts already present:
  - `tools/prune_aetherra_gui.py`
  - `tools/prune_lyrixa_gui.py`

## 3) Canonical Direction

### Keep as Product Surface

- `aetherra_os.py` (launcher contract)
- `aetherra_os_launcher.py` (orchestration/boot flow)
- `frontend/` (canonical web UX)
- `aetherra_hub/` backend routes/services that support frontend runtime

### Keep as Transitional Compatibility (short-term)

- `Aetherra/gui/aetherra_os_gui.py`
- `Aetherra/gui/launch_enhanced_neural_os.py`
- `Aetherra/gui/run_aetherra_os.py`

### Internalize / Deprecate Branding

- User-facing "Lyrixa" naming should be phased out from launch surfaces and docs.
- Any retained Lyrixa modules are internal implementation detail only.

## 4) Classification Matrix

## A) Likely Keep / Consolidate Into Canonical UX

- `frontend/`
- `aetherra_hub/`
- `aetherra_os.py`
- `aetherra_os_launcher.py`
- `Aetherra/gui/aetherra_os_gui.py` (transitional)

## B) Likely Archive (do not hard-delete first pass)

- Root demo UIs:
  - `adk_demo_ui.py`
  - `chat_stream_ui.py`
  - `agent_pipeline_ui.py`
  - `kernel_status_ui.py`
- Legacy Lyrixa UIs:
  - `Aetherra/gui/lyrixa_gui.py`
  - `Aetherra/lyrixa/lyrixa_basic_gui.py`
  - `Aetherra/lyrixa/plugins/*_ui.py`
- Dashboard duplicates:
  - `quantum_dashboard/`
  - `templates/` dashboard pages where equivalent exists in canonical frontend

## C) Scripted Prune Candidates (after archive + verification)

- `Aetherra/gui/*` except curated keep-list (already encoded in `tools/prune_aetherra_gui.py`)
- `Aetherra/lyrixa/gui/*` except curated React/Vite keep-list (already encoded in `tools/prune_lyrixa_gui.py`)
- `Aetherra/lyrixa/ui/` (legacy directory targeted by existing prune script)

## D) Do-Not-Touch Zones (mass deletion forbidden)

- `dist-packages/**`
- `**/node_modules/**`
- `.git/**`, `.github/**`
- Dependency manifests (`requirements*.txt`, `package.json`, lockfiles)

## 5) Phased Execution

## Phase 0 — Freeze and Map (1 sprint)

1. Freeze new UI entrypoint creation unless approved.
2. Produce `UI_MIGRATION_MAP.md` mapping old UI files to replacement or archive target.
3. Mark legacy UIs as deprecated in headers (no behavior changes).
4. Confirm canonical frontend launch path from `aetherra_os.py`.

Exit criteria:

- Every discovered UI entrypoint is mapped to Keep / Archive / Remove.

## Phase 1 — Consolidate UX (1–2 sprints)

1. Move or reimplement required dashboard/plugin views in canonical frontend.
2. Remove Lyrixa branding from user-visible copy and launcher choices.
3. Keep compatibility wrappers temporarily for external scripts.
4. Add tests ensuring canonical startup path works headless and interactive.

Exit criteria:

- All user-critical UI features available through canonical frontend path.

## Phase 2 — Archive and Prune (1 sprint)

1. Archive legacy UI files to a controlled location (or branch/tag) first.
2. Execute dry-run on prune scripts; review output.
3. Execute `--apply` only after sign-off.
4. Remove stale tests pointing to deleted legacy paths.

Exit criteria:

- Legacy duplicate UI trees removed, no broken launch/task/test references.

## 6) Recommended Archive Structure

Use a single archive root to avoid workspace clutter:

- `docs/archived/ui/` for historical docs and migration map
- `archive/ui_legacy/` for code snapshots pending final deletion

If repository policy avoids large archives in mainline, place snapshots in a dedicated branch/tag instead.

## 7) Validation Checklist

Before each removal batch:

1. Run dry-run prune scripts.
2. Run smoke tests and selected GUI/API tests.
3. Verify launcher and canonical frontend boot.
4. Search for references to soon-to-delete paths.

After removal batch:

1. Re-run smoke tests.
2. Re-run UI standards check task/tooling.
3. Confirm docs and contributor guides match new reality.

## 8) Decision Log Needed from Team

1. Canonical frontend location confirmation (`frontend/` vs alternative).
2. Whether any PySide UI remains long-term or only transitional.
3. Archive-in-repo vs archive-in-branch policy.
4. Sunset date for Lyrixa naming in public artifacts.

## 9) Immediate Next Actions

1. Approve canonical UX stack and archive policy.
2. Create `docs/UI_MIGRATION_MAP.md` with exact file-by-file disposition.
3. Run prune scripts in dry-run mode and capture outputs for review.
4. Schedule first removal wave limited to root-level demo UIs.
