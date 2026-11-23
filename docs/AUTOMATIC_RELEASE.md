# Automatic beta releases

Main continues the owner-approved **0.5 beta** line. Release runs only after a
successful main push through CI Quality Gates. Its preflight checks the exact
main SHA and successful production signing and policy steps. Manual dispatch
uses the same checks; no signing bypass is provided.

## Disconnected release history

Run [44675577968](https://github.com/AetherraLabs/Aetherra/actions/runs/44675577968)
passed signed-CI preflight, then correctly rejected a proposed downgrade from
`0.5.0-beta.0` to `0.1.0`. The historical release tags, including `v1.0.0`, are
not ancestors of reconstructed main.

`.ci/release-bootstrap.json` pins the approved package version, main baseline
commit and original annotated tag object. Only when no release tag is reachable,
`tools/run_release.py` temporarily maps that baseline tag to the approved commit
inside a standalone checkout. It verifies package metadata and ancestry first,
refuses shallow/shared worktrees or changed tag identity, and restores the original
tag in `finally` using compare-and-swap. No historical remote tag is changed.

The pinned CLI drops `.beta.0` when resolving its history traversal boundary. A
temporary **non-tag** local branch alias resolves that boundary; it is removed
afterward and never pushed. The first new reachable beta tag makes this bootstrap
unnecessary on subsequent releases. The downgrade guard remains active.

Publication always names the calculated tag explicitly; the CLI's default would
otherwise select the unrelated historical `v1.0.0`. Uploads use checked GitHub CLI
commands because the pinned semantic-release publisher can swallow HTTP errors.
Uploaded files are downloaded, compared to the signed build, and cryptographically
verified before success. The dry-run workflow executes the same version plan and
fails on errors.

## Signing and verification

The release build synchronizes README metadata, builds distributions, signs their
manifest with `AETHERRA_RELEASE_PRIVKEY`, and verifies artifact hashes and the
signature against `keys/release_signing_ed25519.pub` **before** the release CLI
pushes its new commit/tag. Missing or incorrect keys fail publication. The secret
is scoped to the release step and never supplied as a command-line argument.
The GitHub release includes the distributions, manifest and detached signature.

## Release dependencies

Install the package with `requirements/release.txt`, not the general `dev`
extra. Safety 3.8.1 requires `filelock<4`, which forced Release onto vulnerable
3.32.7 despite the runtime locks using patched 4.2.1. Release does not invoke
Safety. The dedicated input retains the formatter baseline, test tools, pinned
semantic-release CLI, build/signing tools and pip-audit, with filelock 4.2.1.

Both Release and the PR Packaging Check install this input, run `pip check`,
and audit an exact inventory of every installed third-party distribution.
Only Aetherra itself, the source being built rather than a published PyPI
dependency, is excluded. Findings, skipped dependencies and scanner failures
block the audit; no advisory suppression is used. PR checks exercise release
regressions with synthetic signing keys and never receive the production key.

## Operator commands

Use a disposable standalone clone, with full history and branch `main`, for a
local plan. A linked worktree cannot safely bootstrap shared tag refs.

```powershell
git clone https://github.com/AetherraLabs/Aetherra.git aetherra-release-check
cd aetherra-release-check
python -m pip install . -r requirements/release.txt
python -m pip check
python -m pip freeze --all --exclude aetherra | Set-Content -Encoding ascii release-environment.lock
python tools/vuln_scan.py --lock release-environment.lock --exact-pins --fail-level low
python tools/run_release.py --plan
python -m pytest tests/tools/test_release_bootstrap.py tests/tools/test_release_ci.py tests/tools/test_release_version.py -q -o addopts=
```

Prefer the automatic workflow. To retry current main after its signed CI passes:

```powershell
gh workflow run release.yml --repo AetherraLabs/Aetherra --ref main
gh run list --repo AetherraLabs/Aetherra --workflow release.yml --limit 3
```

If publication failed **after** the bot pushed its version commit, main has
advanced and retrying the old run correctly fails the exact-SHA preflight.
The bot's `GITHUB_TOKEN` push does not trigger another CI run. From a clean
standalone clone of current main, submit an empty recovery commit with your
normal push credentials:

```powershell
git pull --ff-only origin main
git commit --allow-empty -m "chore: retry signed release publication"
git push origin main
```

This triggers full CI and a newly signed production bundle for the new exact
main SHA. A complete, verified release is preserved without rebuilding. For an
incomplete release, recovery requires the current tree to equal the tagged tree;
an empty recovery commit satisfies this. Release rebuilds and signs that version,
creates the GitHub release if missing, replaces partial assets, and verifies downloads.
Never bypass preflight or force-push historical tags to recover an upload.

Inspect the completed run and GitHub release; a version-plan success alone is not
publication evidence. Download all assets into an empty directory and verify:

```powershell
gh release download v0.5.0-beta.1 --repo AetherraLabs/Aetherra --dir release-assets
python tools/verify_release_manifest.py --manifest release-assets/release-manifest.json --dist release-assets --pubkey (Get-Content keys/release_signing_ed25519.pub -Raw).Trim()
```

Offline regressions use real Git and the pinned CLI to test the first beta and
the next increment, ref restoration on failure, shared-worktree rejection,
explicit publication target, and signed-manifest verification with synthetic keys.
