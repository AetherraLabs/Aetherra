# Hub policy alignment + tokens

Labels: phase:2, area:apis, type:feature
Milestone: Self-Incorporation v1

## Description

Ensure self-incorporation APIs align with Hub auth tokens/claims gating and propagate
policy in responses/streams.

## Acceptance Criteria

- Self-inc endpoints honor Hub’s token/claims gating
- Policy surfaced in headers/streams per chat contracts
- Tests for token gating and header propagation
- Docs updates for env flags and headers
