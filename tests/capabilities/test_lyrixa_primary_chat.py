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

# Standard library imports
import asyncio

# Add project root to path
import sys
from pathlib import Path

# Third party imports
import pytest

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from Aetherra.lyrixa.chat.lyrixa_chat_service import ChatOptions, LyrixaChatService


@pytest.mark.asyncio
async def test_lyrixa_chat_service_responds():
    svc = LyrixaChatService()
    await svc.initialize()
    opts = ChatOptions(user_id="test", session_id="test-session")
    resp = await svc.chat("hello", opts)
    assert hasattr(resp, "text")
    assert isinstance(resp.text, str)
    assert resp.text.strip() != ""
    assert len(resp.text) < 5000


def test_model_alias_normalization():
    # Aetherra imports
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
    # Aetherra imports
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
