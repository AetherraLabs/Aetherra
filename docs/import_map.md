# Import Map

Canonical import namespaces for Aetherra to reduce drift and ambiguity.

- Aetherra.* — Primary package namespace (preferred for all internal modules)
- aetherra_core.* — Legacy namespace (avoid in new code; add adapters if needed)
- lyrixa_core.* — Legacy namespace for Lyrixa (avoid in new code)

Guidelines

- Prefer absolute imports using the Aetherra.* namespace.
- Avoid mixed-case duplicates or relative-import backtracking.
- When moving modules, add a thin compatibility shim (re-export) and mark with a TODO to remove once call-sites are migrated.# Import Map

This project standardizes Python import paths to avoid drift and ambiguity.

- Canonical package namespace: `Aetherra.*`
- Avoid legacy or alternate roots such as `aetherra_core.*`, `lyrixa_core.*`, or ad hoc relative imports.
- For internal cores, import as subpackages of `Aetherra.aetherra_core.*`.
- For Lyrixa UI, import under `Aetherra.lyrixa.*`.

Guidelines:

- Prefer absolute imports over relative ones.
- If a module is shared across OS and Lyrixa, place it under `Aetherra/aetherra_core/...` and import with `Aetherra.aetherra_core...`.
- Add simple compatibility shims only if necessary and annotate with a deprecation comment.

CI validation:

- The CI job checks for non-canonical imports and fails with a readable list of offenders.
