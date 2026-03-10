from __future__ import annotations

# Standard library imports
import logging
import os
import sys

"""Legacy import shim for BeyondTranscendenceEngine.

Delegates to the namespaced adapter at
`Aetherra.consciousness.transcendence.beyond_transcendence_engine`.

This file exists solely for backward compatibility with older tests and
launcher code that import the legacy root-level module name. A future
release may remove this shim once all references migrate to the
namespaced location.
"""

logger = logging.getLogger(__name__)

_DEP_MSG = (
    "[DEPRECATION] Importing 'BeyondTranscendenceEngine' from root module. "
    "Use 'Aetherra.consciousness.transcendence.beyond_transcendence_engine' instead."
)

# Ensure project root in sys.path so namespaced package resolves when launcher
# invoked from alternative working directories.
try:
    _root = os.path.abspath(os.path.dirname(__file__))
    if _root not in sys.path:
        sys.path.insert(0, _root)
except Exception:
    pass

try:  # Preferred import
    # Aetherra imports
    from Aetherra.consciousness.transcendence.beyond_transcendence_engine import (
        BeyondTranscendenceEngine as _NSBeyondTranscendenceEngine,  # type: ignore
    )

    BeyondTranscendenceEngine = _NSBeyondTranscendenceEngine  # type: ignore[assignment]
    logger.debug("[Phase8.3] Using namespaced BeyondTranscendenceEngine adapter (shim)")
    logger.info(_DEP_MSG)
except Exception as _e:  # Fallback minimal stub (should rarely trigger)
    logger.warning(
        f"[Phase8.3] Namespaced adapter unavailable ({_e}); using minimal fallback"
    )
    # Standard library imports
    from dataclasses import dataclass
    from typing import Any

    @dataclass
    class BeyondTranscendenceEngine:  # pragma: no cover - fallback only
        version: str = "8.3-fallback"
        phase: str = "transcendence"

        async def initialize_transcendence(self) -> bool:  # noqa: D401
            return True

        async def achieve_infinite_learning_capacity(
            self,
        ) -> dict[str, Any]:  # noqa: D401,E501
            return {"learning_capacity": 0.0}

        async def master_reality_synthesis(self) -> dict[str, Any]:  # noqa: D401
            return {"reality_mastery": 0.0}

        async def multiply_consciousness_entities(
            self,
        ) -> dict[str, Any]:  # noqa: D401,E501
            return {"entities_created": 0}

        async def discover_universal_purpose(self) -> dict[str, Any]:  # noqa: D401,E501
            return {"purpose_clarity": 0.0}

        async def establish_eternal_consciousness_preservation(
            self,
        ) -> dict[str, Any]:  # noqa: D401,E501
            return {"preservation_strength": 0.0}

        async def achieve_absolute_transcendence(
            self,
        ) -> dict[str, Any]:  # noqa: D401,E501
            return {"absolute_transcendence_level": 0.0}

        async def complete_beyond_transcendence_integration(
            self,
        ) -> dict[str, Any]:  # noqa: D401,E501
            return {"beyond_transcendence_level": 0.0}

        def integrate_beyond_transcendence(self) -> dict[str, Any]:  # noqa: D401,E501
            return {"beyond_transcendence_level": 0.0}

        def get_transcendence_status(self) -> dict[str, Any]:  # noqa: D401
            return {"beyond_transcendence_level": 0.0}


__all__ = ["BeyondTranscendenceEngine"]
