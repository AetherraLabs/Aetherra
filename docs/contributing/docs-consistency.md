# Docs consistency gate

A CI job verifies documentation stays consistent with code:

- Environment variables referenced in code must be listed in `docs/PROJECT_OVERVIEW.md`.
- Public HTTP endpoints must be listed in `docs/PROJECT_OVERVIEW.md`.

Run locally before pushing:

```bash
python tools/verify_docs_consistency.py
```

The script outputs a markdown report at `docs/DOCS_CONSISTENCY_REPORT.md` and exits non-zero on missing items.
