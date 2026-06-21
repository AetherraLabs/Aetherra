# The Understanding Rule

Updated: 2026-06-20

The Understanding Rule is a project-level completion gate for Aetherra systems.
It exists because Aetherra is being built with AI assistance, and code volume
alone must never be treated as proof that a system is complete.

## Rule

Before a system is considered complete, the builder must be able to explain,
without looking at the code:

- What it does.
- Why it exists.
- What authority it owns.
- What authority it does not own.
- How it fails.
- How it interacts with other systems.

If that explanation cannot be given clearly, the system is not complete.

No amount of code, tests, documentation length, or generated structure overrides
this rule.

## Completion Meaning

A system may be described as `functional foundation complete` or `functional
complete` only when its behavior and boundaries are understandable at the
architecture level.

The required explanation should cover:

| Question | Required Understanding |
| --- | --- |
| What it does | The system's actual runtime responsibility |
| Why it exists | The architectural reason it is separate from other systems |
| What authority it owns | The decisions or actions the system is allowed to control |
| What authority it does not own | Explicit boundaries and forbidden responsibilities |
| How it fails | Degraded behavior, refusal behavior, rollback, containment, or safe stop |
| How it interacts | Inputs, outputs, dependencies, and governance path with other systems |

## Authority Discipline

The Understanding Rule protects Aetherra from systems that overlap, drift, or
silently gain authority.

For Aetherra's current architecture:

- Guardian decides.
- Security enforces.
- Homeostasis observes and verifies.
- Self-Improvement diagnoses and proposes.
- Self-Incorporation executes approved changes.
- Maintenance coordinates.
- Runtime UI observes.

Any system that appears to own another system's authority must be corrected,
split, renamed, or documented as a deliberate architecture change before it can
be considered complete.

## Review Checklist

Before marking a system complete, answer:

1. Can its purpose be explained in one paragraph?
2. Can its authority boundary be explained in one paragraph?
3. Can its failure behavior be explained without reading implementation code?
4. Can its dependencies and interactions be explained as a flow?
5. Can someone else read the system document and reach the same understanding?

If any answer is no, the system remains incomplete.

## Application

This rule applies to:

- New systems.
- Existing systems being upgraded.
- Systems marked functional foundation complete.
- Systems marked functional complete.
- Major refactors that change authority, failure behavior, or system boundaries.

The rule does not require every implementation detail to be memorized. It
requires architectural understanding of purpose, authority, failure, and
interaction.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
