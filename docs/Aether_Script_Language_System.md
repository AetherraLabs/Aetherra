# Aether Script Language System (`.aether`)

> Version: 1.1
> Status: Stable
> Maintainer: Aetherra Labs
> Purpose: Defines the syntax, structure, execution rules, and operational profiles of `.aether` (Aether Script), the native language of the Aetherra Operating System.

---

## 📌 Overview

Aether Script is a **declarative-intent language** designed to describe cognitive workflows, plugin coordination, and memory-based execution logic. It is whitespace-sensitive, human-readable, and interpretable by AI agents and the Aether Runtime.

It blends human goals with formal logic in a way that allows autonomous systems to **understand**, **reason over**, and **evolve** the script content.

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

Determinism Profiles: In deterministic policy runs, the runtime enforces seeded randomness, disables non‑deterministic plugins unless mock_io is true, and records a reproducible narrative trace.

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

Require:

aether

require:
    plugins:
        - "anomaly_detector>=0.3,<0.5"
        - "report_merger==1.2.1"
    capabilities: ["storage.write", "network.read"]

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
- AETHERRA_STRICT and AETHERRA_HUB_STRICT environment flags select strict/lenient verification by default. The policy block can override determinism and mocks per‑run in CI or tests.

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
.aether is an expressive, semantic-first language for orchestrating thought-driven computation inside the Aetherra OS. It emphasizes clarity of intention, dynamic adaptability, and integration with intelligent memory, agent systems, and evolving plugins.

The goal is not just to describe what the system does, but to encode why it does it — making the code itself a living participant in the cognition of the OS.

Examples:
- See `examples/daily_anomaly_digest.aether` for a runnable v1.1 script using meta/policy/require, parallel/await, on_error, transaction, and observability.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
