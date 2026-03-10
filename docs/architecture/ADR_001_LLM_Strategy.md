# ADR 001: LLM Provider Strategy

- Status: Accepted
- Date: 2026-03-10
- Owners: Phase 1 Team
- Related: `PRODUCTION_ROADMAP.md` section 1.1.3

## Context

Aetherra currently has mixed runtime paths with fallback behavior in core engine modules.
For production, LLM invocation must be deterministic, observable, and policy-controlled.

The roadmap decision point is whether to use a single-provider hard coupling or a provider abstraction.

## Decision

Adopt a multi-provider abstraction with local-first policy and strict production gating.

Decision details:

- Keep a single internal provider interface for reasoning/chat/completion operations.
- Support multiple adapters behind that interface (local and remote).
- Default to local provider when available.
- In production profile, disallow silent fallback to mock providers.
- Require explicit capability registration for any provider used by engine code paths.

## Rationale

- Preserves operational resilience when one provider is unavailable.
- Prevents lock-in while maintaining one stable internal contract.
- Aligns with existing config posture and environment-driven policy gates.
- Supports reproducible tests via deterministic provider selection.

## Consequences

Positive:

- Cleaner engine code with fewer ad hoc import-fallback branches.
- Better observability for provider health and response latency.
- Easier compliance and security review through a centralized provider policy layer.

Negative:

- Requires adapter maintenance and contract tests.
- Adds migration work to remove direct provider calls in legacy paths.

## Implementation Notes (Phase 1-2)

1. Define a provider contract module (request/response schema, errors, timeouts).
2. Add a provider registry with explicit capability metadata.
3. Enforce profile-based policy: prod rejects unregistered or mock providers.
4. Refactor engine runtime to consume the contract only.
5. Add integration tests for local-first, failover, and strict-production rejection behavior.

## Validation Criteria

- No core engine path uses implicit provider imports directly.
- Production profile fails fast when provider contract is not satisfied.
- Metrics expose provider selected, fallback attempts, and rejection reasons.
- Capability tests pass for both local-first and configured remote provider modes.
