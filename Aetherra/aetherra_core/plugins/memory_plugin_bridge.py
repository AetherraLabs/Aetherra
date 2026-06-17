# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Memory Plugin Bridge
Routes memory read/write/recall commands from plugin ecosystem.

Provides a stable API for plugins regardless of the underlying engine.
"""

from __future__ import annotations

# Standard library imports
import hashlib
import os
from typing import Any, Dict, List

try:
    # Prefer absolute import within Aetherra package layout
    # Aetherra imports
    from Aetherra.aetherra_core.memory.lyrixa_memory_engine import LyrixaMemoryEngine
except ImportError:
    # Fallback to relative style when package context differs
    # Local imports
    from ..memory.lyrixa_memory_engine import LyrixaMemoryEngine  # type: ignore


_engine = LyrixaMemoryEngine()


def _hash_value(value) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "memory:plugin_bridge" and capability == "memory:write":
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_plugin_forget(key: str):
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "memory:plugin_bridge"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="memory",
            action="memory.plugin_forget",
            target="memory:plugin_bridge",
            purpose="Delete plugin-associated memory when backend supports it",
            capabilities=("memory:write",),
            evidence=("plugin_forget_request",),
            reversible=True,
            rollback_plan="restore plugin-associated memory from backup or export",
            metadata={
                "plugin_key_hash": _hash_value(key),
                "plugin_key_length": len(str(key or "")),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


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
    decision = _guardian_preflight_plugin_forget(key)
    if not decision.allowed:
        return False

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
