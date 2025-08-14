"""
Memory Plugin Bridge
Routes memory read/write/recall commands from plugin ecosystem.

Provides a stable API for plugins regardless of the underlying engine.
"""

from __future__ import annotations

from typing import Any, Dict, List

try:
    # Prefer absolute import within Aetherra package layout
    from Aetherra.aetherra_core.memory.lyrixa_memory_engine import (
        LyrixaMemoryEngine,
    )
except ImportError:
    # Fallback to relative style when package context differs
    from ..memory.lyrixa_memory_engine import LyrixaMemoryEngine  # type: ignore


_engine = LyrixaMemoryEngine()


def plugin_store(key: str, content: Any) -> Dict[str, Any] | None:
    """Store memory content with plugin metadata."""
    try:
        return _engine.store({"content": content, "plugin": key})
    except TypeError:
        # Legacy signature
        return _engine.store(content)


def plugin_recall(query: str) -> List[Dict[str, Any]] | Dict[str, Any] | None:
    """Recall memories by query using engine defaults."""
    try:
        return _engine.retrieve(query)
    except TypeError:
        return _engine.retrieve(query, {})


def plugin_forget(key: str) -> bool:
    """Best-effort memory deletion for plugin-associated content.

    Not all engines support deletion; perform a no-op if unavailable.
    """
    eng = getattr(_engine, "engine", _engine)
    # Try a few likely method names
    for attr in ("delete", "remove", "forget"):
        fn = getattr(eng, attr, None)
        if callable(fn):
            try:
                fn(key)
                return True
            except Exception:
                continue
    # No deletion API available
    return False
