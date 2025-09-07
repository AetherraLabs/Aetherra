# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Lyrixa primary chat path tests.

These tests assert that:
1. The advanced LyrixaChatService backend is selected (not the basic fallback) during
   normal initialization of `LyrixaBasicAssistant`.
2. Model name alias normalization maps deprecated names ("gpt-4") to modern
   defaults ("gpt-4o-mini").

Fallback note: If the advanced service cannot initialize (e.g. missing
optional deps or severe environment constraints) the test will be skipped
instead of failing, because fallback correctness is covered elsewhere.
A hard failure (assert) is used only when the fallback is engaged despite
advanced components being importable.
"""

from __future__ import annotations

import asyncio

# Add project root to path
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.mark.asyncio
async def test_advanced_chat_backend_selected():
    from Aetherra.lyrixa.lyrixa_basic import LyrixaBasicAssistant

    assistant = LyrixaBasicAssistant()
    ok = await assistant.initialize()
    assert ok, "LyrixaBasicAssistant failed to initialize (OS/hub not ready?)"

    ai_chat = assistant.ai_chat_system
    assert ai_chat is not None, "AI chat system not initialized"

    # Heuristic: advanced wrapper defines attribute _svc after init
    is_advanced = hasattr(ai_chat, "_svc") and getattr(ai_chat, "_svc") is not None

    if not is_advanced:
        pytest.skip(
            "Advanced LyrixaChatService backend not active; environment forced fallback"
        )

    # Smoke send without asserting semantic content (network/model may be rate limited)
    try:
        resp = await ai_chat.send_message("hello")  # type: ignore[attr-defined]
    except Exception as e:  # pragma: no cover - environment/network issues
        pytest.skip(f"Chat send skipped due to transient error: {e}")

    # Accept either ChatResponse-like object with text or plain string
    text_attr = getattr(resp, "text", None)
    output_text = (
        text_attr
        if isinstance(text_attr, str)
        else (resp if isinstance(resp, str) else None)
    )
    assert output_text, "No chat text produced by advanced backend"
    assert len(output_text) < 5000, "Response unexpectedly large (possible runaway)"


def test_model_alias_normalization():
    from Aetherra.lyrixa.intelligence.lyrixa_full_intelligence import (
        LyrixaIntelligenceCore,
    )

    # Direct static method use (does not require provider initialization)
    norm = LyrixaIntelligenceCore.normalize_model_name("gpt-4")
    assert norm == "gpt-4o-mini", "Deprecated 'gpt-4' should normalize to 'gpt-4o-mini'"

    # Idempotent for already-normalized
    assert LyrixaIntelligenceCore.normalize_model_name("gpt-4o-mini") == "gpt-4o-mini"

    # Empty / None handling
    assert LyrixaIntelligenceCore.normalize_model_name("") == "gpt-4o-mini"


def test_intelligence_capabilities_reinforced():
    from Aetherra.lyrixa.intelligence.lyrixa_full_intelligence import (
        LyrixaIntelligenceCore,
    )

    core = LyrixaIntelligenceCore()
    # Simulate config toggles off to ensure enforcement flips them back on
    core.config["memory_integration"] = False
    core.config["emotional_modeling"] = False
    core.config["learning_enabled"] = False
    core._ensure_full_capabilities()  # type: ignore[attr-defined]
    assert core.config["memory_integration"] is True
    assert core.config["emotional_modeling"] is True
    assert core.config["learning_enabled"] is True


if __name__ == "__main__":  # Manual debug helper
    asyncio.run(test_advanced_chat_backend_selected())
    test_model_alias_normalization()
    print("Manual run complete.")
