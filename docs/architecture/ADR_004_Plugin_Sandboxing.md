# ADR 004: Plugin Sandboxing Model

- Status: Accepted
- Date: 2026-03-10
- Owners: Phase 1 Team

## Context

Plugins are a core extensibility surface and a primary risk vector for production stability and security.

## Decision

Use process-isolated plugin execution for untrusted plugins, with signed in-process exceptions for trusted core plugins.

## Rationale

- Process isolation constrains blast radius.
- Signed trusted plugins can keep lower overhead for critical paths.
- Supports phased migration from legacy in-process assumptions.

## Consequences

Positive:

- Stronger containment and failure isolation.

Negative:

- IPC overhead for isolated plugins.

## Implementation Notes

1. Classify plugins by trust tier and signature status.
2. Default unknown plugins to isolated mode.
3. Add kill/restart and timeout controls at plugin runner boundary.
