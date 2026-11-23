# Alpha Readiness Decision

Updated: 2026-11-22 (America/Denver)

## Decision

**Go for supervised synthetic verification; no-go for broader internal alpha.**
The alpha integration candidate passes the complete default suite, independent
review, remote CI, normal-launch restart, browser reconnection and live-model
checks. Desktop dependency disposition and a fresh desktop installation remain
open. No unattended operation or risk acceptance is inferred.

- Decision owner: Aetherra Labs.
- Integration: [PR #326](https://github.com/AetherraLabs/Aetherra/pull/326).
  Reviewed code: `ef064b7638bf0ad33825573e3340538239cce30c`; includes main `86982cc5` and the completed website migration.
- Clean runtime checkout: `7e5c5204f8973eafdb60c2c0513de6be97b6fc4f`. The only later
  Python change adds two import-section comments in a test. Frozen runtime
  source matches; the test's parsed Python structure is identical.
- Environment: Windows, Python 3.13.7, Node 22.18.0, the provisioned pinned Python
  environment and cached MiniLM model; fresh locked Observatory npm install.
- All conversations are synthetic. Profiles isolate local data directories;
  account/user isolation is not claimed. Aetherra is the persistent cognitive
  system; Lyrixa is her user-facing persona.

At this reviewed-code evidence checkpoint, final documentation-only descendant
CI, merge, clean-main verification and production signing are pending. Their
completed results will be recorded in PR #326. The evidence below establishes
the reviewed candidate; pre-merge checks alone are not a clean-main pass.

See [the checklist](ALPHA_READINESS_CHECKLIST.md),
[operator commands](ALPHA_OPERATOR_RUNBOOK.md) and
[integration evidence](evidence/internal_alpha_integration_2026-11-22.json).

## Repairs And Review

The saved candidate `198cbbca` repaired expired ingress, early response headers,
source-checkout identity configuration, SQLite connection ownership, coordination
serialization/discovery/cleanup, readiness accounting and test isolation.
[Its earlier evidence](evidence/internal_alpha_suite_2026-11-22.json) records
3,115 passing tests and the original failing reproductions.

Integration review found a further timing gap: a request could expire while
policy or registry admission was waiting, then reach generation or a successful
offline fallback. The follow-up resolves TTL once, rechecks the same deadline
before dispatch, rejects delayed fallback, releases only an expired stream's
own retry reservation, and balances active-stream counters. Generation already
started before expiry is not cancelled or rolled back.

Deterministic reproductions failed before correction. All 41 request-contract
cases now pass, including POST, GET and WebSocket retry ownership, blocked
worker lookup, late registry failure and stream-counter cleanup. Independent
review found no remaining scoped blocker; its 64 focused checks pass.

## Current Verification

| Gate | Result | Evidence / boundary |
| --- | --- | --- |
| Default repository suite | PASS | **3,135 passed / 40 skipped**, exit 0, 1864.98s; default collection, addopts and coverage. Skip reasons and log hash are retained. |
| Source provenance | PASS | Exact-byte frozen source copy; runtime matches the reviewed commit. Two test comments differ, with identical parsed Python structure. |
| Python quality | PASS | Zero new/edited violations; 980 unchanged legacy files, 53 resolved. Baseline unchanged. |
| Documentation | PASS | Consistency and PR Markdown gates pass. |
| Remote candidate CI | PASS | 36 successful checks on the reviewed code; optional auto-merge skipped. Final integration status is in PR #326. |
| Runtime Observatory | PASS | Fresh locked install, 18 tests, build/lint; browser unavailable after stop and automatically reconnected after restart. |
| Normal full CLI | PASS | Two clean-checkout processes; 12 JSON APIs in four samples; both Ctrl+C exits 0 without force. |
| Engine and governance | PASS for observation | No-provider degradation; gpt-4o ready; Guardian enforcing with intact audit; Homeostasis observe_only and zero actions. |
| Fresh live continuity | PASS | Three gpt-4o turns after restart: correct recall amid newer competitors, unknown door color, preserved identity; zero fallback. |
| Expiry and privacy | PASS | Four request paths in each process leave stored IDs unchanged; prompts and replies absent from ordinary runtime logs. |
| Signing | ENFORCED | No workflow, key, strict flag or Security/Guardian policy changes. Check PR #326 for post-merge production signature verification. |
| Broader alpha | NO-GO | Desktop dependency/fresh-install limits remain. |

## Normal Launch And Evidence Trace

Entry point: `python aetherra_os_launcher.py --mode full --no-gui --config <profile>/launcher.json`.
The recorded isolated ports are Hub 13301 and Observatory 13300. No runtime,
memory, retrieval or generation double was used for these manual checks.

```text
full CLI PID 53372, new synthetic local profile
  saved record 7e3e0eeaf811434ff9d5f332dc1fc78f
  saved three newer competing facts, including Copper Finch
  no-provider fallback is explicit; stop -> exit 0
full CLI PID 48712, same persisted directory, empty chat history
  retrieved 7e3e0eeaf811434ff9d5f332dc1fc78f
  generation evidence 7e3e0eeaf811434ff9d5f332dc1fc78f -> Lantern Room
  openai/gpt-4o; three live replies; fallback=false
  unknown door color acknowledged; Aetherra/Lyrixa identity preserved
  browser reconnects automatically; stop -> exit 0
```

The preceding 35-turn/nine-process varied live matrix remains historical
evidence. This pass repeats the three core live turns; offline restart
acceptance tests cover varied paraphrases, missing facts and separate profiles.

## Limits And Next Action

Security, Maintenance and Integration Validation evidence that is unavailable
remains unknown in the Observatory. Registry freshness is distinct from service
readiness. Optional policy denials, relative configuration defaults, watchdog
teardown logging, THREE.Clock deprecation and the GUI bundle warning remain
visible. No all-services-ready or remote-assistance-execution claim is made.

The desktop findings in [BUILD_REPRODUCIBILITY.md](BUILD_REPRODUCIBILITY.md) remain
separate from the CI lock audit. The provisioned environment's legacy
pyxnat/pathlib metadata conflict is not a fresh-install clearance. Installed-wheel
identity configuration, privileged live mutation, soak/load and unattended
operation remain unverified.

Use PR #326's final merge/clean-main record before deploying this candidate.
Then resolve the desktop dependency and installation limits before reconsidering
broader alpha. Stage 21 remains Active; Beta Hardening and Production Readiness
remain Planned. Unrelated staged/unstaged work is preserved.
