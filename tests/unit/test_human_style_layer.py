# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio
import importlib


def test_human_style_default_enabled(tmp_path, monkeypatch):
    # Ensure defaults
    monkeypatch.delenv("AETHERRA_STYLE_ENABLED", raising=False)
    monkeypatch.setenv("AETHERRA_STYLE_SEED", "7")
    hs_mod = importlib.import_module("Aetherra.aetherra_core.conversation.human_style")
    HumanStyle = hs_mod.HumanStyle
    styler = HumanStyle()
    out, markers = styler.enhance(
        user_message="I'm a bit confused about setup",
        base_text="Let's walk through this.",
        evidence_count=0,
        bucket_index=1,
    )
    assert isinstance(out, str)
    assert hasattr(markers, "used_contractions")


def test_human_style_env_toggles(monkeypatch):
    monkeypatch.setenv("AETHERRA_STYLE_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_STYLE_TONE", "concise")
    monkeypatch.setenv("AETHERRA_STYLE_ASK_QUESTION", "1")
    monkeypatch.setenv("AETHERRA_STYLE_EMOJI", "0")
    monkeypatch.setenv("AETHERRA_STYLE_SEED", "9")

    hs_mod = importlib.import_module("Aetherra.aetherra_core.conversation.human_style")
    HumanStyle = hs_mod.HumanStyle
    styler = HumanStyle()
    out, markers = styler.enhance(
        user_message="Hello",
        base_text="Thanks for the details.",
        evidence_count=3,
        bucket_index=2,
    )
    assert isinstance(out, str)
    # May or may not ask a question depending on stable_choice; just ensure no crash
    assert hasattr(markers, "asked_question")


def test_engine_integration_exports(monkeypatch):
    # Simulate minimal engine usage: style metrics should be present in session_metrics
    # Aetherra imports
    from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine

    monkeypatch.setenv("AETHERRA_STYLE_ENABLED", "1")
    eng = AetherraEngine()

    async def _run():
        await eng.initialize()
        await eng.process_message("hello there")
        st = await eng.get_system_status()
        return st

    st = asyncio.run(_run())
    sm = st.get("session_metrics", {}) if isinstance(st, dict) else {}
    # Style counters exist
    assert "style_contractions" in sm
    assert "style_questions" in sm
    assert "style_empathy" in sm
