# Aetherra imports
from Aetherra.consciousness.self_model import who_am_i


def test_who_am_i_contains_identity():
    ident = who_am_i()
    assert "Lyrixa" in ident
    assert "Aetherra" in ident
    assert "Unified Consciousness & Operating Substrate" in ident


def test_explicit_self_model_path_is_preserved(tmp_path):
    model = tmp_path / "custom.json"
    model.write_text(
        '{"name":"Synthetic","identity":{"role":"Test collaborator"}}', encoding="utf-8"
    )
    assert who_am_i(model) == "Synthetic v0 — Test collaborator"


def test_explicit_missing_self_model_keeps_fallback(tmp_path):
    assert who_am_i(tmp_path / "missing.json") == "Lyrixa v0 — AI collaborator"
