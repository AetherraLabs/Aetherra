# Aether Script Operator Guide

> Target: CI, Ops, and Release Engineers
>
> Scope: How to run, verify, and enforce profiles for `.aether` scripts with the v1.1 Language System.

---

## Profiles and Strictness

- AETHERRA_PROFILE=test enables deterministic runs (seeded RNG, stable hashes).
- AETHERRA_DETERMINISTIC=1 forces deterministic engine behavior when applicable.
- AETHERRA_SCRIPT_VERIFY_STRICT=1 enforces signature checks for `.aether` in verification.
- AETHERRA_STRICT / AETHERRA_HUB_STRICT control default strictness at runtime/hub; the `policy:` block can request deterministic/mock modes per run.

## Verifying Scripts in CI

- Tool: `tools/verify_aether_scripts.py`
- Strict mode: set `--strict` or `AETHERRA_SCRIPT_VERIFY_STRICT=1`.
- Profiles: `--profile test` or `AETHERRA_PROFILE=test` to apply deterministic toggles.
- Output: Markdown report at `aether_static_report.md` by default.

Example CI steps (PowerShell):

```powershell
# Deterministic, strict verification
$env:AETHERRA_PROFILE = "test"
$env:AETHERRA_SCRIPT_VERIFY_STRICT = "1"
python tools/verify_aether_scripts.py --root . --output aether_static_report.md --strict
if ($LASTEXITCODE -ne 0) { throw "Aether script verification failed" }
```

## Recommended Repository Layout

- `scripts/` and `workflows/` for first-class `.aether` programs.
- `examples/` for demo/reference scripts. A sample is provided: `examples/daily_anomaly_digest.aether`.
- Keep plugin manifests and schemas under each plugin to support `require:` checks and `plugin_contract:`.

## Deterministic/Test Profiles at Language Level

Prefer setting determinism in the script for CI repeatability:

```aether
policy:
  deterministic: true
  mock_io: true
  seed: 1337
```

- Deterministic: runtime enforces seeded randomness and mocks side-effectful I/O.
- mock_io: allows plugins to provide mock implementations suitable for CI.

## Runtime Safety and Transactions

- Use `transaction:` to wrap effectful operations (store/send/modify) for atomicity.
- Pair with `on_error:` to route failures to escalation or narration.

## Concurrency and Observability

- Use `parallel:` with `await` to safely run independent steps and join results.
- Use `trace`, `log`, and `metrics` to expose run telemetry to the hub.

## Fast Local Smoke

For quick checks during development:

```powershell
python tools/verify_aether_scripts.py --root . --risk-threshold 5 --profile test
```

This prints a summary risk score and the top risky files; non-zero exit when score exceeds threshold or signatures fail (in strict mode).

---

For the full language reference, see `docs/Aether_Script_Language_System.md`.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
