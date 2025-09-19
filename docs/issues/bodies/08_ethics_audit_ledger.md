# Ethics & Audit Ledger (append-only)

Labels: phase:1, area:ethics, type:infra
Milestone: Self-Incorporation v1

## Description

Implement an append-only JSONL ledger for ethics/audit decisions.

## Acceptance Criteria

- 100% of quarantine/allow decisions produce a JSONL entry
- Entries link scans, signatures, capability diffs
- Provide a basic query tool (filter by date, action, component)
- Unit tests for writer and basic query
