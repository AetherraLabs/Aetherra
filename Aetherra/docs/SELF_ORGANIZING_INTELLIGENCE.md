# Aetherra Self-Organizing Intelligence

Status: Historical reference.

This document previously described an autonomous file-organization prototype.
That prototype depended on package-level cleanup scripts under
`Aetherra/scripts/` and an older import layout that is no longer part of the
active architecture.

The current Aetherra design separates authority:

- Homeostasis observes and verifies system state.
- Self-Improvement diagnoses issues and proposes improvements.
- Guardian reviews and decides whether change is allowed.
- Security enforces capabilities, sandboxing, signing, and audit.
- Self-Incorporation applies only approved changes with rollback.
- Maintenance coordinates the full loop.

The signed `Aetherra/scripts/self_organizer.aether` file remains in place only
until Aether Script verification and runtime discovery paths are migrated
together. It must not be treated as an active autonomous mutation path.

For current repository mapping and cleanup decisions, use:

- `docs/AETHERRA_MASTER_MAP.md`
- `docs/REPOSITORY_STRUCTURE.md`
- `docs/ROOT_SCRIPT_WORKFLOW_TRIAGE.md`
