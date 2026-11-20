# Main CI follow-up

The post-#318 main run passed three restart acceptance cases and 1,795 tests
(10 skipped), then stopped at production signing. Separate jobs exposed legacy
style debt, duplicated YAML workflow definitions, and an invalid dependency name.

## Python quality

Fast Quality and Release run the same command on PRs and main:

```powershell
python -m pip install -r requirements/quality.txt
python tools/python_quality.py
```

The checked-in `.ci/python-quality-baseline.json` records existing violations
from main commit `25753cfcebc12a51a5a0873fc955340bf3b9fa0c`. Its only source
correction before capture was the obsolete manual-test function reference in
`test_lyrixa_primary_chat.py`; critical Ruff findings cannot be baselined.

An allowance applies only to the same path, normalized source SHA-256 and set of
checks. Editing a legacy file requires making that file clean. New files have no
allowance. Changes to formatter configuration or installed tool versions fail
closed. LF and CRLF are equivalent. Normal checks do not rewrite the baseline;
resolved debt is reported and can be removed in a reviewed cleanup.

The baseline was explicitly chosen to keep this CI repair focused. It does not
claim the whole repository is style-clean. Updating it is a maintainer action:

```powershell
python tools/python_quality.py --write-baseline .ci/python-quality-baseline.json
git diff -- .ci/python-quality-baseline.json
```

Do not regenerate it merely to make a failing PR pass. Review every added
allowance. The pinned Black, Ruff and isort versions match pre-commit. Both use the root
formatter configuration explicitly; nested configuration cannot hide violations.
The source inventory includes tracked Python files even if a new gitignore rule
would hide them, and excludes untracked generated test artifacts.

## Workflow and dependency repairs

`ci.yml` now has one workflow header and one jobs mapping. Both original sets of
jobs are retained; workflow YAML validation rejects duplicate keys. Restored smoke
jobs explicitly clear whole-repository coverage options, install their async
test dependency, and retain the existing WebSocket `<16` compatibility bound. The debugger
dependency uses the published package name `pdbpp`, as documented by
[its maintainers](https://github.com/pdbpp/pdbpp#installation).

## Required operator action: release signing

The repository secret list and failed main run show no configured repository
secret named `AETHERRA_RELEASE_PRIVKEY`. An administrator must add the approved
Ed25519 signing seed as **64 hexadecimal characters**, not a filename or PEM:

1. Open repository **Settings → Secrets and variables → Actions**.
2. Add `AETHERRA_RELEASE_PRIVKEY`, or grant this repository access to an existing
   organization Actions secret of that name. Keep the existing trusted signing
   identity; do not generate a replacement merely to pass CI.
3. Rerun **CI Quality Gates** for the current main commit. Both production bundle
   signing and signed-manifest policy must succeed.

The secret is never printed by preflight. Missing secrets remain hard failures;
there is no unsigned mode or test-key substitution in production.

Release starts after successful CI Quality Gates and verifies the exact main
commit, push event, and successful signing/policy steps through the GitHub API.
Manual dispatch uses the same preflight. If main advances, release stops and
waits for the newer commit's signed build. PR CI cannot authorize a release.

Production publication remains unverified until the operator supplies the
signing secret. Tests use synthetic metadata only and never publish a release.

The pinned semantic-release CLI now has explicit root package/build configuration.
It derives the next version from Git history; a preflight rejects downgrades. The
build updates both README version markers, and README is included in the release
commit, preserving the existing version-badge gate. This is tested with disposable
metadata and a no-operation release run; no tag or release was published.

## Verification notes

Regression checks cover unchanged legacy debt, edited/new files, config/tool drift,
critical syntax errors, hidden source files, ignored generated files, nested config
bypasses, exact-commit signing prerequisites, and README version synchronization.
Workflow syntax is checked with actionlint and duplicate-key-aware YAML validation.

Local full collection still encounters the pre-existing
`tests/integration/test_phase2_bridge.py` import of `lyrixa.gui.main_window` when
PySide6 is installed. No unrelated GUI work is included; Linux CI is reported
separately.
