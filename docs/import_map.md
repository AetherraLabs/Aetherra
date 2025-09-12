# Import Map & Enforcement (P2 #13)

Canonical import namespace: `Aetherra.*`

Legacy namespaces (blocked in CI):

| Forbidden                              | Rationale                                    | Replacement                |
| -------------------------------------- | -------------------------------------------- | -------------------------- |
| `aetherra_core.*`                      | Pre-refactor root causes packaging shadowing | `Aetherra.aetherra_core.*` |
| `lyrixa_core.*`                        | Legacy Lyrixa split namespace                | `Aetherra.lyrixa.*`        |
| `aetherra_core` / `lyrixa_core` (bare) | Same as above                                | `Aetherra.*`               |

Relative import policy:

| Pattern                     | Allowed        | Notes                                |
| --------------------------- | -------------- | ------------------------------------ |
| `from . import X`           | Yes            | Intra-package clarity okay           |
| `from .sub import Y`        | Yes            | Shallow relative is fine             |
| `from ..foo import Z`       | Warn/Fail (CI) | Depth >1 discouraged; use absolute   |
| `from ...deep.mod import Q` | Fail           | Hard to maintain; triggers validator |

Why enforce:
- Avoid module shadowing & sys.path order surprises.
- Keep refactors mechanical (search/replace under single root).
- Reduce accidental cross-layer imports through relative backtracking.

Tooling layers:
1. Ruff banned-modules (quick feedback) — rejects direct use of legacy roots.
2. `tools/validate_import_map.py` (CI hard gate) — adds deep relative depth check (>1) outside `tests/`.
3. Future (optional): block star-imports for internal modules (placeholder hook in validator).

Local run:
```
python tools/validate_import_map.py
```
Exit code 1 → fix flagged lines (convert to `Aetherra.*`).

Migration pattern:
```
# BEFORE
from aetherra_core.memory.engine import MemoryEngine

# AFTER
from Aetherra.aetherra_core.memory.engine import MemoryEngine
```

Test fixtures may still use deeper relatives for brevity; production code should not.

Roadmap:
- Add optional whitelist file to suppress legacy adapter modules until removed.
- Integrate star-import detection (FUTURE_FLAG: STAR_IMPORT_BLOCK=1).
- Auto-fix script to rewrite obvious legacy paths (planned `tools/auto_rewrite_imports.py`).

CI integration: enforced inside main CI (`syntax-validation` job runs validator). No separate workflow file required now; this doc is authoritative.

Status: Active — failing imports block merges.

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

