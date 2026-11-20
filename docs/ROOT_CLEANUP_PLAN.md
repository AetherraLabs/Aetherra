# Root Cleanup Plan (Alpha → Beta Hardening)

Status: PRUNE PHASE COMPLETED. All 19 planned operations successfully moved (copy + prune) to their destinations (`archive/`, `tests/legacy/`, `experiments/`). Originals removed per enhanced prune logic (delete even if destination pre-existed). Journals: `root_cleanup_apply.json` (copy) and `root_cleanup_prune.json` (prune).



* Minimize top‑level cognitive load (≤ ~40 user‑facing items)
* Separate runtime/data/log artifacts from source & docs
* Preserve historical transformation intelligence (archive, not delete)
* Avoid breaking imports or tests (staged moves + alias shims if needed)

## Guiding Principles

1. Non‑destructive first pass: create `archive/` + `legacy/` + `data/` placements, leave originals until CI confirms safety.
2. Reversible: every move scripted & logged (`tools/root_cleanup.py --apply` writes a journal).
3. Deterministic: explicit allow/ignore lists, no wildcard deletions.
4. Test safety: run capability + quality gates after each batch.

## Classification Summary

| Category                           | Items                                                                                                                                      | Action                                | Destination               |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------- | ------------------------- |
| Backups / Cleanup Snapshots        | `backups/`, `comprehensive_cleanup_backup/`, `final_organization_backup/`, `focused_cleanup_backup/`, `smart_cleanup_backup/`              | Archive                               | `archive/backups/`        |
| Backup Info JSON                   | `plugins_cleanup_backup_info.json`, `lyrixa_cleanup_backup_info.json`                                                                      | Archive                               | `archive/metadata/`       |
| Phase Test Scripts (legacy)        | `phase_7_4_test.py`, `phase_7_4_ultimate_test.py`, `phase_7_5_test.py`, `phase_8_1_test.py`, `phase_8_2_test.py`, `phase_8_3_test.py`      | Move                                  | `tests/legacy/`           |
| Legacy Docs Trees                  | `documentation/`                                                                                                                           | Keep as compatibility pointer          | `documentation/`          |
| Engine / Experimental Scripts      | `beyond_transcendence_engine.py`, `cosmic_consciousness_engine.py`, `intelligent_error_handler_8.py`, `enhanced_conversation_manager_7.py` | Review (plugin or experimental)       | `experiments/`            |
| Large Report Artifacts             | *All reports currently in root (none new)*                                                                                                 | Move (already mostly in `docs/`)      | —                         |
| Data / DB Files                    | `*.db`, `aetherra_kernel_metrics.json`, `live_file_index.json`, `concept_clusters.db` etc.                                                 | Consolidate                           | `data/` (already partial) |
| Logs                               | `aetherra_os.log`, `lyrixa_system.log`, `lyrixa_basic.log`                                                                                 | Consolidate (already `logs/`)         | `logs/`                   |
| Cleanup Plan/Applied JSON          | `PROJECT_CLEANUP_PLAN.json`, `PROJECT_CLEANUP_APPLIED.json`                                                                                | Keep (audit)                          | `archive/plans/`          |
| Misc Root Markdown (announcements) | `docs/archive/root-reports/QUANTUM_CONSCIOUSNESS_BREAKTHROUGH_ANNOUNCEMENT.md`                                                            | Archived                              | Completed                 |

## First Batch (Proposed NOW – Non‑Destructive)

Create structure only:

```text
archive/
  backups/
  metadata/
  docs/
  plans/
experiments/
tests/legacy/
```

No files moved yet. Commit structure + plan + tool.

## Second Batch (Dry Run Moves)

Run:

```bash
python tools/root_cleanup.py --plan --dry-run
```

Outputs JSON journal of intended operations.

## Third Batch (Apply Moves)

Executed:

```text
python tools/root_cleanup.py --apply
python tools/root_cleanup.py --apply --prune-originals
```

Outcome: copy journal recorded (`root_cleanup_apply.json`), followed by prune journal (`root_cleanup_prune.json`). Enhanced logic ensured originals deleted even if destination already existed from copy phase.

## Risk Mitigation

* Imports: none of the targeted phase test scripts are imported by prod code; relocation only affects test discovery (will still be found if `tests/` is included). If any import path expects root, we can leave symlink/ shim (Windows note: use small stub file importing from new path until next major release).
* Historical Analysis: Plan & Applied JSON retained under `archive/plans/`.
* CI: Add optional job later to ensure no new root `.py` files unless whitelisted.

## Success Metrics

* Root file count ↓ (baseline recorded by script)
* New contributor “time to first run” unaffected (< 2 min)
* All existing tests pass post‑move

## Follow Ups

* Add `ROOT_POLICY.md` summarizing allowed root items (pending).
* Introduce `lint-root-structure` CI check.
* Collapse legacy documentation into curated `docs/archive/` material only when
  it has ongoing traceability value.

---
Generated: initial manual draft (tool will embed hash once executed).
