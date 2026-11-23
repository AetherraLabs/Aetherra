# Alpha Readiness Decision

Updated: 2026-11-22 (America/Denver)

## Decision

**Go for supervised synthetic verification of this candidate; no-go for broader
internal alpha operation.** The remaining reproduced suite failures and the
false Engine degradation are repaired. The final default repository suite
finished with **3,115 passed / 40 skipped**, with process exit 0. Full launcher, stop/restart,
browser reconnection and live-model continuity also pass. Candidate CI, merge,
clean-main verification and desktop dependency disposition remain open.

- Decision owner: Aetherra Labs. This technical assessment does not accept
  outstanding risks on the owner's behalf or authorize unattended operation.
- Base main: `d00120e8d8fb5f14f5b1f5fa1bd295ceb9c25930`, `v0.5.0-beta.4`.
  Verification used the isolated `codex/alpha-chat-contracts` candidate before
  publication; the evidence records that checkpoint's source and state.
  This is a candidate pass, not a clean-main or remote-CI pass.
- Environment: Windows, Python 3.13.7, Node 22.18.0; provisioned runtime and
  cached MiniLM dependencies. Task-local tools match the repository pins:
  Ruff 0.17.6 (metadata and binary), Black 26.10.1, isort 9.0.2. Shared
  environments and the fixed legacy style baseline are unchanged.
- All conversations are synthetic. Profiles isolate local data directories;
  account/user isolation is not claimed. Aetherra is the persistent cognitive
  system; Lyrixa is her user-facing persona.

See [the checklist](ALPHA_READINESS_CHECKLIST.md),
[operator commands](ALPHA_OPERATOR_RUNBOOK.md),
[fresh suite and launch evidence](evidence/internal_alpha_suite_2026-11-22.json) and
[the preceding chat-contract/live-matrix checkpoint](evidence/internal_alpha_2026-11-22.json).

## Repairs And Review

Integration resumed in [PR #326](https://github.com/AetherraLabs/Aetherra/pull/326),
including main's completed website migration. Review found a further admission
race: a turn could expire during policy or registry waits and still dispatch or
return a successful fallback. The follow-up preserves the resolved deadline,
rejects before dispatch, releases only the expired stream's retry reservation,
and balances active-stream counters. Its 41 deterministic request-contract tests
pass, including reproductions that failed before correction. The full suite is
being rerun for this follow-up; the 3,115-test result below remains evidence for
the preceding saved candidate, not a claim about these additional edits.

The preceding checkpoint repaired ALPHA-07, the original nine legacy cases and
the capability test that replaced real packages in `sys.modules`. Those changes
remain in this candidate: expired chat requests fail before storage/generation,
standard headers survive early errors, identity configuration resolves from the
source checkout, and signed plugin tests use the real capability implementation.

The first complete diagnostic rerun after that isolation fix exited 1:
**5 failed / 3,059 passed / 44 skipped / 21 errors**. Follow-up development was
in progress in that editable checkout, so this is diagnostic evidence, not an
immutable baseline. Each repair also has a focused failing reproduction and
passing regression recorded in the evidence.

| Failure | Repair and evidence |
| --- | --- |
| Windows SQLite teardown errors | Close all 14 owned alert-manager connection scopes after transaction completion, preserving commit/rollback. Seven real-connection regressions prove closure on success/error/early return; 28 related tests pass. |
| Multi-node tests and discovery | Preserve the strict severity boundary; serialize/restore node-state enums, advertise actual ephemeral ports, close writers without masking cancellation, and remove a nonexistent placeholder signal access. Tests use actual ephemeral TCP discovery; 30 pass. Remote assistance execution remains simulated. |
| Quiesce loop and Phase 7.4 order | Give the test its own event loop; use package-relative imports and the real temporal engine's constructor in the experimental harness. Ordered reproduction and real-state regression pass; 25 related tests pass. |
| Streaming retry order | Scope SSE environment settings with pytest cleanup. The exact ordered pair failed before the change; all 14 related streaming tests now pass. |
| Quality-tool setup errors | The old provisioned environment resolved Ruff binary 0.12.1 despite metadata 0.16.0. A task-local environment supplies the exact pinned tools; all 12 quality-tool tests pass. No baseline expansion. |
| False Engine degradation | Count complete successful lifecycle receipts separately from actual problems. Unknown/malformed receipts remain failures. All 19 readiness tests pass; actual no-provider failure still degrades, while configured live generation reports ready. |

Independent review findings around writer cleanup, malformed success receipts
and fixed-port discovery were reproduced and corrected. Final review found no
remaining blocker in these scoped changes. Signing enforcement was not weakened.

## Verification Results

| Gate | Result | Evidence / boundary |
| --- | --- | --- |
| Default repository suite | PASS | 3,115 passed / 40 skipped; default collection, addopts and coverage; process exit 0 in 1740.01s. Individual skip reasons are retained in evidence; no new skips/xfails added. |
| Source provenance | PASS | Final run uses a frozen source copy; all changed Python hashes match the candidate. An earlier attempt with the wrapper's wrong cwd was stopped and excluded. |
| Boot / integration / imports / hygiene | PASS | Four boot and five integration contracts; import and hygiene checks pass. |
| Documentation | PASS | Final consistency and Markdown checks are recorded separately in the evidence. |
| Fixed-baseline Python quality | PASS | Zero new/edited violations; 980 unchanged legacy files, 53 resolved. Baseline unchanged. |
| GUI | PASS | 18 tests, build and lint; reused the previously installed locked GUI dependencies. |
| Normal full CLI | PASS | Two processes, 12 JSON APIs at startup and steady state; both Ctrl+C child exits 0 without force. |
| Engine readiness | PASS | No-provider: degraded, 4 events / 1 problem. Configured gpt-4o: ready and safe_for_requests=true, 3 events / 0 problems. |
| Governance | PASS for observation | Guardian enforcing with intact audit; Homeostasis observe_only; actuator/recovery/restart counters zero in all four samples. |
| Browser | PASS | Automatic unavailable state after stop, automatic reconnect, Engine readiness matching JSON, read-only controls, three event titles; no application console errors observed. |
| Fresh live continuity | PASS | Three gpt-4o turns after restart: correct recall, honest unknown attribute and preserved identity; zero fallback. |
| Chat admission | PASS | Four expiry paths in each process reject before storage; stored IDs unchanged. Authentication, audit-limit and disabled-control guards retain expected status. |
| Signing | PASS within stated scope | Strict runtime flags retained; published beta.4 wheel/sdist hashes and Ed25519 signature verify with trusted public key. |
| Candidate integration / broader alpha | OPEN | Candidate remote CI, merge, clean-main verification and desktop dependency disposition remain. |

The earlier 35-turn gpt-4o matrix across nine stopped processes remains historical
evidence for varied paraphrases, competing facts, missing facts and separate
profiles. It was not rerun in this pass. The fresh three-turn normal-CLI check
above is recorded separately and does not count a fallback as a live pass.

## Normal Launch And Evidence Trace

Entry point: `python aetherra_os_launcher.py --mode full --no-gui --config <profile>/launcher.json`.
The run used Hub 13301 and Observatory 13300 with only Vite's server host,
ports and proxy overridden. Both default and recorded-port commands are in the
runbook. No runtime or generation double was used for these manual checks.

```text
full CLI PID 43068, new synthetic local profile, no configured provider
  explicit unavailable-model fallback; saved b0eec83f8b8578e96b912f3079739a84
  four expiry paths rejected; stored IDs unchanged; Ctrl+C -> child exit 0
  browser -> unavailable, every subsystem unknown, empty feed
full CLI PID 3740, same persisted directory, configured gpt-4o
  retrieved ID b0eec83f8b8578e96b912f3079739a84
  generation evidence ID b0eec83f8b8578e96b912f3079739a84 -> Lantern Room
  unknown door color acknowledged; Aetherra/Lyrixa identity preserved
  all three live replies: openai/gpt-4o, fallback=false
  Engine ready; browser automatically reconnects; expiry still rejects
  Ctrl+C -> child exit 0, no force; both PIDs gone; ports 13300/13301 closed
```

Each of the four samples returned 200 for all 12 JSON endpoints. Unauthenticated
chat returned 403, unauthenticated audit 401, disabled Kernel control 501,
invalid audit limits 400 and filtered authenticated audit 200. Synthetic
conversation content was absent from ordinary runtime logs.

## Limits And Next Action

Unregistered Security, Maintenance and Integration Validation UI evidence remains
unknown. Registry freshness can differ from service readiness. Optional policy
denials, relative configuration defaults and watchdog teardown logging remain
visible. THREE.Clock deprecation and the GUI bundle warning remain nonblocking.
No all-services-ready or remote-assistance-execution claim is made.

The desktop dependency findings in [BUILD_REPRODUCIBILITY.md](BUILD_REPRODUCIBILITY.md)
remain distinct from the CI lock audit. This provisioned environment also fails
`pip check` because legacy `pyxnat 1.6.3` requires an absent `pathlib`
distribution. The suite pass is not a fresh desktop install or a dependency
security clearance. Installed-wheel identity configuration, privileged live
mutation, soak/load and unattended operation were not verified.

The prior main [CI](https://github.com/AetherraLabs/Aetherra/actions/runs/45062835784),
[Quality Gates](https://github.com/AetherraLabs/Aetherra/actions/runs/45062835897)
and [signed Release](https://github.com/AetherraLabs/Aetherra/actions/runs/45063644307)
are baseline evidence, not candidate CI. No private key, signing workflow,
enforcement flag or legacy style baseline changed; no secret action is required.

Next, when work resumes: run candidate CI, merge only with
passing gates, and verify clean main. Resolve or explicitly disposition the
desktop dependency limits before broader alpha acceptance. Stage 21 remains
Active; Beta Hardening and Production Readiness remain Planned. Unrelated
staged/unstaged work and both original workspace indexes are preserved.
