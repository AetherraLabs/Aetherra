import json
import zipfile

import Aetherra.plugins.core.plugin_system as plugin_system_module


def _system(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_PRINCIPAL", "plugin-system-test")
    return plugin_system_module.LyrixaPluginSystem()


def _source_plugin(tmp_path, name="installable_plugin", description="Installable plugin"):
    source_dir = tmp_path / "source_plugins" / name
    source_dir.mkdir(parents=True)
    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": description,
        "entry_point": "main.py",
        "permissions": [],
        "capabilities": ["hello"],
    }
    (source_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (source_dir / "main.py").write_text(
        "def execute(command, **kwargs):\n    return {'ok': True}\n",
        encoding="utf-8",
    )
    return source_dir


def _guardian_entries(tmp_path):
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_directory_plugin_install_passes_through_guardian(monkeypatch, tmp_path):
    system = _system(monkeypatch, tmp_path)
    source_dir = _source_plugin(
        tmp_path,
        description="secret='do-not-audit-plugin-description'",
    )

    result = system.install_plugin(str(source_dir))
    ledger_text = (
        tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "plugin.install"
    )

    assert result["success"] is True
    assert (tmp_path / "lyrixa_plugins" / "installable_plugin").exists()
    assert guardian_entry["details"]["intent"]["capabilities"] == [
        "plugin:install",
        "fs:write",
    ]
    assert "plugin_installation" in guardian_entry["details"]["risk"]["factors"]
    assert "do-not-audit-plugin-description" not in ledger_text


def test_directory_plugin_install_denied_before_copy_when_capability_missing(
    monkeypatch, tmp_path
):
    system = _system(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    source_dir = _source_plugin(tmp_path, name="blocked_install")

    result = system.install_plugin(str(source_dir))
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "plugin.install"
    )

    assert result["success"] is False
    assert "Guardian denied" in result["error"]
    assert (tmp_path / "lyrixa_plugins" / "blocked_install").exists() is False
    assert guardian_entry["details"]["decision"]["status"] == "deny"
    assert guardian_entry["details"]["decision"]["reason"] == "missing_capability"


def test_plugin_uninstall_requires_guardian_approval_before_delete(monkeypatch, tmp_path):
    system = _system(monkeypatch, tmp_path)
    source_dir = _source_plugin(tmp_path, name="uninstall_guarded")
    install_result = system.install_plugin(str(source_dir))

    result = system.uninstall_plugin("uninstall_guarded")
    guardian_entry = next(
        entry
        for entry in _guardian_entries(tmp_path)
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "plugin.uninstall"
    )

    assert install_result["success"] is True
    assert result["success"] is False
    assert "Guardian denied" in result["error"]
    assert (tmp_path / "lyrixa_plugins" / "uninstall_guarded").exists()
    assert guardian_entry["details"]["decision"]["status"] == "require_approval"


def test_zip_plugin_install_blocks_path_traversal(monkeypatch, tmp_path):
    system = _system(monkeypatch, tmp_path)
    archive_path = tmp_path / "malicious_plugin.zip"
    escaped = tmp_path / "escaped.py"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../escaped.py", "print('bad')\n")
        archive.writestr(
            "safe/manifest.json",
            json.dumps({"name": "zip_plugin", "version": "1.0.0", "entry_point": "main.py"}),
        )

    result = system.install_plugin(str(archive_path))

    assert result["success"] is False
    assert "escapes extraction directory" in result["error"]
    assert escaped.exists() is False
