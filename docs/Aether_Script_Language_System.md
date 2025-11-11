# Aether Script Language System (`.aether`)

> Version: 1.1
> Status: Stable
> Maintainer: Aetherra Labs
> Purpose: Defines the syntax, structure, execution rules, and
> operational profiles of `.aether` (Aether Script), the native language
> of the Aetherra Operating System.

## Runtime Execution Semantics: Retry & Timeout

Workflow steps are executed actively rather than returned as static
metadata. Each step supports two reliability modifiers:

1. retry=N (integer ≥ 0)
    - Attempts the step up to N+1 times (initial + N retries)
    - Exponential backoff with base 100ms, doubling per attempt
    - Stops early on first success

2. timeout=duration
    - Maximum wall-clock time per attempt
        - Units: ms, s, m, h; fractions supported (e.g., 0.5s, 2.5m)
    - Prefer unquoted tokens (e.g., `timeout=150ms`, `timeout=0.2s`)

### Duration normalization

The interpreter normalizes durations to seconds using
`<number>(ms|s|m|h)`:

- ms → number / 1000
- s  → number
- m  → number × 60
- h  → number × 3600

Quoted durations (e.g., `timeout="0.1s"`) may be parsed by a fallback
path, but unquoted forms are preferred until quoted forms are formally
documented.

### Step result schema (augmented)

```jsonc
{
  "name": "<str>",
  "retry": "<int?>",
  "timeout": "<raw token?>",
  "timeout_secs": "<float?>",
  "attempts": "<int>",        // attempts performed (≤ retry+1)
  "success": "<bool>",
  "result": "<any?>",         // present iff success
  "error": "<str?>",          // present iff success == false
  "duration_ms": "<float>"    // total elapsed time across attempts
}
```

- rollback_plan includes a restore dict (variables with pre-transaction values) and a
    delete list (variables introduced during transaction).
- rollback_simulated flags when a simulate_error statement is present inside a transaction
    for testing rollback logic.

Planned additions (not yet implemented): `start_time`, `end_time` (epoch seconds) per step attempt for finer-grained tracing.

### Timeout behavior

Timeout is enforced per attempt via `asyncio.wait_for()`. If an attempt
exceeds `timeout_secs`, that attempt fails with a timeout error and the
retry loop proceeds (if retries remain). The final result has
`success: false` and `error: "Timeout after <secs>s"` if all attempts
time out.

### Backoff strategy

Exponential backoff: `delay = 0.1 * 2^(attempt-1)` seconds between
attempts (attempts are 1-indexed). Backoff is not applied after the
final attempt.

### Alias binding (as <alias>)

If a step includes `as alias_name` and succeeds, its `result` value is
injected into the workflow context under `alias_name` for subsequent
steps’ expression resolution.

### Failure semantics

- Non-timeout exceptions mark the attempt failed; retry proceeds if available
- Final failure object includes the last error string encountered
- Mixed failure modes (e.g., timeout first, then non-timeout exception) report the last error

### Testing status

Tests cover: retry on simulated failure, timeout enforcement on a slow
step with small timeout, immediate success, alias binding. All passing
as of Nov 10, 2025. Additional combined scenarios (retry + timeout) can
be added.

### Roadmap items

- Per-attempt metrics array (attempt timing, individual errors)
- Configurable backoff (policy-level override instead of fixed exponential)
- Structured error codes (e.g., TIMEOUT, EXEC_ERROR) for downstream automation
- Documentation of quoted duration forms and validation for malformed tokens

## Implementation status (Option 1 + 2 + 3 complete)

Current lightweight interpreter: `aetherra_script_service.py`.

- **Implemented (Option 1):** goal, assignment with expression evaluation (booleans, numbers, strings, lists, arithmetic,
    identifiers), if / elif / else (nested supported), for-in over lists/variables, guarded while, workflow (steps with
    as/retry/timeout/requires), meta, on_error (structural).

- **Implemented (Option 2):** parallel (block-local assignments captured as tasks), await (identifier list), transaction
    (structural capture of inner ops; ops count, rollback tokens, and rollback_plan with restore/delete targets exposed),
    policy (block; key=value; duration normalization for *_secs), require (block; plugins/capabilities with = and : syntax),
    plugin_contract (block; key=value).

- **Implemented (Option 3):** dict literals {key: value} with nesting and variable references, typed assignments
    (name: Type = value; type hints stored in \_types metadata), enhanced require block with plugins = \[...\] and
    capabilities = \[...\] syntax, transaction blocks store records in \_transactions context for payload exposure; rollback_plan
    includes restore/delete actions keyed by rollback_token; policy keys ending with "timeout" or "duration" have normalized
    *_secs fields; workflow requires list is inherited into steps; boolean logic parser with precedence (not > and > or)
    and parentheses support; simulate_error statement for transaction rollback testing.

### Option 3: Require block examples and payload fields

Supported syntaxes for require blocks:

- Dash-list form
    require
            plugins:
                    - "summarizer>=0.2"
            capabilities:
                    - "memory.read"

- Inline list with equals
    require
            plugins = ["summarizer>=0.2"]
            capabilities = ["memory.read", "network.write"]

Interpreter behavior and payload exposure:

- Collected requires are exposed in result.payload as a list of require groups, and tests/wrappers may merge them:
    payload["requires"]: [
        {"type": "require_block", "plugins": [..], "capabilities": [..]}
    ]
- Policy key-values (from block or inline) appear under:
    payload["policy"]: { "deterministic": true, "seed": 1337, ... }
- Transactions include per-block records, rollback tokens, and a
    convenience rollback registry keyed by token:

```jsonc
payload["transactions"]: [
    {
        "type": "transaction",
        "ops": 2,
        "ops_count": 2,
        "rollback_token": "...",
        "rollback_plan": {
            "restore": { /* ... */ },
            "delete": [ /* ... */ ]
        },
        "rollback_simulated": false
    }
]

payload["rollback_tokens"]: [
    "..."
]

payload["rollback_registry"]: {
    "<token>": {
        "restore": { "x": 10 },
        "delete": ["y"]
    }
}
```

- rollback_plan includes a restore dict (variables with pre-transaction values) and a delete list (variables introduced during transaction).
- rollback_simulated flags when a simulate_error statement is present inside transaction for testing rollback logic.
- Typed assignment hints are returned under:
    payload["types"]: { "count": "int", "items": "List[str]" }
- Soft warnings (non-fatal) may be included when requires cannot be fully validated at parse time:
    payload["warnings"]: [
        "missing_plugins:summarizer>=0.2",
        "capabilities_unverified:network.write"
    ]

- Capability verification (if security policy is available) records verified items and can be made strict:
    payload["verified_capabilities"]: ["memory.read", ...]
  - When a capability cannot be verified, a soft warning is added by default:
        `missing_capabilities:cap1,cap2` or `capabilities_unverified:cap1,cap2` when the policy module is unavailable.
  - Strict mode (fail-fast) is enabled with `AETHERRA_REQUIRE_CAPABILITIES=1`, which raises an error if any required
        capability is missing for the current requester.

- Not yet implemented:
  - Active runtime execution for retry/timeout
  - on_error exception dispatch
  - break/continue
  - function invocation (calls preserved as strings)

- **Test coverage:** 46/46 tests passing across Options 1-3 (13 control flow, 5 parallel/await/transaction/policy/require, 10
    dict literals/typed assignments/enforcement, 4 arithmetic precedence, 1 workflow kwargs/durations, 3 capability verification,
    2 transaction rollback, 4 boolean precedence, 2 policy duration normalization, 2 workflow requires inheritance).

- Architecture note: advanced runtime/parsers under `Aetherra/core` and `Aetherra/runtime` are broader but not yet
    unified with the new block-aware lightweight path.

- Examples: see `workflows/health_check_conditional.aether`, `workflows/batch_processing_loop.aether`, and
    `workflows/plugin_chain_workflow.aether` (signatures pending; run signing tool when stabilised).

---

## 📌 Overview

Aether Script is a **declarative-intent language** for cognitive workflows, plugin coordination,
and memory-based execution logic. It is whitespace-sensitive, human-readable, and
interpretable by AI agents and the Aether Runtime.

It blends human goals with formal logic so autonomous systems can **understand**, **reason over**,
and **evolve** the script content.

---

## 🧱 1. Top-Level Grammar (v1.1)

```ebnf
script          ::= (statement | comment | blank_line)+

statement       ::= goal_stmt
                 | meta_block
                 | policy_block
                 | require_block
                 | on_error_block
                 | plugin_contract_block
                 | memory_stmt
                 | assignment
                 | function_call
                 | conditional
                 | workflow_block
                 | loop_block
                 | parallel_block
                 | await_stmt
                 | transaction_block

goal_stmt       ::= "goal:" string_literal
memory_stmt     ::= "memory:" function_call

assignment      ::= identifier ":" expression
                 | typed_assignment

typed_assignment::= identifier ":" type_hint "=" expression

type_hint       ::= identifier ("[" type_hint ("," type_hint)* "]")?

expression      ::= string_literal
                 | number_literal
                 | boolean_literal
                 | null_literal
                 | function_call
                 | identifier
                 | list_literal
                 | dict_literal

function_call   ::= identifier "(" [call_arguments] ")"
call_arguments  ::= argument ("," argument)*
argument        ::= expression | identifier "=" expression

conditional     ::= "if" expression ":" block
                 [ "else:" block ]

loop_block      ::= "for" identifier "in" expression ":" block

workflow_block  ::= "workflow:" INDENT workflow_body DEDENT
workflow_body   ::= (assignment | list_of_steps)+
list_of_steps   ::= "- " step
step            ::= identifier ["(" [call_arguments] ")"]
                    [ "as" identifier ]
                    [ "retry=" integer ]
                    [ "timeout=" (duration | string_literal) ]
                    [ "requires=" list_literal ]

duration        ::= number_literal ("ms"|"s"|"m"|"h")

block           ::= INDENT statement+ DEDENT

comment         ::= "#" [any characters]
blank_line      ::= NEWLINE

parallel_block  ::= "parallel:" INDENT (assignment)+ DEDENT
await_stmt      ::= "await" identifier ("," identifier)*

transaction_block ::= "transaction:" INDENT (assignment | list_of_steps)+ DEDENT

meta_block      ::= "meta:" block
policy_block    ::= "policy:" block
require_block   ::= "require:" block
plugin_contract_block ::= "plugin_contract:" block
on_error_block  ::= "on_error:" INDENT on_error_rule+ DEDENT
on_error_rule   ::= "- when:" identifier NEWLINE INDENT "do:" function_call DEDENT

boolean_literal ::= "true" | "false"
null_literal    ::= "null"

🔤 2. Tokens & Primitives
- identifier — summarize, log, daily_digest
- string_literal — "system state", 'hello world'
- number_literal — 42, 3.14, -10
- boolean_literal — true, false
- null_literal — null
- list_literal — ["a", "b", "c"]
- dict_literal — { key: value, ... }

📘 3. Statements
3.1 goal:
Declares the primary intention or objective of the script.

aether

goal: "Clean memory and summarize logs"
3.2 memory:
Initializes a memory operation or loads a memory scope.

aether

memory: load_feature_index()
3.3 Assignment (: syntax)
Stores a value, function output, or expression in a named identifier.

aether

summary: summarize(memory)
anomalies: detect(summary)
Typed assignment (optional, for tools/LSP; engine may ignore at runtime):

aether

summary: Summary = summarize(memory)
flags: List[Anomaly] = detect_anomalies(summary)
Note: Type hints improve auto‑completion and static checks; runtime may coerce/ignore.
3.4 Function Call
Calls a system-defined or plugin-defined function. Supports positional and keyword arguments.

aether

escalate_to("Lyrixa")
store(summary, tag="daily")
3.5 Conditionals
Basic branching logic.

aether

if anomalies:
    reflect_on(anomalies)
else:
    store(summary, tag="normal_day")
3.6 Loops
Iterate over memory, plugin outputs, or structured lists.

aether

for plugin in available_plugins():
    check_confidence(plugin)
3.7 Workflow Block
Declarative chaining of plugin steps with reliability controls and capability gating.

aether

workflow:
    input: "design.json"
    output: "game.rbxmx"
    steps:
        - parse_input as parsed
        - generate_assets(parsed) as assets retry=2 timeout="30s"
        - assemble_scene(assets) as scene requires=["graphics.render"]
        - export_game(scene, target="rbxmx")

Step fields:
- as alias — bind step result
- retry=N — retry count on failure
- timeout=1s|30s|5m — duration literal (string or numeric with unit)
- requires=[...] — capabilities required to run step
Interpreter payload enrichments for workflow steps:
- args: positional arguments evaluated via the expression engine
- kwargs: keyword arguments evaluated and captured as a dict
- timeout_secs: normalized seconds from timeout (e.g., 30s -> 30.0, 5m -> 300.0)
- requires: if the workflow has a requires property (list), it is merged into each step's requires field (no duplicates)
🧠 4. Built-in Functions (Standard Library)
- reflect() — Triggers self-introspection
- summarize(x) — Condenses logs, memory, or text
- load_logs() — Loads logs by tag, date, or range
- store(x, tag) — Saves memory or artifacts with metadata
- detect_anomalies() — Flags irregularities or contradictions
- escalate_to(x) — Sends alert or report to named agent
- run_plugin(x) — Executes a plugin by name
- evaluate_confidence(x) — Returns a confidence score
- self_heal() — Attempts to rewrite or fix itself
- narrate() — Outputs a narration of the script’s effects

Observability (v1.1):
- trace(level="debug") — attach step I/O and memory deltas to the run record
- log("message") — free‑form message to OS log
- metrics({"coherence": 0.97, "contradictions": 1}) — structured counters/metrics

These are dynamically linked to runtime plugin and agent systems.

🧩 5. Plugin Contracts (Verifiable Manifests)
Formalize plugin behavior and chaining compatibility. Used for static verification at bind time and aligns with hub strict/non‑strict modes.

aether

plugin_contract:
    id: "anomaly_detector"
    version: ">=0.3,<0.5"
    input_schema: {"type":"array","items":{"type":"string"}}
    output_schema: {"type":"object","required":["flags"]}
    deterministic: true
    side_effects: false
    timeout: "30s"
    permissions: ["memory.read"]

Runtime checks:
- Version constraints must match installed plugin.
- I/O schemas are validated on call boundaries.
- Deterministic + side_effects=false is required in deterministic policy runs.
🧬 6. Execution Semantics
Lazy Resolution: Steps are resolved in dependency order using current memory context.

Symbol Table: All assignments are tracked and exposed to Lyrixa or other agents.

Failure Handling: Fallbacks, retries, or escalations are supported via plugin metadata or conditionals, and first‑class via on_error:.

Agent Delegation: Certain functions (e.g. reflect, self_heal) may dispatch tasks to sub-agents.

Parallel & Await: Assignments within parallel: become promises. await resolves them; failures propagate to on_error:.

aether

parallel:
    a: summarize(load_logs(tag="system"))
    b: summarize(load_logs(tag="user"))
await a, b
merged: run_plugin("report_merger", [a, b])

Transactions & Idempotency: A transaction: block guarantees atomic commit or rollback for effectful ops. Engine issues a rollback token.

aether

transaction:
    - store(summary, tag="daily")
    - escalate_to("Ops")

Determinism Profiles: In deterministic policy runs the runtime enforces seeded randomness,
disables non‑deterministic plugins unless mock_io is true, and records a reproducible
narrative trace.

🧱 7. File Structure Conventions
Scripts reside in scripts/, workflows/, or intelligence/

Extensions must be .aether

Top-level goal is always required

Tabs are disallowed (use spaces only)

🔐 8. Security & Verification (Core in v1.1)
- require: declares plugin and capability prerequisites. Engine fails fast if unsatisfied.
- policy: governs risk and token budgets, data classification, determinism and mocks.
- plugin_contract: enables static I/O verification and timeout/permission checks.
- Signatures: Distributed `.aether` files may be signed; strict hub/runtime modes enforce verification.
- Trust-scoring: Optionally influenced by execution history or memory traceability.

### Operator notes: signature headers and signing

- Signature header format: the first line must be `# @signature: <hex>`.
    - The signature is computed over the script body (everything after the header) with exact bytes preserved (no newline normalization).
    - Avoid auto-formatting the first line or changing line endings after signing.
- Signing utility: run `tools/sign_aether.py` to embed/update headers; safe to re-run and works on multiple files.
- Strict verification: use the editor task “Aether Verify (Strict Signatures)” or run `tools/verify_aether_scripts.py --root . --strict`.
    - Also respects `AETHERRA_SCRIPT_VERIFY_STRICT=1` and supports `--exclude` globs for CI.
- Mutable artifacts: evolving logs (e.g., `evolution_history.aether`) may be excluded from signature checks in CI; operational scripts should be signed.

📎 9. Core Blocks (New in v1.1)

Meta:

aether

meta:
    version: "1.1"
    author: "Aetherra Labs"
    seed: 42

Policy:

aether

policy:
    risk_budget: 0.20
    token_budget: 50_000
    data_class: "internal"
    deterministic: true
    seed: 1337
    mock_io: false
    request_timeout: "30s"

Duration normalization: keys ending with "timeout" or "duration" produce additional *_secs numeric fields (e.g., request_timeout_secs: 30.0).

Require:

aether

require:
    plugins:
        - "anomaly_detector>=0.3,<0.5"
        - "report_merger==1.2.1"
    capabilities: ["storage.write", "network.read"]

Syntax alternatives: plugins = \[...\], capabilities = \[...\] (inline list) are supported.
Capability verification: if Aetherra.security.capabilities is available, has_capability is invoked for each required capability; verified items appear in payload["verified_capabilities"]; missing items trigger soft warnings unless AETHERRA_REQUIRE_CAPABILITIES=1 (strict mode).

On Error:

aether

on_error:
    - when: Timeout
    do: escalate_to("Lyrixa")
    - when: PermissionError
    do: narrate("missing capability: storage.write")

Await:

aether

await a, b

Notes:
- AETHERRA_STRICT and AETHERRA_HUB_STRICT environment flags select strict/lenient verification.
    The policy block can override determinism and mocks per‑run in CI or tests.

📎 10. Future Grammar Extensions (post v1.1)
- agent: dispatch tasks to specific AI agents
- visualize: render memory graphs or output summaries
- while and advanced comprehensions

🧭 11. Spec Diff v1.0 → v1.1 (Summary)
- Added kwargs in function calls; introduced boolean and null primitives.
- Promoted meta, policy, require, on_error to core blocks.
- Enhanced workflow steps with as/retry/timeout/requires.
- Introduced parallel/await concurrency and transaction blocks.
- Added observability built‑ins: trace, log, metrics.
- Formalized plugin_contract for verifiable manifests.
- Added optional type hints via name: Type = expr.
- Clarified determinism/test profiles and strict verification alignment.

🧭 12. Summary
.aether is a semantic-first language for orchestrating thought-driven computation inside the
Aetherra OS. It emphasizes clarity of intention, adaptability, and integration with intelligent
memory, agent systems, and evolving plugins.

The goal is not just to describe what the system does, but to encode why it does it — making the code itself a living participant in the cognition of the OS.

Examples:
- See `examples/daily_anomaly_digest.aether` for a runnable v1.1 script using meta/policy/require, parallel/await, on_error, transaction, and observability.
- See `workflows/health_check_conditional.aether` for conditionals & nested branching.
- See `workflows/batch_processing_loop.aether` for for / while loop constructs.
- See `workflows/plugin_chain_workflow.aether` for workflow steps with options & on_error handlers.

### Minimal Interpreter (Option 1 + 2) Supported Syntax Cheat Sheet

```text
goal "..."

# Assignments / expressions
name = 42
flag = true
items = ["a", "b", "c"]
counter = counter + 1

# Conditionals
if condition
    ...
elif other_condition
    ...
else
    ...

# Loops
for item in items
    ...
while counter < 10
    counter = counter + 1

# Workflow
workflow
    input = "file"
    requires = ["storage.read", "compute"]
    - load_data as data retry=2 timeout="30s"
    - process_data(data) as result requires=["compute"]
    - save_results(result)

Note: if the workflow block has a requires property (list of strings), these requirements are inherited and merged into each step's requires field (deduplication applied).
Boolean expressions: not > and > or precedence; parentheses supported. Examples: not false and true => true; (false or true) and false => false.

# Meta
meta
    version = "1.1"
    author = "User"

# On Error (structural capture only)
on_error
    - when Timeout
      do escalate_to("Ops")
    - when PermissionError
      do narrate("Missing permission")

# Parallel / Await
parallel
    x = load_x()
    y = load_y()
await x, y

# Transaction (structural capture only; rollback_plan exposed)
transaction
    - store(result, tag="daily")
    - escalate_to("Ops")

Transaction blocks capture:
  - ops_count: number of inner operations
  - rollback_token: unique identifier for this transaction
  - rollback_plan: { restore: {var: old_val}, delete: [new_vars] } showing how to reverse effects
  - rollback_simulated: true if a simulate_error statement is encountered (for testing)

# Policy / Require / Plugin Contract (structural capture only)
policy
    deterministic = true
    token_budget = 50000

require
    plugins = ["anomaly_detector>=0.3,<0.5"]
    capabilities = ["storage.write"]

plugin_contract
    id = "anomaly_detector"
    version = ">=0.3,<0.5"
```

### Next Implementation Targets (Beyond Option 1)

| Feature                             | Status      | Notes                                                              |
| ----------------------------------- | ----------- | ------------------------------------------------------------------ |
| parallel / await                    | Structural  | Assignments captured; no promise model                             |
| transaction:                        | Structural  | Ops counted; rollback_plan and tokens exposed; no active hooks yet |
| policy:, require:, plugin_contract: | Structural  | Parser + metadata exposure; enforcement partial                    |
| Typed assignments / type hints      | Implemented | Parsed; types stored in \_types metadata                           |
| Break / continue                    | Pending     | Control flow flags in loop processor                               |
| Function invocation                 | Partial     | Calls preserved as opaque strings in results (no execution)        |
| Retry / timeout semantics           | Structural  | Metadata recorded; no timing logic yet                             |
| on_error execution                  | Structural  | Captured; not triggered by runtime exceptions                      |
| Dict literals                       | Implemented | Nested and variable references supported                           |
| Boolean precedence (not>and>or)     | Implemented | Recursive‑descent parser; parentheses and comparisons supported    |
| Arithmetic beyond '+'               | Implemented | Precedence with -, *, /, %, unary minus, parentheses               |
| Workflow requires inheritance       | Implemented | Workflow‑level requires merged into steps                          |
| Policy duration normalization       | Implemented | Keys ending with "timeout" or "duration" produce *_secs fields     |
| Transaction rollback_plan           | Implemented | Restore/delete actions exposed; simulate_error for testing         |

> Tracking: These items map to future “Option” phases after Option 1 completion.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
