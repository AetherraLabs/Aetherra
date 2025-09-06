<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
# Coverage Policy (Alpha)

## Objectives

- Prevent silent coverage regressions (no-drop gate)
- Allow incremental improvement without blocking on an arbitrary global minimum initially

## Mechanism

Implemented in `tools/quality_gates.py`:

1. Run tests with `pytest --cov` capturing total coverage
2. Compare to last stored baseline file (default `.coverage-baseline`)
3. Fail if current < previous (no-drop)
4. Optional absolute threshold via env `MIN_COVERAGE` (percent)
5. Update baseline to new value when gates pass

## Recommended Settings

CI (alpha):

```powershell
$env:MIN_COVERAGE = '60'  # soft floor (adjust as project matures)
python tools/quality_gates.py
```

Local dev: omit `MIN_COVERAGE` to rely on no-drop only.

## Rationale

Early stage code evolves rapidly; enforcing a high static threshold can discourage refactors. The no-drop model ensures quality never drifts downward while leaving space to ratchet `MIN_COVERAGE` upward deliberately.

## Increasing the Baseline

1. Raise `MIN_COVERAGE` in CI config when organic coverage surpasses new target for several merges.
2. Announce in CHANGELOG (Internal / Governance).
3. Monitor for transient flakes causing false negatives.

## Edge Cases

- First run (no baseline): baseline file created; only absolute threshold applies.
- Large test deletions: coverage may rise artificially—still acceptable; focus on real test quality reviews.

## Future Enhancements

- Per-critical-module required coverage tiers
- Branch / condition coverage measurement
- Differential coverage on PRs (changed lines hit %) integration
