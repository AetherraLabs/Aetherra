# Repository modernization closeout

Administrative/evidence snapshot: 2026-11-26 (America/Denver).
Repository: AetherraLabs/Aetherra. Delivery and hosted review:
[PR #379](https://github.com/AetherraLabs/Aetherra/pull/379).
This record reconciles repository organization and documentation. It does not
expand the supervised internal-alpha boundary or resolve engineering defects.

## Development organization

The proposal in [#375](https://github.com/AetherraLabs/Aetherra/issues/375) was
implemented as five GitHub tracking milestones, without due dates or assignee
changes. Official Master Roadmap stages remain authoritative and unchanged.

Initial assignment snapshot, before registration of additional issue #381:

| Milestone | Assigned issues | Count |
| --- | --- | --- |
| [Internal Alpha — Runtime and Evidence](https://github.com/AetherraLabs/Aetherra/milestone/5) | #369, #370, #371, #372, #373, #374, #377 | 7 |
| [Self-Incorporation — Foundation Verification](https://github.com/AetherraLabs/Aetherra/milestone/6) | #42, #43, #44, #45, #47, #48, #56, #63, #66, #67, #68, #69, #73, #74 | 14 |
| [Future Scope — Governed Expansion](https://github.com/AetherraLabs/Aetherra/milestone/7) | #55, #57, #70, #71, #72, #75 | 6 |
| [Research — Offline Evaluation](https://github.com/AetherraLabs/Aetherra/milestone/8) | #58, #59 | 2 |
| [Contributor Experience](https://github.com/AetherraLabs/Aetherra/milestone/9) | #376, #378 | 2 |

All 31 assignments were independently checked against issue metadata and
milestone-filter endpoints. The 22 previously assigned issues retain their exact
original body prefix and links to old/new milestones. Milestones #1–#4 retain
their IDs, names, descriptions, states and existing closed assignments. Tracking
issue #76 retains milestone #4; #375 remains unmilestoned. Both are pinned.

All nine status/priority labels retain their names and IDs and now have meaningful
colors and descriptions. The other 48 labels are unchanged. Before registration
of #381 and documentary closure of #377, the 33-open-issue filter snapshot was:

| Status | Count | Priority | Count |
| --- | --- | --- | --- |
| active | 6 | high | 5 |
| planned | 14 | medium | 17 |
| research | 2 | low | 9 |
| deferred | 6 | intentionally unprioritized tracking | 2 |
| community | 3 | | |
| tracking | 2 | | |

Counts describe that initial snapshot, not a quota. Subsequent registration of
[#381](https://github.com/AetherraLabs/Aetherra/issues/381) formalizes the prior
unresolved capability timeout already documented in PR #368 and the similar
PR #379 observation. It adds one active/medium issue and one assignment to
milestone #5; it does not recreate the backlog or establish a common cause.
The original 31 assignments remain intact; the added issue makes 32.

With #381 registered, documentary closure of #377 will leave 33 open issues:
status counts active 7, planned 14, research 2, deferred 6, community 2 and
tracking 2; priority counts high 4, medium 18 and low 9. Milestone #5 will contain
eight assigned issues (seven open, #377 closed). These are conditional closeout
counts until #377 closes; no engineering record closes with it. Every issue has
one status classification; #76/#375 remain intentionally unprioritized tracking.
Priority is review order, not severity or release-blocking status.

GitHub's aggregate milestone counters disagreed with the verified filtered
assignments at inspection (notably #6/#7/#8 reported zero rather than 14/6/2).
No milestone or issue was recreated to force a counter refresh. Use the actual
issue lists until GitHub's counters reconcile.

## Evidence and traceability

The [Development Issue Register](DEVELOPMENT_ISSUES.md) links reciprocally to
issues #369–#374. ALPHA-CKPT-001, DEV-CKPT-001, DEV-AUDIT-001 and DEV-OBS-001 retain
their IDs. Collision-checked DEV-HOMEOSTASIS-001 and DEV-STORM-001 now record
watchdog shutdown and skipped persistence evidence. All six remain OPEN with
owners, next actions and closure gates; no unknown cause is assigned from reruns.
Additional [DEV-CI-001](DEVELOPMENT_ISSUES.md#dev-ci-001--capabilities-job-timeout-before-a-result-summary)
links [#381](https://github.com/AetherraLabs/Aetherra/issues/381) to the
[four-log CI receipt](evidence/ci_capabilities_timeout_2026-11-26.json). The
original six C2b records and this seventh CI record all remain OPEN.

The [merged-main review receipt](evidence/c2b_merged_main_review_2026-11-26.json)
and [readiness decision](ALPHA_READINESS_DECISION.md#c2b-merged-main-evidence-review-2026-11-26)
separate merge `592c4622`'s full suite, released `5662300`'s offline continuity,
and candidate-only live/browser/physical checks. Historical failures and receipt
files remain retained. Documentation acceptance under #377 is separate from
engineering closure, risk acceptance and a new GO decision.

## Presentation and verification

PR #379's original README, CONTRIBUTING, issue-picker and PR-template changes
were reviewed. Narrow follow-ups make historical/intermittent defect reports
possible, retain research topics under explicit future-scope wording, add a
clickable contributor redirect, and use the enabled private security-report route.
No runtime, dependencies, workflows or enforcement configuration change here.

Checks for this documentation-only delivery:

- Parse all four issue YAML files and both Markdown frontmatters; validate IDs.
- Run focused Markdown lint with `markdownlint-cli2@0.13.0` and `.markdownlint.jsonc`.
- Run `python tools/verify_docs_consistency.py`; archive its generated report separately.
- Check changed relative links/anchors, 19 original C2b archive hashes, four CI log hashes and unchanged historical receipts.
- Run `git diff --check` and review hosted checks on the exact PR head before merge.

Discussions and GitHub private vulnerability reporting are enabled. SECURITY.md
retains `security@aetherra.dev`; mailbox delivery was not tested and no message was
sent. At inspection, main had no branch protection or repository rulesets defining
required checks. All applicable PR checks are therefore reviewed explicitly;
this closeout does not change branch policy or weaken any signing gate.
The existing Markdown workflow is informational, so direct lint is required here.

At PR head `6a1b978a`, the Linux capability step timed out before a result summary.
Its unchanged-checkout retry passed 171 tests / 4 skips in 62.42 seconds and then
8 SSE tests in 32.76 seconds. PR #368 had a similar preserved timeout followed
by a passing retry. Both failures remain unexplained in DEV-CI-001; a common
cause is not established. No runtime fix or timeout change is included here.
Unchanged runtime/test/workflow content does not prove documentation irrelevant,
because the static-security capability test scans repository contents. Final
checks must run on the resulting pushed revision.

The detailed Self-Incorporation guide reconciliation (#376) and full contributor
entry-path audit (#378) remain separate open work. Temporal observer PR #380 is
paused for this closeout and remains a separate integration review.
