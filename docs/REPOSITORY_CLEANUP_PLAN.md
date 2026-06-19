# Aetherra Repository Cleanup Plan

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Status: Active cleanup plan

This document tracks repository hygiene work for the GitHub-facing Aetherra
repository. The goal is to make the repository understandable, safer to clone,
and easier to contribute to without removing useful project history blindly.

## Cleanup Principles

- Do not delete tracked files until their purpose is understood.
- Prefer moving historical reports into `docs/archive/` over deleting them.
- Keep generated runtime state out of future commits.
- Keep root-level files limited to project entry points, governance, packaging,
  and high-value orientation documents.
- Keep system completion status in `docs/AETHERRA_*_SYSTEM.md`.
- Treat databases, logs, packaged builds, generated reports, and local caches as
  artifacts unless explicitly needed by tests or packaging.

## Current Root-Level Problems

The repository currently contains several categories of clutter:

- packaged distribution output under `dist-packages/`
- generated local databases such as `*.db`
- generated coverage, security, lint, and scan reports
- old duplicate files such as `.gitignore.old`, `.gitignore.new`, and `README_OLD.md`
- many root-level standalone scripts and historical milestone reports
- runtime files such as logs, metrics snapshots, and local URL files
- package/build output directories that should not be reviewed as source

Some of these files are already tracked, so adding ignore rules only prevents
new files from being added. Removing tracked artifacts should be done in a
separate reviewed cleanup commit.

## Phase 1 - Non-Destructive GitHub Presentation

Status: Complete

- [x] Replace root README with a current Alpha/Foundation overview.
- [x] Document active system completion status.
- [x] Add this cleanup plan.
- [x] Tighten ignore rules for future generated artifacts.
- [ ] Add or update a concise docs index if needed.

## Phase 2 - Candidate Artifact Removal

Status: In progress

Candidates to remove from Git history going forward:

- `dist-packages/` - removed from source control in the first artifact cleanup pass
- `build/`
- `htmlcov/`
- `.coverage`
- `coverage.xml`
- `ruff_report*.json`
- `ruff_report*.txt` - obvious tracked root reports removed in the first artifact cleanup pass
- `security_scan.json` - removed in the first artifact cleanup pass
- `licenses_report.json`
- `gate_results.json` - removed in the first artifact cleanup pass
- `demo_dashboard_report.json`
- `pre_pack_validation*_report.json`
- `phase*_validation_report_*.json`
- `homeostasis_metrics_*.json`
- `rollback_test.json`
- `integrity_manifest.json`
- root-level `*.db`, `*.db-shm`, and `*.db-wal`
- root-level `*.log`
- root-level generated backup snapshots such as `*_backup.json`
- populated local env files such as `.env.autonomy.staging`
- generated `data/artifacts/*.sarif`, coverage, and scan reports - removed in the first artifact cleanup pass
- generated workflow failure summaries and parse baselines under `data/artifacts/`

Before removal, confirm whether any workflow still depends on the file being
present in the repository.

First pass notes:

- Removed the checked-in packaged Windows distribution output under
  `dist-packages/`.
- Removed old duplicate root files: `.gitignore.new`, `.gitignore.old`, and
  `README_OLD.md`.
- Removed generated SARIF, coverage, quality gate, lint, and scan reports that
  should be produced by CI rather than committed as source.
- Removed obvious local runtime outputs such as `hub_runtime_url.txt` and
  tracked database sidecar artifacts.
- Left source workflows, root scripts, and ambiguous data files for later
  targeted triage.

Second pass notes:

- Removed timestamped Homeostasis metrics exports and rollback test output.
- Removed stale generated release integrity output from the repository root.
- Removed old generated backup snapshots, including an empty cleanup marker and
  a plugin catalog backup with local absolute paths.
- Kept `sbom.json`, license trend history, docs consistency config, and stub
  inventories because they are referenced by active workflows, tools, or docs.

Third pass notes:

- Removed `.env.autonomy.staging` from Git tracking while leaving the ignored
  local file available for the operator environment.
- Removed generated workflow-failure summaries, parse baselines, duplicated
  verification/sign-off artifacts, and the doctor last-run output.
- Removed a placeholder generated downloads page under `docs/downloads/`.
- Kept active `.aether` workflows even though broad ignore rules match them;
  they are operational source files and require a separate policy decision.

## Phase 3 - Historical Documentation Reorganization

Status: Pending explicit review

Candidates to move into `docs/archive/` or `docs/reports/`:

- `*_COMPLETE.md`
- `*_SUMMARY.md`
- `*_REPORT.md`
- `PHASE_*`
- `PACKAGING_*`
- `PRE_PACK_*`
- `STORM_*`
- `README_OLD.md`
- older root-level roadmap and analysis documents that are no longer source of truth

System documents under `docs/AETHERRA_*_SYSTEM.md` should remain first-class.

## Phase 4 - Root Script Triage

Status: In progress

Many executable Python files live at the repository root. They should be
classified into one of these outcomes:

- keep as public entry point
- move to `tools/`
- move to `scripts/`
- move to `demos/`
- archive as historical
- delete if superseded and unused

Likely root files to keep:

- `aether.py`
- `aetherra_os.py`
- `aetherra_os_launcher.py`
- `aetherra_self_incorporation.py`
- `main.py`
- `setup.py`
- `pyproject.toml`

Everything else should be triaged before moving.

Initial classification is recorded in
`docs/ROOT_SCRIPT_WORKFLOW_TRIAGE.md`. The safest first move is a focused
standalone-test migration, because many root tests are outside normal pytest
discovery but some harnesses still call exact root filenames.

Root test cleanup notes:

- Root standalone validation scripts were moved under
  `tests/legacy/root_standalone/`.
- Root manual Homeostasis probes were moved under `tests/homeostasis/manual/`.
- Root STORM probes were moved under `tests/storm/manual/`.
- Root API/manual GUI probes were moved under `tests/api/manual/` or `demos/`.
- `test_unicode_workflow_fix.py` remains at root because active workflow and
  helper scripts call that exact path.

Root utility cleanup notes:

- Maintenance utilities were moved under `tools/maintenance/`.
- GitHub administration helpers were moved under `tools/github/`.
- Operator diagnostics and stack helpers were moved under `tools/ops/`.
- The superseded root `generate_stub_inventory.py` duplicate was removed; the
  maintained implementation remains at `tools/maintenance/generate_stub_inventory.py`.
- Root demo/manual UI launchers were moved under `demos/`.

## Phase 5 - GitHub Hygiene

Status: Pending

- Confirm README badges reflect real current checks and release maturity.
- Confirm GitHub Actions do not depend on tracked generated artifacts.
- Confirm Dependabot/code-scanning alerts are not caused by checked-in build output.
- Remove packaged dependencies from source control where possible.
- Ensure `.gitignore` matches the cleanup policy.
- Consider Git LFS or release assets for large binary distribution outputs.

## Acceptance Criteria

Repository cleanup is complete when:

- the root README accurately describes current Aetherra status
- root-level files are limited and intentional
- generated runtime artifacts are ignored and untracked
- packaged builds are not committed as source
- historical docs are discoverable but not mixed with current source of truth
- GitHub security/dependency alerts no longer come from generated distribution copies
- CI still passes after artifact removal and path updates
