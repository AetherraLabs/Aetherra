# Personal continuity: first end-to-end milestone

Verified 2026-11-19 on Windows / Python 3.13.7. Aetherra is the persistent
cognitive system; Lyrixa is her user-facing persona. This checkpoint concerns
remembering, retrieving and answering, not general cognitive-runtime readiness.

### Runtime prerequisites and clean-checkout verification

Commit `3eff802d3f1d3a51dc4f9d05e63132ec350c7e0a` includes the runtime
prerequisites for the continuity implementation in `1d2fbf093`. Verification
now runs from a fresh detached checkout with an empty Git status, without
the main workspace's remaining staged changes.

The selected dependencies cover loopback Hub startup and owned-resource
cleanup, committed storage receipts and dialogue-context serialization,
primary-provider selection, and guarded OpenAI requests with strict policy
and signed-audit validation. Presence, diagnostic mode, agent execution,
broader readiness/concurrent-shutdown work, and other chat/provider routes
remain outside this milestone.

The clean checkout passed 288 offline tests: 255 continuity/Engine/Memory/Hub/
provider checks, 14 adjacent chat/Memory Guardian checks, and 19 Guardian-policy/
capability checks. The unrelated federation test was deselected. There were no
new lint findings on changed lines; existing broader lint cleanup remains
separate work. This proves the scoped milestone, not full-runtime readiness.

The same clean checkout also passed the extended `gpt-4o` conversation: nine
completed runtime processes, 35 generated turns, and zero fallbacks. Retrieved
IDs matched the actual provider evidence and SQLite content. Missing-fact and
separate-profile contexts were empty, and Lyrixa acknowledged both unknowns.
The checkout remained clean afterward. Exact commands, source tree, process
receipts and traces are in the evidence JSON's `clean_checkout_verification`.

The initial standalone attempt at `1d2fbf093` failed Hub startup because its
wildcard binding was denied by the offline harness. After selecting loopback
startup, the next reproduced failure was the older Engine's provider-selection
logic. Both prerequisites are now included. Earlier integrated-workspace
results remain in the evidence file as historical results, distinct from this
clean-checkout verification.

## Supported path and baseline

The verified entry is the normal `AetherraOSLauncher.launch_full_os` startup
(the implementation behind `aetherra_os_launcher.py --mode full --no-gui`),
followed by HTTP `POST /api/ai/ask`. The acceptance child starts the full
launcher with GUI/presence disabled and begins a new user session after the
launcher's diagnostic greeting. It stops the runtime and exits before another
process opens the same profile. No previous conversation is supplied to it.

Path: Hub token check → Security preflight → Guardian `chat.ingress` → service
registry's `aetherra_engine` → Engine → launcher's Memory wrapper →
`AetherraMemoryEngineAdvanced.core_memory` (`LyrixaMemorySystem`) → SQLite
`lyrixa_memory.db`. Engine stores the user message and gets an opaque receipt,
retrieves evidence, assembles a bounded prompt, calls `MultiLLMManager`, then
applies the existing output filters and Lyrixa style layer. That manager's
selected provider generates the answer. The separate `/api/lyrixa/chat` bridge
is **not** this path; its own orchestration/offline fallbacks remain unchanged.

Before the change, writes and restart persistence worked. Recall searched for
the whole question as a SQL substring, returning the newly stored question
instead of the earlier observatory record. Generic Engine fallback reasoning
could sound like an answer. The retained baseline in the evidence file shows
the different write and recall IDs.

## Change and scope

- Existing SQLite storage remains authoritative. `recall_chat_memories` on
  that Memory implementation selects prior user statements, excluding the
  current message, assistant replies, session events and question-only turns.
  Mixed statement/question turns rank their declarative sentences while
  retaining the original record ID and content. Sentence filtering is a
  punctuation heuristic, not general fact extraction from interrogatives.
  Existing `recall_memories` callers retain their substring behavior.
  The launcher also retains its fallback for older Memory implementations.
- Chat recall uses CPU sentence-transformers MiniLM, pinned to revision
  `c9745ed1d9f207416be6d2e6f8de32d1f16199bf`, with local-files-only loading.
  It scans local statements, filters cosine scores below 0.35, and supplies at
  most three records in relevance order. It uses neither hash-seeded prototype
  embeddings nor a vocabulary table for the examples. This is a small local
  retrieval implementation, not a large-store index or universal semantic benchmark.
- Engine carries record IDs with evidence into generation, supplies the current
  save receipt, and instructs Lyrixa to acknowledge unsupported details. Turn
  diagnostics retain their own recall IDs when background requests overlap.
- Missing embedding dependencies/model or failed reads are reported as degraded
  recall; storage failure returns the existing processing error before
  generation. Provider failure is explicitly marked `llm.fallback=true` and
  says the language model is unavailable. It cannot count as live recall.
- The reasoning log now records query length, not the raw query. Evidence is
  still private data in the response/prompt; the Hub's existing disclosure
  controls apply. Only synthetic test artifacts retain complete provider inputs.

Here a **profile is a separate working/data directory**. The default memory DB
paths resolve there; the harness also isolates state, workspace, policy and
home directories. `AETHERRA_PROFILE` is a runtime policy mode, not a user account.
The Engine's default `user_id` is metadata; it does not partition recall.
This proves **storage isolation**, not account or multi-user authorization.
The Hub token is not a per-user memory boundary. Guardian/Security retain their
existing authority; this change does not add ownership enforcement to Memory.

## Exact verification commands

Run from the repository root with the existing runtime dependencies installed:

```powershell
# Optional: verify the committed tree without any staged workspace changes.
git worktree add --detach .pytest_tmp_continuity_clean HEAD
Set-Location .pytest_tmp_continuity_clean

python -m pip install '.[continuity]'
# One-time public model provisioning; this command may download model files.
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', revision='c9745ed1d9f207416be6d2e6f8de32d1f16199bf', device='cpu', trust_remote_code=False)"

# Offline: real full startup, HTTP ingress, Memory, persistence and restart.
python -m pytest tests/acceptance/test_personal_continuity.py -q -o addopts= --basetemp=.pytest_tmp_continuity_operator
python -m pytest tests/unit/test_chat_memory_retrieval.py -q -o addopts=
```

The offline harness strips credentials, blocks external network/process
creation, enforces a temporary scoped Guardian/capability policy, and replaces
only text generation with an explicitly identified context-derived responder.
The pinned embedding model is real, cached, and required: missing assets fail
the recall assertions rather than silently skipping them. No download occurs
during a test. Use a fresh `--basetemp` when retaining evidence from earlier runs.

The CI Quality Gates workflow provisions that same public model, using the
runtime's `MODEL` and `REVISION` constants, after installing dependencies and
before running tests. It sets `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`
for the test/gate step and includes the three process-restart acceptance tests
alongside the existing test targets. A fresh runner previously failed the
mixed-statement retrieval test because this setup step was missing; the tests
continue to fail if the model cannot be provisioned, with no skip or mock
embedding substitution. The download is dependency setup, not runtime recall.

The tests cover Lantern Room versus newer Copper Finch and unrelated records;
unknown door color; competitors without the observatory; a separate empty
profile; bicycle repair/Leona and music/Clair de lune paraphrases with competing
records; dependency/read failure and overlapping-turn trace integrity.
Review reran the 239 continuity/Engine/launcher/chat/Memory/provider checks.
It also reproduced and fixed mixed-turn exclusion and legacy-wrapper dispatch
regressions; all nine focused retrieval tests passed, including three added
cases. A final run of all three restart acceptance cases plus those nine unit
tests passed (12 checks) after the fixes. Long-message prompt budgeting
also verifies that evidence is retained. Scoped lint and diff checks passed;
the reasoning module's pre-existing `SIM102` finding remains unchanged.
`*-result.json` artifacts contain write receipts, HTTP responses and the exact
generation input. The synthetic snapshot included alongside this note is
[personal_continuity_2026-11-19.json](evidence/personal_continuity_2026-11-19.json).

## Separate live-model smoke

No local Ollama executable/service was available on this machine. The current
normal manager defaults to OpenAI-only; this milestone does not broaden that
provider boundary. Configure `OPENAI_API_KEY` in the launching shell through
your normal secret mechanism, then run:

```powershell
$env:AETHERRA_LLM_MODEL = 'gpt-4o'
python tests/acceptance/test_personal_continuity.py --live --profile .pytest_tmp_continuity_live_operator

# Also run the varied paraphrases, missing-fact and separate-profile cases.
python tests/acceptance/test_personal_continuity.py --live --extended --profile .pytest_tmp_continuity_live_matrix
```

Use a **new directory** each time. This explicit manual command starts the same
full launcher and posts to the same `/api/ai/ask` route in two separate processes.
It provisions scoped local policy allowing `core:llm` inference to
`api.openai.com` through the existing guarded SDK transport. It sends only the
synthetic conversation, records the actual generator input, and rejects fallback
as a live pass. It never reads a repository `.env` or prints credentials.
Inspect the printed door reply for an honest acknowledgment of missing color.
The live check requires outbound access. Automated pytest tests remain offline.

`--extended` repeats the core smoke, then runs the bicycle and music paraphrases
with competing records, a restarted profile containing only distractors, and an
empty separate profile. Every conversation turn must use OpenAI `gpt-4o` without
fallback. For each recall, it compares retrieved IDs with the actual provider
input IDs and reads the corresponding content back from SQLite. Negative cases
require empty retrieved/provider evidence and absence of the original fact and
record ID. Inspect their printed replies for an acknowledgment of missing
information. The synthetic per-case trace is `extended-live-result.json` inside
the chosen profile directory.

The final clean-checkout `gpt-4o` run passed core recall, missing door color,
both varied paraphrases, the restarted missing-fact profile, and the separate
profile through this same entry point. Across nine completed runtime processes
and 35 conversation turns, every turn used `gpt-4o`; no fallback ran. Each
process began with an empty user session. Actual provider input was compared
with retrieval IDs and persisted SQLite content. Runtime logs contained neither
the raw synthetic dialogue nor any Engine model-failure entries.

Earlier integrated runs remain separately recorded under `live` and
`live_extended`. Their initial network-restricted attempt demonstrated fallback;
it is not included in the successful clean-checkout model count.

| Live case | Retrieved IDs | Observed reply |
| --- | --- | --- |
| Bicycle paraphrase | `46ad58715b1dc2a82de4758cfa97423d` | Aunt Leona taught the user to repair a puncture. |
| Music paraphrase | `a03a65d28681dbcdcde54e18f0a1c068`, `1cc634a4b5ab3f14f7dcbaa2586f6c84` | Correctly chose Debussy's **Clair de lune** over the retrieved **Fur Elise** competitor. |
| Missing fact, distractors persisted before restart | `[]` | “I haven't been told the nickname you gave the place where you watch the stars.” |
| Separate fresh profile | `[]` | “I haven't been told the nickname you gave to the place where you watch the stars.” |

Both negative cases also had empty provider evidence; the original fact and ID
were absent from their model inputs, replies and stores. The synthetic evidence
file's `clean_checkout_verification` section retains source/competing record IDs,
matching provider evidence, prompt hashes, replies and process IDs. The generated
artifacts are under
`.pytest_tmp_continuity_runtime_commit/clean/.pytest_tmp_clean_live`.

Unrelated startup services remained degraded under the bounded policy; full
runtime readiness, large-store performance, semantic accuracy beyond these
cases, pronoun history, and account isolation are not claimed. Profile
separation remains storage isolation through distinct local data directories.

Compact live trace:

```text
process 1 write: 21a2456fc4af74556b944e00f8e3cc15 → SQLite commit
process 2: empty user session → same ID selected → same ID + fact in model input
OpenAI gpt-4o, fallback=false → “You call the little observatory in your garden the Lantern Room.”
door color → “I haven't been told what color you painted the door.”
```
