# Removal: Legacy Hub Script (`aetherra_hub_server.py`)

## Summary

Removes deprecated monolithic hub shim and related enforcement scaffolding now that a full release cycle has passed and all dependents migrated to `aetherra_hub.compat` / modular app.

## Changes

- Delete `aetherra_hub_server.py`
- Delete `tests/integration/test_hub_compat_parity.py`
- Remove pre-commit hook `block-legacy-hub-import` + script `tools/precommit_block_legacy_hub.py`
- Remove quality gate legacy import enforcement block (or downgrade to informational message)
- Update CHANGELOG (move deprecation note to Removed section with version tag)
- Update `docs/DEPRECATION_TRACKER_LEGACY_HUB.md` (mark COMPLETE and archive)

## Verification Checklist

- [ ] Grep shows no `aetherra_hub_server` references besides changelog historical entries
- [ ] Full test suite passes
- [ ] Quality gates pass with enforcement code removed
- [ ] Coverage unchanged or improved

## Migration Guidance (already completed earlier)

To start Hub:

```bash
python -m aetherra_hub.compat
```

Or programmatically:

```python
from aetherra_hub import compat
server = compat.start_hub_server(port=3001)
```

## Backward Compatibility

No supported surfaces removed besides already-deprecated shim. Import attempts will now raise `ModuleNotFoundError` (documented in release notes).

## Release Notes Snippet

The deprecated legacy monolithic hub (`aetherra_hub_server.py`) has been removed after a full deprecation cycle. Use `python -m aetherra_hub.compat` or the modular `create_app` interface.

## Risk & Mitigation

Risk: Hidden downstream dynamic imports.
Mitigation: Pre-commit + gates ran for full cycle; parity test ensured export surface stable.

## Additional Actions

- [ ] Tag release after merge.
- [ ] Announce in README / release notes.

---
Generated template; adjust version numbers and dates prior to merge.
