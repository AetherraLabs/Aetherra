# Deprecation Tracker: Legacy Hub Script (`aetherra_hub_server.py`)

Status: Active (Phase B enforcement in place)
Target Removal Earliest: First release after stabilization of 0.5.x (see CHANGELOG Unreleased)

## Rationale

The monolithic hub script has been replaced by a modular blueprint-based implementation (`aetherra_hub.compat` and `aetherra_hub.app`). Centralizing startup via the module interface simplifies maintenance, testing, and plugin evolution.

## Completed

- [x] All docs & scripts migrated to `python -m aetherra_hub.compat`
- [x] Shim reduced to re-export + deprecation warning
- [x] Quality gate enforcement (fails on new legacy imports)
- [x] Pre-commit hook (`block-legacy-hub-import`) for faster local feedback
- [x] Compat parity test (`tests/integration/test_hub_compat_parity.py`)
- [x] Metrics histogram stability (always-export buckets)

## Pending

- [ ] One full minor release cycle observation for regressions
- [ ] Optional telemetry warning if shim imported at runtime in production profile
- [ ] Removal PR: delete shim, remove parity test, drop enforcement overrides, update CHANGELOG
- [ ] Update any downstream integration guides (external) referencing shim (if any discovered)

## Removal Plan (Draft)

1. Confirm zero repository references beyond shim + tracker + changelog.
2. Land removal PR (template below) after release branch cut for final version still carrying shim.
3. Major steps in PR:
   - Delete `aetherra_hub_server.py`
   - Delete `tests/integration/test_hub_compat_parity.py`
   - Remove enforcement code branches referencing override envs (retain gating message for historical clarity optional)
   - Remove pre-commit hook entry and script `tools/precommit_block_legacy_hub.py`
   - Purge CHANGELOG deprecation note or mark as "Removed" with version.
4. Tag release; communicate in release notes.

## Environment Overrides

- `LEGACY_HUB_IMPORT_ENFORCE=0` bypasses quality gate enforcement (emergency only)
- `LEGACY_HUB_IMPORT_ALLOW=1` bypasses pre-commit hook (discouraged)

## Risk Mitigation

- Parity test ensures export surface intact until removal.
- Histograms forced to export to keep existing integration tests stable.
- Removal scheduled only after at least one cycle to detect hidden dynamic imports.

## Contacts / Ownership

Primary: Engine / Hub maintainers
Secondary: Tooling & Quality Gates maintainers

---
Generated: Automated tracker initialization.
