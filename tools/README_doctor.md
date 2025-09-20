# Project Doctor

A one-command local fixer/checker to keep the repo healthy without breaking
code.

## Scripts

- `tools/project-doctor.ps1` (Windows)
- `tools/project-doctor.sh` (Unix/macOS/Linux)

## Modes

- `--check`: run Ruff (no-fix), MyPy, optional Pyright, PyTest quick, Gitleaks;
  does not modify files.
- `--fix` (default): Ruff format + fix, then types/tests/secrets. Safer when
  you’ve got a clean working copy and quick tests are green.
- `--guarded-fix`: requires a clean git working tree. Runs Ruff
  formatting/fixes, then tests. If tests fail, reverts all changes via
  `git reset --hard`. Afterwards runs types/secrets. Use for safe bulk
  formatting.
- `--security-deep`: additionally runs Bandit (static security) and pip-audit
  (dependency vuln scan) if available, writing JSON reports into `tools/`.

## VS Code tasks

- "Doctor": default behavior (fix). Shows problems in the Problems panel (Ruff
  and MyPy patterns and Python matcher).
- "Doctor (Check only)": safe read-only mode.
- "Doctor (Guarded fix)": safe auto-fix with test gate and auto-revert on
  failure.

Open: Terminal → Run Task → pick a Doctor task.

## Installation (once)

- Python tooling (inside your venv):
  - `pip install -U pip ruff mypy pytest gitleaks-bin`
  - Optional: `pip install bandit pip-audit`
- Optional type feedback: Install VS Code Pyright extension (or `npm i -g
  pyright`).
- Optional frontend: in `frontend/`, install ESLint, Prettier, TypeScript, and
  wire `npm run lint/format/typecheck`.

## Tips

- Prefer `Doctor (Guarded fix)` for bulk formatting across many files; it
  auto-reverts if tests fail.
- `--check` is CI-friendly and safe to run any time.
- Secret scan reports: `tools/gitleaks_report.json`; deep scans:
  `tools/bandit_report.json`, `tools/pip_audit_report.json`.
- MyPy scope currently set to `Aetherra` for signal-to-noise. Expand as the
  codebase stabilizes.
