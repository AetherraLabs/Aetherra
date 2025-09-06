# License Policy & Enforcement Gates

This repository enforces a continuous-improvement license hygiene policy.

## Objectives

1. Zero UNKNOWN license metadata in the dependency graph (baseline locked at 0).
2. Deterministic & reproducible reporting (compressed multiline license fields, overrides only for gaps).
3. Fast regression detection (trend gating + absolute max == 0).

## Data Sources

- `requirements.lock` provides the enumerated dependency set.
- `tools/license_report.py` extracts license classifiers / metadata.
- `license_overrides.yml` supplies temporary SPDX-style expressions only when upstream metadata is absent or malformed.

## Enforcement Flow (quality_gates.py)

1. Generate license report (with overrides applied).
2. If report has zero UNKNOWN entries and no explicit ceiling is provided, auto-set `LICENSE_UNKNOWN_ABS_MAX=0`.
3. Run `enforce_license_policy.py` which tracks trend history (`licenses_unknown_history.json`).
4. Fail gate if:
	- UNKNOWN count exceeds `LICENSE_UNKNOWN_ABS_MAX` (default 0 after baseline attainment), or
	- UNKNOWN delta upward > `LICENSE_UNKNOWN_TOLERANCE` (default 0) when `LICENSE_UNKNOWN_TREND_FAIL=1` (default enforced).
5. Optional defense-in-depth: re-run report with `--fail-on-unknown` when ABS_MAX=0.

## Key Environment Variables

| Variable                   | Default   | Description                                                |
| -------------------------- | --------- | ---------------------------------------------------------- |
| LICENSE_UNKNOWN_TREND_FAIL | 1         | Enable trend delta enforcement.                            |
| LICENSE_UNKNOWN_TOLERANCE  | 0         | Allowed increase in UNKNOWN count before failure.          |
| LICENSE_UNKNOWN_ABS_MAX    | Auto 0    | Absolute maximum UNKNOWN count (auto-set to 0 once clean). |
| LICENSE_COMPRESS_MULTILINE | 1 (CI)    | Collapse multiline license strings for stable diffs.       |
| LICENSE_FAIL_ON_UNKNOWN    | (derived) | Adds `--fail-on-unknown` to report when explicitly set.    |

## Overrides Lifecycle

1. Add only for packages that would otherwise be UNKNOWN and where the SPDX identifier is well established.
2. Weekly task: run `license_report.py` after temporarily renaming `license_overrides.yml` to surface resolved metadata.
3. Use `tools/prune_license_overrides.py` to comment out stale overrides no longer needed.
4. Remove commented stale entries after verification in a follow-up PR for audit clarity.

## Rationale for Overrides

Some upstream packages omit `License` metadata but provide classifier(s). Where classifiers are missing or ambiguous, a manual override ensures continuous zero-UNKNOWN baseline without blocking releases.

## Auditing & Transparency

Trend and current UNKNOWN counts are emitted with `[LICENSE_ENFORCE]` prefix for log scraping and dashboards.

Example line:

```text
[LICENSE_ENFORCE] unknown_current=0 prev=0 trend_delta=0 history_len=42
```

## Future Enhancements

- Automatic SBOM license reconciliation.
- SPDX validity canonicalization (normalize dual expressions).
- Alerting / Slack notification on first regression event.

---

Maintained as part of governance transparency commitments.
