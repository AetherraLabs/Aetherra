import json

import pytest

from Aetherra.plugins.core.plugin_generator_plugin import PluginGeneratorPlugin


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)


def _audit_text(root):
    return (root / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _audit_entries(root):
    return [
        json.loads(line)
        for line in _audit_text(root).splitlines()
        if line.strip()
    ]


def test_plugin_generator_save_is_guardian_audited_without_raw_paths(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    generator = PluginGeneratorPlugin()
    plugin_id = generator.generate_plugin(
        "ui_widget",
        "Demo Widget",
        "Sensitive demo plugin description",
    )
    output_dir = tmp_path / "generated-output"

    assert generator.save_plugin_to_disk(plugin_id, str(output_dir)) is True

    assert (output_dir / "demo_widget_plugin" / "widget.py").exists()
    ledger_text = _audit_text(tmp_path)
    assert str(output_dir) not in ledger_text
    assert "Demo Widget" not in ledger_text
    assert "Sensitive demo plugin description" not in ledger_text
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "coding.plugin_generator_save"
    assert entry["details"]["intent"]["metadata"]["template_id"] == "ui_widget"
    assert entry["details"]["intent"]["metadata"]["file_count"] == 3


def test_plugin_generator_save_denial_skips_filesystem_write(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-code-generator",
        strict=True,
    )
    generator = PluginGeneratorPlugin()
    plugin_id = generator.generate_plugin(
        "data_processor",
        "Data Tool",
        "Do not write this plugin",
    )
    output_dir = tmp_path / "generated-output"

    with pytest.raises(PermissionError, match="guardian_denied:missing_capability"):
        generator.save_plugin_to_disk(plugin_id, str(output_dir))

    assert not output_dir.exists()
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "coding.plugin_generator_save"
    assert entry["details"]["decision"]["reason"] == "missing_capability"
