# Aetherra Engine System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Status: v0.1 Functional Complete

The Aetherra Engine System is the cognitive runtime coordinator for Aetherra.
It receives intent, builds context, coordinates reasoning, uses memory, produces
bounded responses, submits governed work, and reports readiness.

The Engine exists to answer one question:

**How does Aetherra think through this moment?**

It is not the whole organism. It is not the Guardian. It is not Security. It is
not Self-Incorporation. It is the central cognitive processing path inside the
larger Aetherra operating layer.

Core rule:

```text
The Engine thinks and coordinates.
Guardian decides.
Security enforces.
Memory preserves.
Agents specialize work.
Self-Improvement proposes.
Self-Incorporation executes approved changes.
Homeostasis verifies.
Kernel manages runtime lifecycle.
Lyrixa presents Aetherra to the user.
```

## Purpose and Scope

Aetherra is a governed cognitive operating layer designed to maintain memory,
continuity, reasoning, self-regulation, and safe evolution through specialized
systems with separated authority.

The Engine gives that organism one stable cognitive runtime path. It turns
incoming messages, goals, tasks, and system events into structured reasoning
flows while respecting the authority boundaries of every other system.

The Engine should make Aetherra feel coherent without becoming all-powerful.
It may coordinate cognition, but it must not collapse governance, enforcement,
execution, memory ownership, and self-modification into one subsystem.

## Definition

The Aetherra Engine is Aetherra's active reasoning coordinator.

It is responsible for:

- receiving user, system, agent, and runtime intent;
- normalizing that intent into bounded engine requests;
- building cognitive context from session state, memory, system state, and
  constraints;
- invoking reasoning providers or reasoning subsystems;
- producing response payloads for Lyrixa, Hub, agents, and future clients;
- submitting work to the correct governed subsystem;
- reporting health, readiness, degraded state, and failure state.

The Engine is not responsible for:

- approving actions;
- enforcing permissions;
- bypassing Guardian or Security;
- directly mutating privileged runtime state;
- installing plugins;
- self-modifying code;
- executing Self-Incorporation plans;
- overriding Homeostasis verification;
- owning the user's interface identity.

## Relationship to Aetherra

Aetherra is the cognitive operating layer.

Lyrixa is the persona and primary user-facing expression of Aetherra.

The Engine is the cognitive processor that helps Aetherra interpret, reason,
respond, and submit work.

Simple identity map:

```text
Aetherra = governed cognitive operating layer
Lyrixa = persona/interface
Engine = cognitive runtime coordinator
Guardian = decision authority
Security = enforcement authority
Kernel = runtime lifecycle authority
```

The Engine should make Aetherra coherent. It should not pretend to be the
entire system.

## Cognitive Operating Intelligence Alignment

The Engine supports Aetherra's long-term Cognitive Operating Intelligence goal
by coordinating five ideas without owning all of them:

| COI Principle | Engine Responsibility | Owned Elsewhere |
| --- | --- | --- |
| Goal-causal computing | Preserve intent, purpose, trace IDs, and reasoning context | Maintenance, Guardian, audit ledgers |
| Observer relativity | Carry observer/session context into reasoning | Memory owns persistence and branching |
| Ethical configurability | Include active ethical/policy context in requests | Guardian/Security enforce policy |
| Identity-bound coherence | Preserve continuity signals and self-model context | Memory/Consciousness own durable identity |
| Quantum-fractal memory | Use memory retrieval results as evidence | Memory owns storage and retrieval policy |

The Engine coordinates these signals. It does not replace the systems that own
them.

## Authority Ownership

| Authority | Owning System | Engine Behavior |
| --- | --- | --- |
| Interpret intent | Engine | Normalizes messages, goals, tasks, and runtime prompts |
| Build cognitive context | Engine | Combines session state, memory summaries, constraints, and system status |
| Reason | Engine | Invokes reasoning path and produces bounded reasoning output |
| Present persona | Lyrixa | Engine returns payloads; Lyrixa shapes the user-facing experience |
| Preserve memory | Memory | Engine requests recall/store through Memory contracts |
| Approve or deny action | Guardian | Engine submits intent for review before privileged task execution |
| Enforce capabilities/security | Security | Engine depends on Security for policy, sandbox, signing, network, and audit |
| Schedule runtime lifecycle | Kernel | Engine reports state; Kernel manages lifecycle |
| Execute specialized work | Agents | Engine submits approved or allowed work to Agent System |
| Propose improvement | Self-Improvement | Engine sends observations and metrics; it does not self-improve directly |
| Apply approved change | Self-Incorporation | Engine must not apply code/runtime mutations itself |
| Verify outcome | Homeostasis | Engine exposes results and health for verification |

Ownership rule: if an Engine path needs an authority that belongs to another
system, the Engine must call that system instead of duplicating the authority
locally.

## Core Lifecycle

Canonical Engine flow:

```text
Receive intent
Normalize request
Assign trace/session identifiers
Build cognitive context
Recall relevant memory
Apply safety and policy context
Reason
Generate bounded response or task plan
Submit governed work if needed
Record metrics and improvement signals
Report status
```

For action-oriented requests:

```text
Intent
Engine interpretation
Guardian review when privileged
Security enforcement
Agent/Kernel/Aether Script/Self-Incorporation dispatch
Homeostasis verification
Maintenance record
```

The Engine should not skip directly from interpretation to privileged action.

## Functional Layers

### Layer 1: Intent Intake

Purpose: accept input safely and convert it into a bounded request.

Responsibilities:

- Accept message, task, goal, and runtime request inputs.
- Validate input shape and size.
- Sanitize prompt-injection markers and unsafe content where appropriate.
- Assign trace IDs and session IDs.
- Preserve the user's intent without blindly obeying unsafe instructions.

Failure behavior:

- Invalid request shape returns a bounded validation error.
- Unsafe input is sanitized or rejected.
- No raw exception details are returned to callers.

### Layer 2: Context Construction

Purpose: build the working cognitive context for the current moment.

Responsibilities:

- Include current session state.
- Request relevant memory from Memory.
- Include active system status where available.
- Include Guardian/Security/Homeostasis constraints where relevant.
- Keep context compact, bounded, and privacy-aware.

Failure behavior:

- Memory failure degrades response quality but must not grant new authority.
- Missing optional context is recorded as degraded state.
- Sensitive memory or internal details are not leaked into public responses.

### Layer 3: Reasoning

Purpose: interpret the request and decide the next cognitive step.

Responsibilities:

- Classify whether input is conversational, analytical, operational, or
  task-oriented.
- Invoke the reasoning provider or reasoning subsystem.
- Produce confidence, uncertainty, and evidence-grounding signals.
- Keep reasoning output bounded and auditable.

Failure behavior:

- Reasoning failure returns a safe internal-processing error payload.
- Fallback reasoning is marked as degraded.
- The Engine must not fabricate authority or pretend an action succeeded.

### Layer 4: Response Generation

Purpose: produce safe response payloads for Lyrixa, Hub, agents, and clients.

Responsibilities:

- Produce human-readable output.
- Include confidence and trace metadata where appropriate.
- Avoid exposing secrets, stack traces, internal paths, or raw prompts.
- Preserve Aetherra's identity: this is a cognitive operating layer, not a
  chatbot pretending to be independent from the system.

Failure behavior:

- Response generation failure returns a stable error code and trace ID.
- Sensitive details stay in internal logs or audit records after redaction.

### Layer 5: Governed Work Submission

Purpose: route work to the correct subsystem without bypassing authority.

Responsibilities:

- Convert action requests into structured task submissions.
- Submit agent work through the Agent System.
- Submit workflow intent through Aether Script or Kernel paths where applicable.
- Request Guardian review before privileged or risky operations.
- Depend on Security for capability and sandbox enforcement.

Failure behavior:

- Guardian denial blocks submission.
- Security denial blocks execution.
- Invalid task payloads fail before dispatch.
- No active task record is created for denied privileged work.

### Layer 6: Learning Signals

Purpose: report observations without self-modification.

Responsibilities:

- Record interaction metrics.
- Send improvement observations to Self-Improvement.
- Report recurring failures, low confidence, latency, and degraded components.
- Preserve traceability between request, response, and improvement signals.

Failure behavior:

- Self-Improvement unavailability does not block basic response generation.
- Metrics failure is observable but does not crash the Engine.
- The Engine must not directly apply its own proposed improvements.

### Layer 7: Readiness and Observability

Purpose: make Engine state visible to operators and other systems.

Responsibilities:

- Expose read-only status.
- Report component availability, degraded state, and readiness.
- Track safety filters, processing failures, task submissions, and latency.
- Support Hub, Runtime UI, Kernel, and Maintenance visibility.

Failure behavior:

- Missing required components make readiness blocked.
- Optional unavailable components are reported as degraded.
- Status endpoints must remain bounded and safe.

## Current Implementation Surfaces

Primary implementation:

- `Aetherra/aetherra_core/engine/aetherra_engine.py`
- `Aetherra/aetherra_core/engine/readiness.py`
- `Aetherra/aetherra_core/engine/reasoning_engine.py`
- `Aetherra/aetherra_core/engine/self_improvement_engine.py`

Related Hub/API surfaces:

- `aetherra_hub/blueprints/ai_ask.py`
- `aetherra_hub/blueprints/ai_stream.py`
- `aetherra_hub/blueprints/ai_api.py`
- `aetherra_hub/blueprints/kernel.py`
- `GET /api/ai/status`

Related tests:

- `tests/unit/test_aetherra_engine_hardening.py`
- `tests/unit/test_engine_memory_compatibility.py`
- `tests/unit/test_engine_reset_env_vars.py`
- `tests/failure_injection/test_memory_offline.py`
- Hub AI and metrics tests under `tests/unit/`

Related documentation:

- `docs/AETHERRA_ARTIFICIAL_INTELLIGENCE_SYSTEM.md`
- `docs/AETHERRA_CHAT_SYSTEM.md`
- `docs/AETHERRA_AGENT_SYSTEM.md`
- `docs/AETHERRA_MEMORY_SYSTEM.md`
- `docs/AETHERRA_GUARDIAN_SYSTEM.md`
- `docs/AETHERRA_SECURITY_SYSTEM.md`
- `docs/AETHERRA_KERNEL_SYSTEM.md`

## Functional Completion Criteria

The Engine is functionally complete for the current alpha foundation milestone
when it satisfies these requirements:

- One canonical Engine path is identified and documented.
- Engine status exposes required, optional, degraded, and blocked components.
- Message processing returns bounded payloads with trace IDs.
- Memory recall/store failures are safe and test-covered.
- Reasoning failures are safe and test-covered.
- Task submission validates payloads before dispatch.
- Privileged task paths use Guardian review and Security enforcement.
- Denied privileged tasks do not create active task records.
- Engine responses do not leak secrets, internal paths, stack traces, raw
  exception text, or private implementation details.
- Self-Improvement receives observations or metrics without gaining execution
  authority through the Engine.
- Functional tests cover the normal path, degraded component path, denied
  privileged path, and sanitized failure path.

Current completion state:

- Complete for controlled alpha foundation.
- Safe enough to operate as the central cognitive coordinator behind Lyrixa,
  Hub, agents, memory, readiness, and governed task submission.
- No known alpha-blocking Engine debt remains in the current authority boundary.

Implemented hardening coverage:

- Message payload validation and bounded response contracts.
- Readiness contract for required, optional, degraded, and blocked components.
- Alpha readiness reporting through the Engine readiness model.
- Persistent memory bridge readiness and degraded-state reporting.
- Task submission preflight with Guardian review and Security enforcement for
  privileged paths.
- Sanitized task preflight, decision, and submission diagnostics.
- LLM provider normalization, bounded prompt construction, evidence truncation,
  and provider timeout controls.
- Scratchpad bounds, entry sanitization, and failure diagnostics.
- Coherence and reflection diagnostics that report degraded state without raw
  exception exposure.
- Failure-path tests for memory, reasoning, Guardian denial, task validation,
  readiness, scratchpad, coherence, reflection, and LLM runtime contracts.

Current verification snapshot:

Verified on 2026-07-18:

```powershell
python -m pytest -q -o addopts= --basetemp .pytest_tmp_engine_complete tests\unit\test_aetherra_engine_hardening.py tests\unit\test_ai_readiness.py tests\unit\test_engine_package_contract.py tests\unit\test_engine_memory_compatibility.py tests\unit\test_engine_reset_env_vars.py tests\unit\test_ai_engine_guardian.py tests\unit\test_ai_stream_engine_failures.py tests\unit\test_hub_ai_api.py tests\failure_injection\test_memory_offline.py
python -m Aetherra.integration_validation
python tools\alpha_boot_validation.py
python tools\verify_docs_consistency.py
git diff --check
```

Results:

- Engine focused and adjacent Hub/Guardian tests passed: 85 tests.
- Integration Validation passed: 5 checks.
- Alpha boot validation passed: 4 checks.
- Docs consistency passed.
- Whitespace check passed.

## Understanding Rule

Before the Engine is considered complete, it must be explainable without looking
at code.

What it does:

- Coordinates Aetherra's cognitive runtime path.
- Receives intent, builds context, reasons, responds, submits governed work, and
  reports readiness.

Why it exists:

- Aetherra needs one stable cognitive processing layer that connects memory,
  reasoning, agents, Lyrixa, Hub, and improvement signals without giving any
  one subsystem unchecked power.

Authority it owns:

- Intent interpretation.
- Cognitive context construction.
- Reasoning coordination.
- Response payload generation.
- Governed task submission.
- Engine readiness and metrics reporting.

Authority it does not own:

- Approval.
- Security enforcement.
- Memory ownership and persistence policy.
- Runtime scheduling.
- Self-modification.
- Plugin installation.
- Self-Incorporation execution.
- Homeostasis verification.
- Lyrixa's full persona/interface authority.

How it fails:

- Invalid inputs are rejected before dispatch.
- Missing required components block readiness.
- Optional missing components degrade readiness.
- Processing errors return stable error codes and trace IDs.
- Denied privileged actions do not execute.
- Sensitive details are redacted from responses and logs.

How it interacts with other systems:

- Memory supplies recall and persistence.
- Guardian reviews privileged intent.
- Security enforces capability, sandbox, signing, network, and audit policy.
- Agents execute specialized work.
- Kernel owns runtime lifecycle.
- Self-Improvement receives observations.
- Self-Incorporation applies only approved changes.
- Homeostasis verifies outcomes.
- Maintenance records lifecycle results.
- Lyrixa presents Engine output to the user.

## Non-Goals

The Engine foundation does not claim:

- full AGI;
- human consciousness;
- unrestricted autonomy;
- direct self-rewriting;
- direct plugin installation;
- bypass authority over Guardian, Security, Kernel, or Memory;
- final production-grade LLM reasoning.

The Engine is allowed to become more capable only when its authority boundaries
remain intact.

## Post-Completion Hardening

The following work is future hardening, not incomplete Engine authority. These
items improve maintainability, live validation, and provider coverage after the
controlled alpha foundation:

- Split the remaining monolithic Engine coordinator into smaller focused
  modules when doing so reduces risk and improves maintainability.
- Expand provider-specific LLM adapter tests for OpenAI, Anthropic, Ollama,
  Gemini, llama.cpp, and local model manager paths.
- Add longer-running live runtime smoke tests that exercise Hub, Lyrixa,
  Memory, Guardian, Security, and Engine together.
- Promote Engine metrics into the broader observability dashboard once the
  alpha runtime path is stable.
- Remove any legacy compatibility paths when they are proven unused by the
  active runtime.

## Current Milestone Statement

For alpha readiness, the Engine does not need to be a final autonomous mind.
It needs to be a reliable, bounded, observable cognitive coordinator that can
think through a request, use memory safely, submit governed work, degrade
honestly, and preserve the authority boundaries of the larger Aetherra organism.
