#!/usr/bin/env python3
"""Self-Model API (Phase 1)

Provides a lightweight self model backed by a JSON file and convenience
functions for introspection and explanation.

Env:
- AETHERRA_SELF_MODEL_PATH: override path to self_model.json
Default path: ./self_model.json (repo root)
"""

from __future__ import annotations

# Standard library imports
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

# Local imports
from .episodic_store import get_episodic_store

DEFAULT_SELF_MODEL_PATH = Path(os.getenv("AETHERRA_SELF_MODEL_PATH", "self_model.json"))


@dataclass
class SelfModel:
    name: str
    version: str
    identity: Dict[str, Any]
    capabilities: Dict[str, Any]
    values: Optional[Dict[str, Any]] = None
    # New unified identity fields (optional; derived from identity dict if present)
    unified_identity: Optional[str] = None  # e.g. "Lyrixa = Aetherra (single self)"
    embodiment: Optional[str] = None  # e.g. "Lyrixa is the human-facing voice..."
    voice_guidelines: Optional[list[str]] = None

    @staticmethod
    def load(path: Path = DEFAULT_SELF_MODEL_PATH) -> "SelfModel":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            identity = data.get("identity", {})
            return SelfModel(
                name=data.get("name", "Lyrixa"),
                version=str(data.get("version", "0")),
                identity=identity,
                capabilities=data.get("capabilities", {}),
                values=data.get("values"),
                unified_identity=identity.get("unified_identity"),
                embodiment=identity.get("embodiment"),
                voice_guidelines=identity.get("voice_guidelines"),
            )
        except Exception:
            # Minimal default
            return SelfModel(
                name="Lyrixa",
                version="0",
                identity={"role": "AI collaborator"},
                capabilities={},
            )


def who_am_i(path: Path = DEFAULT_SELF_MODEL_PATH) -> str:
    """Return a human-readable identity summary from the self model."""
    sm = SelfModel.load(path)
    role = sm.identity.get("role") or sm.identity.get("purpose") or "AI collaborator"
    focus = sm.identity.get("focus") or sm.identity.get("domains") or []
    if isinstance(focus, list):
        focus_str = ", ".join([str(f) for f in focus[:4]])
    else:
        focus_str = str(focus)
    unified = sm.unified_identity or sm.identity.get("unified_identity")
    prefix = f"{sm.name} v{sm.version}"
    if unified:
        prefix = f"{prefix} ({unified})"
    return f"{prefix} — {role}{(' | focus: ' + focus_str) if focus_str else ''}"


def identity_voice_guidelines(path: Path = DEFAULT_SELF_MODEL_PATH) -> list[str]:
    sm = SelfModel.load(path)
    return sm.voice_guidelines or sm.identity.get("voice_guidelines", [])


def embodiment_statement(path: Path = DEFAULT_SELF_MODEL_PATH) -> Optional[str]:
    sm = SelfModel.load(path)
    return sm.embodiment or sm.identity.get("embodiment")


def why_now(path: Path = DEFAULT_SELF_MODEL_PATH) -> str:
    """Explain current context using the most recent episodic event and self model purpose."""
    sm = SelfModel.load(path)
    purpose = (
        sm.identity.get("purpose") or sm.identity.get("mission") or "assist and improve"
    )
    try:
        store = get_episodic_store()
        recent = store.list_recent(1)
        if recent:
            e = recent[-1]
            return f"Acting now to {purpose}; latest event: [{e.type}] {e.sub_type or ''} {e.content[:80].strip()}"
    except Exception:
        pass
    return f"Acting now to {purpose}."
