# Internal Alpha Readiness Decision

Date: 2026-11-22 (America/Denver)

**Desktop installation blockers are resolved in the candidate. GO for supervised
synthetic verification of this Windows source-runtime profile; NO-GO for an
integrated internal-alpha release until merge and clean-main acceptance are
complete.** No unattended operation or broader risk acceptance is inferred.

- Decision owner: Aetherra Labs.
- Candidate: [PR #327](https://github.com/AetherraLabs/Aetherra/pull/327),
  `codex/desktop-alpha-install`; reviewed runtime code `374a7213`.
- Base: main `b827eccea181f672347ecf277bae99a97521c459`, `v0.5.0-beta.5`.
- Supported profile: Windows x64, Python 3.13.7 source checkout, Node 22.18.0,
  PowerShell 7.5+, the normal full launcher and React Runtime Observatory.
- All conversations are synthetic. Separate local directories isolate storage;
  account/user isolation is not claimed. Aetherra is the persistent cognitive
  system; Lyrixa is her user-facing persona.

See [the checklist](ALPHA_READINESS_CHECKLIST.md),
[fresh installation commands](DESKTOP_INSTALLATION.md),
[operator commands](ALPHA_OPERATOR_RUNBOOK.md) and
[inspectable evidence](evidence/desktop_alpha_2026-11-22.json).

## Previous Integration Is Complete

[PR #326](https://github.com/AetherraLabs/Aetherra/pull/326) merged as `382e77ac`.
Its clean-main verification passed 60 focused regressions, boot/integration,
normal launch and three gpt-4o turns without fallback. Main CI and required
production signing passed. The automatic
[v0.5.0-beta.5 release](https://github.com/AetherraLabs/Aetherra/releases/tag/v0.5.0-beta.5)
completed; its manifest signature and wheel/source archive hashes were verified.
That earlier provisioned environment did not establish a fresh desktop install.

## Reproduced Blockers And Repairs

The old 261-package desktop freeze failed pip resolution: `virtualenv==20.31.2`
requires `filelock<4`, while the freeze pins `filelock==4.2.1`. An advisory audit
reported vulnerabilities in 36 packages. Legacy Pyxnat also introduced the
obsolete `pathlib` distribution, and Streamlit constrained Pillow below the
repaired versions. These packages are outside the current source-runtime inputs.

The desktop lock now resolves the declared runtime and quality inputs explicitly,
constrained by compatible CI versions. It contains 167 exact pins, excludes
unrelated ambient packages, and preserves the old lock tool's no-input caller
behavior. Failed resolution leaves the previous lock intact. Tests use real
local wheels and pip, including installed transitives and conflicting constraints.
No source feature is deleted to reduce the audit graph.

Fresh installation exposed an import of removed `pkg_resources` in the existing
maintenance checker. It now reads standard-library distribution metadata.
Newly supported SPDX expressions use exact matching; compound/custom expressions
require review. Guardian report-write gates remain intact. This is a metadata
compatibility repair, not legal clearance for every dependency.

The diagnostic suite exposed two environment-sensitive defects. Dependency
analysis discarded a project if an ancestor directory started with a dot; it now
filters only paths inside the selected project. Metrics tests reused a singleton
listener on conflicting fixed ports; they now own real loopback listeners and
registries and close them after each test. No production metrics semantics,
test skip or quality-baseline allowance was added to hide a failure.

## Current Verification

| Gate | Result | Evidence / boundary |
| --- | --- | --- |
| Fresh Python installation | PASS | New venv with system-site packages disabled; 167 pins plus pip; dependency consistency and exact lock sync pass. |
| Installed-package audit | PASS | All 168 distributions audited, zero findings and zero skips; separate audit environment. Dated advisory snapshot. |
| Retrieval model | PASS | Pinned MiniLM downloaded into an initially empty cache; remote model code disabled. |
| Default repository suite | PASS | **3,136 passed / 40 skipped**, exit 0; immutable source, default collection/addopts/coverage. |
| Focused regressions | PASS | Resolver 2; metadata/Guardian 9; path/legacy analysis 14; metrics 2 in each order. These selections overlap the full suite. |
| Python quality | PASS | Zero new/edited violations; 978 unchanged legacy files, 55 resolved; baseline unchanged. |
| Hosted Windows installation | PASS | Fresh install/audit; 87 runtime/signing regressions; boot/integration; GUI 18 tests/build/lint. Reviewed runtime has 37 green checks. |
| Runtime Observatory | PASS | Fresh npm install, zero audit findings, 18 tests, build/lint; stop/reconnect verified with zero observed console errors. |
| Normal full CLI | PASS | Two fresh-venv processes; 12 JSON endpoints in four samples; both Ctrl+C exits 0 without force. |
| Engine and governance | PASS for observation | No-provider degradation; gpt-4o ready; Guardian enforcing and audit intact; Homeostasis observe_only and zero actions. |
| Live continuity | PASS | Three gpt-4o turns after restart: correct recall amid newer competitors, unknown door color, preserved identity; no fallback. |
| Expiry and privacy | PASS | Eight expired requests across four routes leave stored IDs unchanged; prompts/replies absent from ordinary runtime logs. |
| Signing | ENFORCED | Existing production workflows, approved key and strict settings unchanged; signature/tampering regressions retained. |
| Integration acceptance | PENDING | PR #327 must merge and pass clean-main verification before this is an integrated alpha release. |

The completed default run took 1476.39s and exited zero. All 1,395
Python source/test files match before and after execution. Individual skip
reasons and artifact digests are retained in the evidence. The desktop graph
omits the release-publishing SDK; its 14 real Git/CLI bootstrap tests separately
pass in the existing Semantic Release Dry Run job. Existing optional/platform
skips are reported explicitly, not counted as coverage of excluded features.
Five passing subtests are reported separately from the 3,136 passing tests.
The superseded diagnostic attempts do not count as suite passes.

## Fresh-Process Evidence Trace

No memory, retrieval, runtime or generation double was used in this manual check.
The initial no-provider fallback is separate from live-model passes.

```text
normal full CLI PID 35548, new synthetic local profile
  saved f8fa1f3588e240a2e1f57ab624c5f97a: Lantern Room
  saved three newer competitors, including Copper Finch
  explicit no-provider fallback; stop -> exit 0
normal full CLI PID 15600, same persisted directory, empty chat history
  retrieved f8fa1f3588e240a2e1f57ab624c5f97a
  generation evidence f8fa1f3588e240a2e1f57ab624c5f97a
  openai/gpt-4o -> Lantern Room; fallback=false
  unknown door color acknowledged; Aetherra/Lyrixa identity preserved
  browser reconnects automatically; stop -> exit 0
```

The earlier 35-turn/nine-process varied live matrix remains historical evidence.
This fresh-install pass repeats three core live turns. Offline real-storage,
real-retrieval restart tests cover varied paraphrases, missing facts and separate
profiles; their text-generation double reads only supplied evidence.

## Accepted Scope And Remaining Gates

The cleared dependency blockers apply to this Windows source-runtime profile.
Qt plugin GUIs, optional SDKs, quantum, research/export plugins and standalone
Lark grammar modules retain their source but require separate verification.
`pip install .` declares a different Qiskit-containing graph. Wheel-only installs,
other platforms/Python versions, privileged live mutation, soak/load and
unattended operation remain unverified.

Unavailable Security, Maintenance and Integration Validation evidence remains
unknown in the Observatory. Registry freshness is distinct from readiness.
Optional policy denials, relative configuration defaults, watchdog teardown
logging, THREE.Clock deprecation and the GUI bundle warning remain visible.
No all-services-ready or remote-assistance-execution claim is made.

Stage 21 remains Active pending integration acceptance. Beta Hardening and
Production Readiness remain Planned. The next gate is PR #327's final review,
green checks, merge, clean-main smoke and required production signature
verification. Candidate CI does not prove post-merge production signing.
Unrelated staged/unstaged work remains outside this PR.
