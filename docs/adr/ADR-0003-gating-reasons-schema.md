# ADR-0003: Gating Reasons Schema

Status: Proposed
Date: 2025-09-08

## Context
Quality gate output previously surfaced only implicit textual logs. UI & autonomy layers require a structured machine-readable summary of why a run failed, passed with warnings, or degraded. Introducing a stable schema early enables tooling and PR integration.

## Decision

Adopt a JSON array of objects each with: `code` (SCREAMING_SNAKE), `severity` (info|warning|error), `message` (human-readable), optional `meta` (dict). Include this in `coverage_gate_report.json` under `gating_reasons` and extend to other gate outputs over time.

## Initial Codes

* COVERAGE_DROP (error)
* FILE_COVERAGE_DROP (warning) – per-file degradation
* TEST_SELECTION (info)
* LICENSE_POLICY (error/warning future)
* SECURITY_FINDINGS (error future)
* ARCH_MISMATCH (warning future)

## Consequences

* Enables UI panels and autonomy policy decisions.
* Increases determinism surface; codes must remain stable or versioned.

## Alternatives Considered

1. Free-form text parsing – brittle, internationalization risk.
2. Single aggregate status code – insufficient granularity.

## Versioning

Schema v1 implicit (no `schema_version` field). Add `schema_version` once first incompatible change arises.

## Review

Owner: Coding Lead
Reviewers: DevEx, Security
Decision Date: (pending)
