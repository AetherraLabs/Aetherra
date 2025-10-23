# STORM Contracts (Frozen)

Status: Frozen for initial integration (v1)

## Types

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Literal

@dataclass
class STORMMetadata:
    cell_id: str
    transport_cost: float           # W_p(μ_q, μ_cell)
    sheaf_inconsistency: float      # ||δs||^2 local
    persistence_bonus: float
    freshness: float
    branch_id: Optional[str] = None

@dataclass
class MemoryRecallResult:
    items: List[Any]                # Memory | MemoryFragment | ReplayEpisode
    scores: List[float]
    source: Literal["core","conceptual","episodic","hybrid","qfac","storm","storm_hybrid"]
    metadata: Dict[str, Any]        # includes STORM fields under metadata["storm_meta"]
```

- `source` must be "storm" or "storm_hybrid" for STORM paths.
- Evidence tags in Chat map as:
  - `ot:<float>` ← `transport_cost`
  - `coh:<float>` ← `coh = 1 / (1 + sheaf_inconsistency)`
  - `pers:<float>` ← `persistence_bonus`

## Determinism requirements

- Test profile must produce stable ordering when scores tie. Implement a tie‑breaker:
  - `score_tiebreak = blake2s(id).hexdigest()` (or equivalent stable hash), used only on equal scores.
- Seeds locked; ANN ordering fixed; GPU backends disabled in `AETHERRA_PROFILE=test`.

## Backward compatibility

- Legacy `list[dict]` adapters remain supported. STORM metadata is placed under `dict["meta"]`.
- Downstreams must not assume availability of STORM fields unless `source` is `storm|storm_hybrid`.
