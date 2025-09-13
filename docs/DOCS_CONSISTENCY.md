# Docs Consistency Verification

This tool (`tools/verify_docs_consistency.py`) enforces alignment between source code and documentation for:

1. Environment variables actually fetched in code vs documented in `PROJECT_OVERVIEW.md`.
2. HTTP endpoints (Hub / QFAC / optional dashboards) exposed in code vs documented.
3. Consciousness metrics (identity, narrative, workspace, latency histograms) present in `METRICS_REFERENCE.md`.

## Why It Exists

- Prevents configuration drift (new env vars silently added without docs).
- Ensures API surfaces remain discoverable and test parity is upheld.
- Guards observability additions (consciousness metrics) from undocumented regressions.

## Invocation

Basic run (quiet exit code focus):

```bash
python tools/verify_docs_consistency.py
```

Verbose diagnostics:

```bash
python tools/verify_docs_consistency.py --debug
# or
AETHERRA_DOCS_DEBUG=1 python tools/verify_docs_consistency.py
```

## Exit Codes

| Exit Code | Meaning                                                                                     |
| --------- | ------------------------------------------------------------------------------------------- |
| 0         | All required env vars, endpoints, and consciousness metrics documented.                     |
| 1         | One or more: missing env var docs, missing endpoint docs, or missing consciousness metrics. |

## Debug JSON Artifact (when --debug or AETHERRA_DOCS_DEBUG=1)

Writes `docs/DOCS_CONSISTENCY_DEBUG.json` containing:

```jsonc
{
  "timestamp": 172,             // float UNIX epoch
  "code_envs_count": 219,       // number of env vars fetched in code
  "doc_envs_count": 238,        // number of env tokens found in docs
  "missing_envs": ["AETHERRA_X"],
  "raw_extra_envs": ["AETHERRA_STYLE_ENABLED", "..."] ,
  "suppressed_doc_only_envs": ["AETHERRA_STYLE_ENABLED"],
  "extra_envs_reported": [],    // extra after suppression
  "code_routes_count": 59,
  "doc_routes_count": 59,
  "missing_routes": [],
  "extra_routes": [],
  "missing_consciousness_metrics": [],
  "report_path": "docs/DOCS_CONSISTENCY_REPORT.md",
  "config_ignore_count": 19
}
```

## Configuration (`docs/docs_consistency.json`)

Optional keys:

- `ignore_extra_envs` (or legacy `doc_only_envs`): list of env vars allowed **only** in docs (suppressed from "extra" warnings).

## Pattern Matching Notes

- Code env detection only counts *fetches* (`os.environ[...]`, `os.environ.get`, `os.getenv`) to avoid false positives.
- Documentation scan uses a broad token regex plus markdown table parsing.
- Endpoints include `/api`, `/ws`, `/quantum`, `/qfac`, `/memory`, `/health`, `/status`, and `/metrics` families. Case-normalized and parameter segments collapsed to `<param>`.
- Consciousness histograms validated by base metric presence (`_bucket` variant enforced if base name missing).

## Adding a New Environment Variable

1. Implement code referencing it via an accepted fetch pattern.
2. Add a row (preferred) or bullet to `PROJECT_OVERVIEW.md` with the backticked name and description.
3. Re-run the script; ensure it drops from the missing list.
4. If intentionally doc-only (rare), add to `docs_consistency.json` under `ignore_extra_envs`.

## Common Failure Scenarios

| Symptom                      | Likely Cause                                                                   | Fix                                                                              |
| ---------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| Env var reported missing     | Not documented, typo (case or underscore), or documented outside overview file | Add / correct entry in `PROJECT_OVERVIEW.md`.                                    |
| Env var reported extra       | Documented but never fetched in code                                           | Remove or implement code usage; or add to ignore list if intentionally doc-only. |
| Endpoint missing             | New Flask route added not mentioned in docs                                    | Add to endpoints section or canonical list.                                      |
| Consciousness metric missing | Metric renamed/removed or not added to `METRICS_REFERENCE.md`                  | Update metrics doc with full name.                                               |

## Minimal Contribution Checklist

- [ ] Added env var row or endpoint bullet
- [ ] Ran verification script (expect exit 0)
- [ ] Added tests (if new pattern extraction logic introduced)
- [ ] Updated `docs_consistency.json` only when truly doc-only

## Maintenance

Keep extraction regex modifications conservative; include unit tests under `tests/tools/` for new patterns. Favor additive logic over brittle one-off special cases.

