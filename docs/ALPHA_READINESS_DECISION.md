# Internal Alpha Readiness Decision

Date: 2026-11-23 (America/Denver)

**GO for supervised internal alpha on the documented Windows source-runtime
profile.** Desktop blockers, clean-main acceptance and required production
signing pass. **NO-GO for unattended or production operation and unverified
installation graphs.** The operating boundary below remains in force.

- Decision owner: Aetherra Labs.
- Integration: [PR #327](https://github.com/AetherraLabs/Aetherra/pull/327),
  merged as `a0e8857c22092b0acf0e997f8b02cf5e04f23be1`.
- Released main: `f55d48a94559364d393fbf10a1e84e397a5109aa`, `v0.5.0-beta.6`.
- Full-suite runtime checkpoint: `374a7213`; its runtime source is unchanged
  by the merge and version-only release commit.
- Supported profile: Windows x64, Python 3.13.7 source checkout, Node 22.18.0,
  PowerShell 7.5+, the normal full launcher and React Runtime Observatory.
- All conversations are synthetic. Separate local directories isolate storage;
  account/user isolation is not claimed. Aetherra is the persistent cognitive
  system; Lyrixa is her user-facing persona.

See [the checklist](ALPHA_READINESS_CHECKLIST.md),
[fresh installation commands](DESKTOP_INSTALLATION.md),
[operator commands](ALPHA_OPERATOR_RUNBOOK.md) and
[fresh-install evidence](evidence/desktop_alpha_2026-11-22.json) and
[clean-main acceptance](evidence/desktop_alpha_main_2026-11-22.json).

## Phase A Core Integration Candidate

Candidate base: `8902e161c728dca50f95555e16bfdfccf5f303b8`, on
`codex/integration-phase-a`. This addendum describes an unmerged focused change;
the historical main/release evidence below remains scoped to those revisions.

The baseline boot/Integration Validation checks passed, but targeted reproduction
found three integration defects: a startup scan could say ready with Memory and
Engine missing; daemon/file-derived Kernel observations could certify scheduling;
and a single Hub request thread blocked health behind generation. Full startup
also overrode Self-Incorporation disablement. The candidate requires actual core
registration and readiness, discloses provider selection as configuration-only,
retains optional states, honors disabled execution, and adds bounded concurrent
observation with serialized mutation ownership.

The normal full CLI parser/main passed the instrumented headless smoke with
real storage/retrieval and a generation-only offline double, then seven gpt-4o
turns without fallback. Both runs started empty local profiles and stopped/restarted
the runtime; all six processes exited zero without force. The live recall supplied
the original record and content to OpenAI after restart; a color not supplied
remained unknown, and a separate profile returned empty evidence. Live status
probes during chat peaked at 546 ms in the final live rerun (663 ms offline,
with other verification running concurrently). This is bounded responsiveness
evidence, not a throughput or soak guarantee, and does not reduce the cold
semantic-retrieval latency itself.

```text
PID 35000 writes 533780ffd6bf9e383ebe5c4ebf9ce2cf: Leona taught bicycle repair
  exit 0 -> PID 55152, same SQLite, empty conversation context
  retrieved ID = supplied evidence ID = 533780ffd6bf9e383ebe5c4ebf9ce2cf
  openai/gpt-4o: "Your aunt Leona showed you..."; fallback=false
```

Guardian remained enabled/enforcing with intact audit. Homeostasis was
`observe_only` with zero actuator attempts/executions/blocks; Self-Incorporation
reported disabled and Self-Improvement reported no automatic implementation.
Strict capability/network/script/signing settings remained enabled; release
workflows, trust keys and the fixed quality baseline are unchanged.

Independent review additionally reproduced shutdown during active generation
and configured cross-origin busy-response gaps; their focused repairs and final
regressions are recorded with the [Phase A evidence](evidence/integration_phase_a_2026-11-23.json).
The final default suite passed **3,348 tests, with 38 skips and 5 passing subtests**,
then exited zero. It retained default collection, addopts and coverage; all
1,412 Python files match the frozen verification source byte-for-byte. The
existing optional/platform skips and diagnostic failures are recorded in the
evidence, not counted as passes. Boot validation (4 checks), Integration Validation
(5 checks), signing regressions (13 tests), the fixed quality baseline and docs
checks passed. Independent review found no remaining blockers in the candidate.
The initial live attempt was sandbox-network denied and used fallback; it is
retained as a failed attempt, not counted in the seven live turns.

**Decision: retain the bounded supervised internal-alpha GO on the previously
verified profile; do not advance Stage 22 or extend authority.** Candidate
integration/hosted CI remain separate gates. Phase B observation/maintenance is
next after this candidate is reviewed and integrated. The separate pending
TemporalConsciousnessEngine observer is preserved and not absorbed here.

This headless run did not repeat browser/interactive ConPTY verification. External
or shared Hub reuse is unverified. Current optional experimental/cognitive startup
is not quarantined yet; its existing diagnostics can fail independently of the
core and generic registry health is not proof of useful loop work. Phase C owns
that activation-order work. No unattended, production, alternate-platform or
account-isolation claim is made.

## First Supervised Use Exercise

The next Stage 21 step was a bounded **15-minute steady-state exercise** on
`ff359b02b8422ea3ef5132bbad3d241de64f0553` (merged PR #328), using the existing
verified Windows installation, normal full CLI, gpt-4o and a new synthetic local
profile. Ten minutes in PID 52828 and five minutes in PID 55764 completed across
a normal restart. All 32 samples checked 12 JSON endpoints; Hub, Kernel and
Engine readiness stayed ready, Guardian enforced with intact audit, and
Homeostasis stayed `observe_only` with zero actuator attempts/executions/blocks,
unexpected restarts or recoveries. Both processes exited zero without force.

All 16 baseline turns used gpt-4o without fallback. Bicycle and music paraphrases
retrieved the original records after restart with empty chat history; the unknown
piano color was acknowledged and Aetherra/Lyrixa identity remained intact.
The browser showed unavailable after stop and reconnected automatically. Engine
registry degradation and unknown optional services remained visible; these are
distinct from core readiness. No browser console errors were observed.

This exercise also found a real reply defect: new personal statements were saved,
but several initial replies incorrectly said Lyrixa had not been told them.
The current record is deliberately excluded from historical recall; the prompt
applied its missing-evidence rule to both disclosures and recall questions.
The candidate repair distinguishes current disclosures from recall, retains
receipt-only save claims, and does not treat questions/guesses as facts.
Storage, ranking and provider selection are unchanged. Its offline tests capture
actual provider input with a neutral generation double; live wording requires a
separate real-model check.

That separate check passed **13 gpt-4o turns without fallback** in a new profile:
plain disclosures, competing relatives/music, a mixed dog-name statement and
question, unknown bicycle-frame/piano colors, an unconfirmed soup guess and later
unknown-soup recall, and identity. All three positive recalls supplied the saved
record IDs to generation. The soup-guess reply included tentative wording but
did not confirm it; later recall correctly remained unknown with empty evidence.
The candidate process exited zero without force. The 25 focused offline tests
and 80 final Engine/disclosure tests pass (overlapping selections); 13 signing
tests pass. The fixed legacy baseline requires style cleanup of the edited Engine
file; normalized syntax-tree review found only the intended prompt change after
accounting for equivalent best-effort exception/control-flow formatting.

```text
PID 52828 saves 317b9b4ffc69b9a784fee68c0abdd151: Leona taught bicycle repair
  normal stop -> exit 0
PID 55764, same data, empty history: "Who showed me how to repair a puncture...?"
  retrieved ID -> generation evidence ID: 317b9b4ffc69b9a784fee68c0abdd151
  openai/gpt-4o -> "Your aunt Leona..."; fallback=false
```

The 15-minute observations describe unchanged main, not the candidate prompt.
At that checkpoint the prompt candidate had focused offline and live checks;
the correction subsequently integrated through PR #347. The earlier 3,136-test
result below is historical coverage of the prior runtime, not a Phase A pass.

The first post-restart recall took **63.603 seconds** total,
and a concurrent 10-second status probe timed out. It recovered without a runtime
restart or retrying the chat write. The five-minute window began afterward.
A separate earlier sampler attempt failed on a disappearing child process;
its partial samples were retained and the full ten-minute window restarted.
Neither failed attempt counts toward the 15 minutes. This is **not** evidence of
uninterrupted cold-start responsiveness, leak-free operation or soak/load capacity.

**Decision: retain the bounded supervised GO; do not advance Stage 22.** The
disclosure correction is now integrated. The Phase A candidate above addresses
concurrent status responsiveness within Stage 21.
Required signing and the approved key remain unchanged. Detailed outcomes and
artifact digests belong in
[the supervised-use evidence](evidence/supervised_alpha_2026-11-22.json).

## Previous Integration Is Complete

[PR #326](https://github.com/AetherraLabs/Aetherra/pull/326) merged as `382e77ac`.
Its clean-main verification passed 60 focused regressions, boot/integration,
normal launch and three gpt-4o turns without fallback. Main CI and required
production signing passed. The automatic
[v0.5.0-beta.5 release](https://github.com/AetherraLabs/Aetherra/releases/tag/v0.5.0-beta.5)
completed; its manifest signature and wheel/source archive hashes were verified.
That earlier provisioned environment did not establish a fresh desktop install.

## Integrated Acceptance

PR #327's final revision passed 36 checks; optional auto-merge was skipped.
The clean merged-main tree exactly matches that reviewed revision. All 87
focused installation, continuity and signing regressions pass, as do dependency
consistency, exact lock sync, boot, integration, import and hygiene checks.
The complete 3,136-test run covers the unchanged runtime source.

Clean main's normal full launcher completed three more gpt-4o turns with no
fallback, retrieved the original saved record, rejected four expired requests
without storage changes, and exited zero without force. Its first probe arrived
while Homeostasis was initialized but not yet running; the retained observation is separate
from the passing startup/steady samples. Wait for launcher initialization before
assessing steady readiness; an HTTP 200 alone does not establish readiness.

All 12 main validation workflows and the automatic Release workflow passed.
Production CI verified the required signature against the approved repository
public key. Published `v0.5.0-beta.6` manifest signature and wheel/source archive
hashes were independently verified. The release changes only CHANGELOG, README
version text and the project version; the clean released-main badge check passes.
No private key, secret or signing-control change was needed.

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

## Historical Desktop Verification (2026-11-22)

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
| Normal full CLI | PASS | Two candidate processes plus one clean-main process; 12 JSON endpoints in six samples; every Ctrl+C exit 0 without force. |
| Engine and governance | PASS for observation | No-provider degradation; gpt-4o ready; Guardian enforcing and audit intact; Homeostasis observe_only and zero actions. |
| Live continuity | PASS | Three candidate and three clean-main gpt-4o turns: correct recall, unknown door color and preserved identity; no fallback. |
| Expiry and privacy | PASS | Eight candidate and four clean-main expired requests leave storage unchanged; prompts/replies absent from ordinary runtime logs. |
| Signing | ENFORCED | Existing production workflows, approved key and strict settings unchanged; signature/tampering regressions retained. |
| Integration acceptance | PASS | PR #327 merged; clean-main checks, 12 main workflows, required production signature and published beta.6 signature/hashes pass. |

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

Stage 21 remains the active phase for supervised internal-alpha operation on
this verified profile. Beta Hardening and Production Readiness remain Planned.
Broader profiles and operating authority require their own evidence and decision.
Unrelated staged/unstaged work was preserved throughout installation and acceptance.
